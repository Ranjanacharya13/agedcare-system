from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from backend.config.settings import get_settings

_client: AsyncMongoClient | None = None


async def connect_to_mongo() -> None:
    global _client
    settings = get_settings()
    _client = AsyncMongoClient(settings.mongodb_uri)


async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


def get_database() -> AsyncDatabase:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo() first.")
    settings = get_settings()
    return _client[settings.mongodb_db_name]
