from datetime import date, datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentType(StrEnum):
    """Who this staff member is to this resident."""

    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    RELIEF = "Relief"


class ResidentAssignment(BaseModel):
    """A standing care relationship between one employee and one resident."""

    id: UUID | None = None
    resident_id: UUID | None = None
    employee_id: UUID | None = None
    assignment_type: AssignmentType = AssignmentType.SECONDARY
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
