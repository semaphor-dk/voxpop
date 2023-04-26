from django.urls import path
from ninja import NinjaAPI

from . import views
from voxpop.api import router as voxpop_router

api = NinjaAPI()

api.add_router("/voxpops/", voxpop_router)

app_name = "voxpop"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("new/", views.new_question, name="new_question"),
    path("api/", api.urls),
]
