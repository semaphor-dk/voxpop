from django.urls import include
from django.urls import path

urlpatterns = [
    path("voxpop/", include("voxpop.urls")),
]
