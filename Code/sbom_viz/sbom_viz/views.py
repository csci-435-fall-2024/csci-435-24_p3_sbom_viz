from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from sbom_viz.scripts.tree_builder import TreeBuilder
from sbom_viz.scripts.relationship_map_builder import RelationshipMapBuilder
from sbom_viz.config.feature_flags import FLAGS
from sbom_viz.scripts import parse_files, tree_builder, security
from typing import Optional
import json
import os

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
tree_builder: Optional[TreeBuilder] = None
uploaded = False    # represents whether an SBOM has been uploaded yet
filename = ""

# DEPRECATED -- will not work with page transitions from navigation bar links. See go_to_page_diagram for its replacement.
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
        pass
        #return render(request, 'sbom_viz/index.html')    
'''
Deprecated - previously, fileInputPage.js would submit an HttpResponse to 127... /data.json to retrieve tree.
Now, it queries 127... /tree/ and receives a JsonResponse.

# Used by D3 to gather data for tree
def json(request):
    return render(request, 'sbom_viz/data.json')
'''
    
'''
Builds and returns the Tree
'''
def get_tree(request):
    if request.method == "GET":
        global sbom_parser
        global tree_builder

        if FLAGS["use_mock_tree"]:
            return JsonResponse(mock_tree)

        tree_builder = TreeBuilder(sbom_parser.get_relationships(), sbom_parser.get_components())
    
        tree_builder.build_tree()

        return JsonResponse(data=tree_builder.get_tree_as_dict(), json_dumps_params={"indent": 4})

'''
Builds and returns the Relationship Map
''' 
def get_relationship_map(request):
    if request.method == "GET":
        global tree_builder
        
        relationship_map_builder = RelationshipMapBuilder(tree_builder.get_root_node())

        relationship_map_builder.build_map()

        return JsonResponse(data=relationship_map_builder.get_map_as_dict(), json_dumps_params={"indent": 4})
    
# This method is called when requesting the URL: localhost:8000/id-data-map
# This url should only be called after the user submits the file upload form. Otherwise the returned data is nearly empty    
def get_data_map(request):
    global data_map
    global sbom_parser
    # if request.method == "GET":
    #     return JsonResponse(data=data_map, json_dumps_params={"indent": 4})
    if request.method == "GET":
        data_map = {"SPDXRef-DOCUMENT": {"name": "SPDXRef-DOCUMENT"}}
        for i in sbom_parser.get_files():
            data_map[i["id"]] = i
        for i in sbom_parser.get_packages():
            data_map[i["id"]] = i
        return JsonResponse(data=data_map, json_dumps_params={"indent": 4})
    
# Indicates if an SBOM has been uploaded
def is_sbom_uploaded(request):
    global uploaded
    return JsonResponse(data={"uploaded": uploaded})

# Endpoint that takes a user back to the home page when the link on the navigation bar is clicked
def go_to_page_home(request):
    return render(request, 'sbom_viz/index.html')

# Endpoint that takes a user to the tree diagram page when the link on the navigation bar is clicked
def go_to_page_diagram(request):
    global uploaded
    global filename
    # If no file has been uploaded yet, and the user tries to force the app to go to the tree diagram page without uploading a file (via the browser search bar), display a 403 Forbidden error.
    if len(request.FILES) == 0 and not uploaded:
        raise PermissionDenied()
    # If the user uploads an SBOM, overwrite the existing SBOM before going to the diagram page.
    if request.method == "POST" and len(request.FILES) == 1:
        uploaded = True
        file = request.FILES["file-select-input"]
        filename = file.name
        print(type(file))
        sbom_parser.parse_file(file.temporary_file_path())
        file_contents = ""
        for line in file:
            file_contents += line.decode()+'\n'
    # If the user does not upload an SBOM on the home page, but they have previously uploaded an SBOM, go straight to the diagram page and display the old SBOM.
    return render(request, 'sbom_viz/display_file.html')

# Endpoint that takes a user to the licenses page when the link on the navigation bar is clicked
def go_to_page_licenses(request):
    return render(request, 'sbom_viz/licenses.html')

# Endpoint that takes a user to the vulnerabilities page when the link on the navigation bar is clicked
def go_to_page_vulnerabilities(request):
    return render(request, 'sbom_viz/vulnerabilities.html')

# Endpoint that takes a user to the PDF Preview page when the link on the navigation bar is clicked
def go_to_page_pdf_preview(request):
    return render(request, 'sbom_viz/pdf_preview.html')

def get_filename(request):
    global filename
    return JsonResponse(data={"filename":filename})

# Endpoint that returns the security information needed for the vulnerabilites page 
def get_sec_info(request):
    global sbom_parser
    if uploaded:
        sec_output=security.get_security_output(sbom_parser)
        if request.method == "GET":
            return JsonResponse(data=sec_output, json_dumps_params={"indent": 4})
            
def get_license(request):
    global sbom_parser
    return JsonResponse(data=sbom_parser.get_license_information(), json_dumps_params={"indent": 4})
