from pymongo.asynchronous.database import AsyncDatabase

from backend.db.mongodb import get_database
from backend.repositories.resident_repository import ResidentRepository
from backend.services.resident_service import ResidentService


def get_db() -> AsyncDatabase:
    return get_database()


def get_resident_service() -> ResidentService:
    repository = ResidentRepository(get_db())
    return ResidentService(repository)
