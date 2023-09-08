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
    path("voxpops/<uuid:voxpop_id>/questions/new", views.new_question, name="new_question",),
    path("voxpops/<uuid:voxpop_id>/questions/stream", views.questions_stream_view, {"channel_prefix": ""}, name="stream_questions",),
    path("api/", api.urls),
    path("admin/", views.admin_index, name="admin"),
    path("admin/voxpops/new", views.new_voxpop, name="new_voxpop"),
    path("admin/voxpops/<uuid:voxpop_id>/edit", views.edit_voxpop, name="edit_voxpop"),
    path("admin/voxpops/<uuid:voxpop_id>/", views.admin_voxpop, name="admin_voxpop"),
    path("admin/voxpops/<uuid:voxpop_id>/<uuid:question_id>", views.admin_question_set_state, name="admin_question_set_state"),
    path("admin/voxpops/<uuid:voxpop_id>/questions/stream", views.questions_stream_view, {"channel_prefix": "admin_"}, name="admin_questions_stream"),
]
