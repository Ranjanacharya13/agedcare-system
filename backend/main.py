from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
