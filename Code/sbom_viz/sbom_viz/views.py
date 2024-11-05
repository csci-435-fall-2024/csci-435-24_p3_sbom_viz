from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from lib4sbom.parser import SBOMParser
from sbom_viz.scripts import build_tree, parse_files
import json

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
        return JsonResponse(data=build_tree.get_relationship_tree(sbom_parser, data_map), json_dumps_params={"indent": 4}) 


    
# This method is called when requesting the URL: localhost:8000/id-data-map
# This url should only be called after the user submits the file upload form. Otherwise the returned data is nearly empty    
def get_data_map(request):
    global data_map
    global sbom_parser
    if request.method == "GET":
        return JsonResponse(data=data_map, json_dumps_params={"indent": 4})
