from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import get_risk_scoring_service
from backend.schemas.risk_score import RiskScoreOut
from backend.services.risk_scoring import RiskScoringService

router = APIRouter()


@router.get("/risk-scores", response_model=list[RiskScoreOut])
async def list_risk_scores(
    skip: int = 0,
    limit: int = 100,
    service: RiskScoringService = Depends(get_risk_scoring_service),
):
    return await service.list_scores(skip, limit)


@router.get("/residents/{resident_id}/risk-score", response_model=RiskScoreOut)
async def get_resident_risk_score(
    resident_id: str, service: RiskScoringService = Depends(get_risk_scoring_service)
):
    score = await service.get_resident_score(resident_id)
    if score is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resident not found")
    return score
