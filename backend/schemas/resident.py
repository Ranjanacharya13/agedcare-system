from datetime import date, datetime

from pydantic import BaseModel, model_validator

from backend.models.resident import CognitiveStatus, ResidentClassification


class ResidentCreate(BaseModel):
    full_name: str
    date_of_birth: date
    room_number: str
    care_level: str
    classification: ResidentClassification
    disability_cognitive_status: CognitiveStatus | None = None
    medical_notes: str | None = None

    @model_validator(mode="after")
    def validate_disability_cognitive_status(self) -> "ResidentCreate":
        if self.classification == ResidentClassification.DISABLED:
            if self.disability_cognitive_status is None:
                raise ValueError(
                    "disability_cognitive_status is required when classification is 'disabled'"
                )
        elif self.disability_cognitive_status is not None:
            raise ValueError(
                "disability_cognitive_status may only be set when classification is 'disabled'"
            )
        return self


class ResidentUpdate(BaseModel):
    full_name: str | None = None
    room_number: str | None = None
    care_level: str | None = None
    classification: ResidentClassification | None = None
    disability_cognitive_status: CognitiveStatus | None = None
    medical_notes: str | None = None

    @model_validator(mode="after")
    def validate_disability_cognitive_status(self) -> "ResidentUpdate":
        if self.classification is not None:
            if (
                self.classification == ResidentClassification.DISABLED
                and self.disability_cognitive_status is None
            ):
                raise ValueError(
                    "disability_cognitive_status is required when classification is 'disabled'"
                )
            if (
                self.classification != ResidentClassification.DISABLED
                and self.disability_cognitive_status is not None
            ):
                raise ValueError(
                    "disability_cognitive_status may only be set when classification is 'disabled'"
                )
        return self


class ResidentOut(BaseModel):
    id: str
    full_name: str
    date_of_birth: date
    room_number: str
    care_level: str
    classification: ResidentClassification
    disability_cognitive_status: CognitiveStatus | None = None
    medical_notes: str | None = None
    created_at: datetime
    updated_at: datetime
