from ninja import NinjaAPI

from voxpop.api import router as voxpop_router

api = NinjaAPI()

api.add_router("/voxpop/", voxpop_router)