from fastapi import APIRouter

from app.api.routes import drop_off_points, login, private, users, utils, address, organizations, members
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(drop_off_points.router)
api_router.include_router(address.router)
api_router.include_router(organizations.router)
api_router.include_router(members.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
