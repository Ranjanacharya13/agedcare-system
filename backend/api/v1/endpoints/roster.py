from fastapi import APIRouter, Depends

from backend.algorithms.ahp import CONSISTENCY_THRESHOLD, build_matrix
from backend.api.deps import get_roster_optimisation_service
from backend.config.risk_weights import (
    JUDGEMENTS,
    RISK_CRITERIA,
    RISK_WEIGHT_MODEL,
)
from backend.schemas.risk_score import AHPCriterionOut, RiskWeightModelOut
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
    model = RISK_WEIGHT_MODEL
    return RiskWeightModelOut(
        method="Analytic Hierarchy Process (Saaty) — principal eigenvector by power iteration",
        criteria=[
            AHPCriterionOut(
                criterion=name,
                weight=round(model.weights[name], 6),
                percentage=round(model.weights[name] * 100, 2),
            )
            for name in sorted(RISK_CRITERIA, key=lambda c: -model.weights[c])
        ],
        comparison_matrix=[
            [round(value, 4) for value in row]
            for row in build_matrix(RISK_CRITERIA, JUDGEMENTS)
        ],
        lambda_max=round(model.lambda_max, 6),
        consistency_index=round(model.consistency_index, 6),
        consistency_ratio=round(model.consistency_ratio, 6),
        consistency_threshold=CONSISTENCY_THRESHOLD,
        is_consistent=model.is_consistent,
        verdict=model.verdict,
    )
