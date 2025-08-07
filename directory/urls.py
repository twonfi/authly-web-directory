from django.urls import path

from .views import *

app_name = "directory"

urlpatterns = [
    path("sites/<str:domain>/", site_page, name="site_page"),
    path("manage/", manage_website, name="manage_site"),
    path("", site_list, name="site_list")
]
