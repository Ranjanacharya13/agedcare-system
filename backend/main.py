import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from backend.api.v1.router import api_router
from backend.config.settings import get_settings
from backend.db.supabase_client import close_supabase_connection, connect_to_supabase

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.secret_key_is_default:
        logger.warning(
            "SECRET_KEY is unset or still 'change-me'. Access tokens are forgeable. "
            "Set secret_key in backend/.env before running anywhere but localhost."
        )
    await connect_to_supabase()
    yield
    await close_supabase_connection()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        lifespan=lifespan,
        # Documents the bearer scheme so /docs offers an Authorize button.
        swagger_ui_init_oauth=None,
    )

    # Order matters: middleware added last runs first. Request context must be
    # established before anything that might want to audit.
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
