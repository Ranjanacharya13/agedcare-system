from pydantic import BaseModel


class CriterionOut(BaseModel):
    """One SAW criterion: contribution = normalised x weight."""

    criterion: str
    value: str | float | None = None
    normalised: float
    weight: float
    contribution: float
