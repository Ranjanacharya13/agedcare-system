from fastapi import APIRouter, Depends

from backend.api.deps import get_roster_optimisation_service
from backend.config.risk_weights import RISK_WEIGHTS
from backend.schemas.risk_score import CriterionWeightOut, RiskWeightModelOut
from backend.schemas.roster import RosterOptimiseOut, RosterOptimiseRequest
from backend.services.roster_optimisation import RosterOptimisationService

#: Running the optimiser — a POST, guarded by "roster_planning".
router = APIRouter()

#: Reading the weight model — a GET, guarded by the read-only "analytics".
weights_router = APIRouter()


@router.post("/roster/optimise", response_model=RosterOptimiseOut)
async def optimise_roster(
    payload: RosterOptimiseRequest,
    service: RosterOptimisationService = Depends(get_roster_optimisation_service),
):
    """Recommend staff for shifts: SAW score, then lexicographic ranking, earliest shift first."""
    return await service.optimise(
        shift_ids=[str(s) for s in payload.shift_ids] if payload.shift_ids else None,
        from_date=payload.from_date,
        to_date=payload.to_date,
        max_candidates=payload.max_candidates,
    )


@weights_router.get("/risk-weights", response_model=RiskWeightModelOut)
async def get_risk_weight_model():
    return RiskWeightModelOut(
        method="Simple Additive Weighting (SAW) — Australian clinical policy direct weights",
        weights=RISK_WEIGHTS,
        criteria=[
            CriterionWeightOut(
                criterion=name,
                weight=round(weight, 4),
                percentage=round(weight * 100, 2),
            )
            for name, weight in sorted(RISK_WEIGHTS.items(), key=lambda c: -c[1])
        ],
    )
