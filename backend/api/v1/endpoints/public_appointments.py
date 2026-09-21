"""The one endpoint anyone on the internet may call."""

import logging

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from backend.api.deps import get_appointment_service
from backend.config.settings import get_settings
from backend.core.rate_limit import (
    SlidingWindowLimiter,
    client_ip,
    rate_limit_dependency,
)
from backend.schemas.appointment import AppointmentCreate
from backend.services.base import CrudService

logger = logging.getLogger(__name__)

_settings = get_settings()
_limiter = SlidingWindowLimiter(
    max_requests=_settings.public_form_rate_limit,
    window_seconds=_settings.public_form_rate_window_seconds,
)

router = APIRouter(dependencies=[Depends(rate_limit_dependency(_limiter))])


class PublicAppointmentRequest(AppointmentCreate):
    """The publicly submittable fields, plus a honeypot."""

    website: str | None = Field(default=None, max_length=200)


class PublicAppointmentAck(BaseModel):
    """Deliberately thin."""

    received: bool = True
    message: str = "Thanks — we'll be in touch within one business day."


@router.post(
    "/public",
    response_model=PublicAppointmentAck,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an appointment enquiry (public, rate limited)",
)
async def submit_public_appointment(
    payload: PublicAppointmentRequest,
    request: Request,
    service: CrudService = Depends(get_appointment_service),
):
    if payload.website:
        # Answer exactly as if it worked. Telling a bot it was caught only
        # teaches whoever wrote it to leave the field alone next time.
        logger.info("Discarded honeypot appointment submission from %s", client_ip(request))
        return PublicAppointmentAck()

    data = AppointmentCreate(**payload.model_dump(exclude={"website"}))
    await service.create(data)
    return PublicAppointmentAck()
