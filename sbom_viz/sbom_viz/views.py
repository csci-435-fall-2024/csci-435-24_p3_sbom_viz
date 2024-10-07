from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    if request.method == "POST":
        return HttpResponse("Form posted")
    else:
        return render(request, 'sbom_viz/index.html')
