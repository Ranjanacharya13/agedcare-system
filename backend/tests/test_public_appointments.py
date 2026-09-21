"""The public appointment form — the only unauthenticated write in the API."""

import pytest

from backend.api.deps import get_appointment_service
from backend.api.v1.endpoints import public_appointments
from backend.main import app

VALID = {
    "full_name": "Ada Lovelace",
    "email": "ada@careos.example.com",
    "appointment_type": "Facility Tour",
}


class RecordingAppointmentService:
    def __init__(self):
        self.created = []

    async def create(self, data):
        self.created.append(data)
        return data


@pytest.fixture
def appointment_service():
    service = RecordingAppointmentService()
    app.dependency_overrides[get_appointment_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_appointment_service, None)


@pytest.fixture(autouse=True)
def fresh_limiter():
    public_appointments._limiter.reset()
    yield
    public_appointments._limiter.reset()


def test_a_visitor_can_submit_without_a_token(client, appointment_service):
    response = client.post("/api/v1/appointments/public", json=VALID)
    assert response.status_code == 201
    assert response.json()["received"] is True
    assert len(appointment_service.created) == 1


def test_the_response_leaks_no_record_details(client, appointment_service):
    body = client.post("/api/v1/appointments/public", json=VALID).json()
    assert set(body) == {"received", "message"}


def test_honeypot_submissions_are_discarded_silently(client, appointment_service):
    response = client.post(
        "/api/v1/appointments/public", json={**VALID, "website": "http://spam.example.com"}
    )
    # Indistinguishable from success, so a bot gets no signal to adapt to...
    assert response.status_code == 201
    assert response.json()["received"] is True
    # ...but nothing was stored.
    assert appointment_service.created == []


def test_admin_only_fields_cannot_be_set_by_the_public(client, appointment_service):
    client.post(
        "/api/v1/appointments/public",
        json={**VALID, "status": "Confirmed", "admin_notes": "let me in"},
    )
    created = appointment_service.created[0]
    assert not hasattr(created, "status")
    assert not hasattr(created, "admin_notes")


def test_invalid_email_is_rejected(client, appointment_service):
    response = client.post("/api/v1/appointments/public", json={**VALID, "email": "not-an-email"})
    assert response.status_code == 422
    assert appointment_service.created == []


def test_rate_limit_kicks_in_and_reports_when_to_retry(client, appointment_service):
    from backend.config.settings import get_settings

    allowed = get_settings().public_form_rate_limit
    for _ in range(allowed):
        assert client.post("/api/v1/appointments/public", json=VALID).status_code == 201

    blocked = client.post("/api/v1/appointments/public", json=VALID)
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0
    assert len(appointment_service.created) == allowed


def test_the_limiter_counts_per_client(client, appointment_service):
    limiter = public_appointments._limiter
    for _ in range(get_limit()):
        assert limiter.check("10.0.0.1") is None
    assert limiter.check("10.0.0.1") is not None
    assert limiter.check("10.0.0.2") is None


def get_limit() -> int:
    from backend.config.settings import get_settings

    return get_settings().public_form_rate_limit
