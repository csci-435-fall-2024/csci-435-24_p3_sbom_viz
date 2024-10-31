"""
URL configuration for sbom_viz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from sbom_viz import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("diagram/", views.go_to_page_diagram, name = "diagram"),
    path("tree/", views.get_tree, name = "get-tree"),
    path("id-data-map/", views.get_data_map, name = "get-map"),
    path("", views.go_to_page_home, name="home"),
    path("uploaded/", views.is_sbom_uploaded, name="uploaded")

  # Previously used to get tree via HttpResponse to 127... /data.json
  # re_path(r"[a-zA-Z]*.json$", views.json, name = "json") # allow D3 to query for data as a JSON file
]
