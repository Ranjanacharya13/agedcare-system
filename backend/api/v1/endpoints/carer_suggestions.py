from fastapi import APIRouter, Depends, Query

from backend.api.deps import get_carer_matching_service
from backend.schemas.carer_suggestion import CarerCandidateOut, SuggestAssignmentsOut
from backend.services.carer_matching import CarerMatchingService

router = APIRouter()


@router.get("/residents/{resident_id}/suggested-carers", response_model=list[CarerCandidateOut])
async def suggested_carers(
    resident_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    service: CarerMatchingService = Depends(get_carer_matching_service),
):
    """Who could take this resident, best first."""
    return await service.rank_candidates_for_resident(resident_id, limit)


@router.post("/coverage/suggest-assignments", response_model=SuggestAssignmentsOut)
async def suggest_assignments(
    limit: int = Query(default=50, ge=1, le=200),
    service: CarerMatchingService = Depends(get_carer_matching_service),
):
    return await service.suggest_assignments(limit)
