from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import get_shift_matching_service
from backend.schemas.shift_suggestion import ShiftSuggestionOut
from backend.services.shift_matching import ShiftMatchingService

router = APIRouter()


@router.get("/shifts/{shift_id}/suggested-employees", response_model=list[ShiftSuggestionOut])
async def get_suggested_employees(
    shift_id: str, service: ShiftMatchingService = Depends(get_shift_matching_service)
):
    suggestions = await service.suggest_employees(shift_id)
    if suggestions is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shift record not found")
    return suggestions
