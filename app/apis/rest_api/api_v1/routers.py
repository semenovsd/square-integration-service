from fastapi import APIRouter

from apis.rest_api.api_v1.endpoints.square import auth
from config import settings

square_router = APIRouter(prefix=settings.API_V1_STR)
square_router.include_router(auth.router, prefix="/square", tags=["square"])
