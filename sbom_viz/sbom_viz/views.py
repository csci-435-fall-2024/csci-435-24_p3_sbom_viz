from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    if request.method == "POST" and len(request.FILES) == 1:
        return render(request, 'sbom_viz/display_file.html')
    else:
        return render(request, 'sbom_viz/index.html')
