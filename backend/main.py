from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.v1.router import api_router
from backend.config.settings import get_settings
from backend.db.supabase_client import close_supabase_connection, connect_to_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_supabase()
    yield
    await close_supabase_connection()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.project_name, lifespan=lifespan)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
