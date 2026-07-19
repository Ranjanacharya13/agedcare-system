from supabase import AsyncClient, acreate_client

from backend.config.settings import get_settings

_client: AsyncClient | None = None


async def connect_to_supabase() -> None:
    global _client
    settings = get_settings()
    _client = await acreate_client(settings.supabase_url, settings.supabase_key)


async def close_supabase_connection() -> None:
    global _client
    _client = None


def get_supabase() -> AsyncClient:
    if _client is None:
        raise RuntimeError("Supabase client is not initialized. Call connect_to_supabase() first.")
    return _client
