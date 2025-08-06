from django.urls import path

from .views import *

app_name = "authly"

urlpatterns = [
    path("login/", login, name="login"),
    path("verify/", verify, name="verify"),
    path("logout/", logout, name="logout"),
]
