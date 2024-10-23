from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from lib4sbom.parser import SBOMParser
from sbom_viz.scripts import build_tree
import json

mock_tree = {
    "name" : "SBOM Root", # artificial root node
    "type" : "ROOT", # special type for root node, not official SBOM
    "ghost" : False,
    "relationships" : 
    {
        "RELATED_TO" : ["SPDXRef-DOCUMENT", "SPDXRef-CommonsLangSrc"] # RELATED_TO is a generic relationship not official SBOM
    },
    "children" : [
        {
            "name" : "SPDXRef-DOCUMENT",
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

sbom_parser = SBOMParser()
data_map = {"SPDXRef-DOCUMENT": {"name": "SPDXRef-DOCUMENT"}}
sbom_tree = {}

def home(request):
    if request.method == "POST" and len(request.FILES) == 1:
        file = request.FILES["file-select-input"]
        print(type(file))
        sbom_parser.parse_file(file.temporary_file_path())
        file_contents = ""
        for line in file:
            file_contents += line.decode()+'\n'
        return render(request, 'sbom_viz/display_file.html', {"file_contents": file_contents})
    else:
        return render(request, 'sbom_viz/index.html')

# This method is called after getting the data map  
def get_tree(request):
    should_return_mock_tree = False
    if request.method == "GET":
        if (should_return_mock_tree):
            return JsonResponse(mock_tree)
        else:
            return JsonResponse(data=build_tree.get_relationship_tree(sbom_parser, data_map), json_dumps_params={"indent": 4}) 


    
# This method is called when requesting the URL: localhost:8000/id-data-map
# This url should only be called after the user submits the file upload form. Otherwise the returned data is nearly empty    
def get_data_map(request):
    if request.method == "GET":
        for i in sbom_parser.get_files():
            data_map[i["id"]] = i
        for i in sbom_parser.get_packages():
            data_map[i["id"]] = i
        return JsonResponse(data=data_map, json_dumps_params={"indent": 4})
