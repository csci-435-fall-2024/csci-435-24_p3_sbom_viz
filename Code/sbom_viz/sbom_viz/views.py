from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from sbom_viz.scripts.tree_builder import TreeBuilder
from sbom_viz.config.feature_flags import FLAGS
from sbom_viz.scripts import parse_files, tree_builder
import json

mock_tree = {
    "sbomId" : "SBOM Root", # artificial root node
    "nodeId" : 0,
    "type" : "ROOT", # special type for root node, not official SBOM
    "ghost" : False,
    "relationships" : 
    {
        "RELATED_TO" : ["SPDXRef-DOCUMENT", "SPDXRef-CommonsLangSrc"] # RELATED_TO is a generic relationship not official SBOM
    },
    "children" : [
        {
            "name" : "SPDXRef-DOCUMENT",
            "id" : 1,
            "type" : "DOCUMENT",
            "ghost" : False,
            "relationships" :
            {
                "CONTAINS" : ["SPDXRef-Package"],
                "COPY_OF" : ["DocumentRef-spdx-tool-1.2:SPDXRef-ToolsElement"],
                "DESCRIBES" : ["SPDXRef-File", "SPDXRef-Package"]
            },
            "children" : [
                {
                    "name" : "SPDXRef-Package",
                    "type" : "PACKAGE",
                    "ghost" : False,
                    "relationships" : 
                    {
                        "CONTAINS" : ["SPDXRef-JenaLib"],
                        "DYNAMIC_LINK" : ["SPDXRef-Saxon"]
                    },
                    "children" : [
                        {
                            "name" : "SPDXRef-JenaLib",
                            "type" : "FILE",
                            "ghost" : False,
                            "relationships" :
                            {
                                "CONTAINS" : ["SPDXRef-Package"]
                            },
                            "children" : [
                                {
                                    "name" : "SPDXRef-Package",
                                    "type" : "PACKAGE",
                                    "ghost" : True,  # for now, ghost nodes have no relationships or children, we can add in relationships if we think it's needed
                                    "relationships" : {},
                                    "children" : []
                                }
                            ]
                        },
                        {
                            "name" : "SPDXRef-Saxon",
                            "type" : "PACKAGE",
                            "ghost" : False,
                            "relationships" : {},
                            "children" : []
                        }
                    ]
                },
                {
                    "name" : "DocumentRef-spdx-tool-1.2:SPDXRef-ToolsElement",
                    "type" : "COMPONENT", # generic type (for when the sbom doesn't specify a type), not official SBOM 
                    "ghost" : False,
                    "relationships" : {},
                    "children" : []
                },
                {
                    "name" : "SPDXRef-File",
                    "type" : "FILE",
                    "ghost" : False,
                    "relationships" :
                    {
                        "GENERATED_FROM" : ["SPDXRef-fromDoap-0"]
                    },
                    "children" : [
                        {
                            "name" : "SPDXRef-fromDoap-0",
                            "type" : "FILE",
                            "ghost" : False,
                            "relationships" : {},
                            "children" : []
                        }
                    ]
                }
            ]
        },
        {
            "name" : "SPDXRef-CommonsLangSrc",
            "type" : "FILE",
            "ghost" : False,
            "relationships" : 
            {
                "GENERATED_FROM" : ["NOASSERTION"] # NOASSERTION is a special case
            },
            "children" : [
                {
                    "name" : "NOASSERTION",
                    "type" : "NOASSERTION",
                    "ghost" : True, # setting all NOASSERTION as ghost nodes since they are not real components
                    "relationships" : {},
                    "children" : []
                }
            ]
        }
    ]
}

sbom_parser = parse_files.SPDXParser()
data_map = {}
sbom_tree = {}

def home(request):
    global sbom_parser
    global data_map
    if request.method == "POST" and len(request.FILES) == 1:
        file = request.FILES["file-select-input"]
        with open(file.temporary_file_path(), 'r') as f:
            data = f.read()
        is_json = False
        try:
            json.loads(data)
            is_json = True
        except ValueError:
            pass
        if ("SPDXID" in data and is_json):
            sbom_parser = parse_files.SPDXParser()
            data_map = sbom_parser.get_id_data_map()
            sbom_parser.parse_file(file.temporary_file_path())
            file_contents = ""
            for line in file:
                file_contents += line.decode()+'\n'
            return render(request, 'sbom_viz/display_file.html', {"file_contents": file_contents})
        else:
            return render(request, 'sbom_viz/index.html') 
    else:
        return render(request, 'sbom_viz/index.html')    
'''
Deprecated - previously, fileInputPage.js would submit an HttpResponse to 127... /data.json to retrieve tree.
Now, it queries 127... /tree/ and receives a JsonResponse.

# Used by D3 to gather data for tree
def json(request):
    return render(request, 'sbom_viz/data.json')
'''
    
def get_tree(request):
    if request.method == "GET":
        global sbom_parser

        if FLAGS["use_mock_tree"]:
            return JsonResponse(mock_tree)

        tree_builder = TreeBuilder(sbom_parser.get_relationships(), sbom_parser.get_components())
    
        tree_builder.build_tree()

        return JsonResponse(data=tree_builder.get_tree_as_dict(), json_dumps_params={"indent": 4})
    
# This method is called when requesting the URL: localhost:8000/id-data-map
# This url should only be called after the user submits the file upload form. Otherwise the returned data is nearly empty    
def get_data_map(request):
    global data_map
    global sbom_parser
    if request.method == "GET":
        return JsonResponse(data=data_map, json_dumps_params={"indent": 4})
