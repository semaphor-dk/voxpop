from ninja import NinjaAPI

from voxpop.api import router as polls_router

api = NinjaAPI()

api.add_router("/polls/", polls_router)
