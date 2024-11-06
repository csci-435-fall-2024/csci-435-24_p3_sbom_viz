from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from scripts.tree_builder import TreeBuilder
from config.feature_flags import FLAGS

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

def home(request):
    if request.method == "POST" and len(request.FILES) == 1:
        file = request.FILES["file-select-input"]
        file_contents = ""
        for line in file:
            file_contents += line.decode()+'\n'
        return render(request, 'sbom_viz/display_file.html', {"file_contents": file_contents})
    else:
        return render(request, 'sbom_viz/index.html')
    
def get_tree(request):
    if request.method == "GET":
        if FLAGS["use_mock_tree"]:
            return JsonResponse(mock_tree)

        tree_builder = TreeBuilder(sbom_relationships, sbom_components)
    
        tree_builder.build_tree()

        return JsonResponse(tree_builder.get_tree_as_dict())

