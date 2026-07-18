from fastapi import APIRouter

from backend.api.v1.endpoints import health, residents

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(residents.router, prefix="/residents", tags=["residents"])
