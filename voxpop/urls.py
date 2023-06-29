from django.urls import path
from ninja import NinjaAPI

from . import views
from voxpop.api import router as voxpop_router

api = NinjaAPI(urls_namespace="voxpop:api")

api.add_router("/voxpops/", voxpop_router)

app_name = "voxpop"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("voxpops/<uuid:voxpop_id>/questions/new/", views.new_question, name="new_question",),
    path("stream/<uuid:voxpop_id>/questions/", views.stream_questions_view, name="stream_questions",),
    path("api/", api.urls),
    path("admin/", views.admin_index, name="admin"),
    path("admin/voxpops/new", views.new_voxpop, name="new_voxpop"),
    path("admin/voxpops/<uuid:voxpop_id>/", views.admin_voxpop, name="admin_voxpop"),
    path("admin/voxpops/<uuid:voxpop_id>/<uuid:question_id>", views.admin_question_set_state, name="admin_question_set_state"),
]
