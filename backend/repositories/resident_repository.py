from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from backend.models.resident import Resident

COLLECTION_NAME = "residents"


class ResidentRepository:
    def __init__(self, db: AsyncDatabase):
        self._collection = db[COLLECTION_NAME]

    async def create(self, resident: Resident) -> Resident:
        doc = resident.model_dump(by_alias=True, exclude={"id"})
        result = await self._collection.insert_one(doc)
        resident.id = str(result.inserted_id)
        return resident

    async def get_by_id(self, resident_id: str) -> Resident | None:
        if not ObjectId.is_valid(resident_id):
            return None
        doc = await self._collection.find_one({"_id": ObjectId(resident_id)})
        return Resident(**doc) if doc else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Resident]:
        cursor = self._collection.find().skip(skip).limit(limit)
        return [Resident(**doc) async for doc in cursor]

    async def update(self, resident_id: str, updates: dict) -> Resident | None:
        if not ObjectId.is_valid(resident_id):
            return None
        await self._collection.update_one({"_id": ObjectId(resident_id)}, {"$set": updates})
        return await self.get_by_id(resident_id)

    async def delete(self, resident_id: str) -> bool:
        if not ObjectId.is_valid(resident_id):
            return False
        result = await self._collection.delete_one({"_id": ObjectId(resident_id)})
        return result.deleted_count > 0
