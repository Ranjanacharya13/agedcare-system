"""Authentication: tokens, login, lockout, and self-service."""

from datetime import timedelta

import pytest

from backend.config.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.models.audit_log import AuditAction
from backend.models.user import AccessRole
from backend.tests.conftest import TEST_PASSWORD, make_user


def test_password_hash_is_not_reversible_and_verifies():
    hashed = hash_password("a-long-enough-password")
    assert hashed != "a-long-enough-password"
    assert verify_password("a-long-enough-password", hashed)
    assert not verify_password("a-long-enough-passwore", hashed)


def test_token_round_trips_subject_and_role():
    token = create_access_token("user-123", role="Nurse", email="n@careos.example.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "Nurse"
    assert payload["email"] == "n@careos.example.com"


def test_expired_token_is_rejected():
    token = create_access_token("user-123", expires_delta=timedelta(seconds=-1))
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_token_signed_with_another_key_is_rejected():
    import jwt

    forged = jwt.encode({"sub": "user-123", "exp": 9999999999}, "not-our-key", algorithm="HS256")
    with pytest.raises(TokenError):
        decode_access_token(forged)


def test_garbage_token_is_rejected():
    with pytest.raises(TokenError):
        decode_access_token("not-a-token")


def test_login_returns_a_usable_token(client, users):
    admin = users[AccessRole.ADMIN]
    response = client.post(
        "/api/v1/auth/login", json={"email": admin.email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == admin.email
    # The hash must never cross the wire.
    assert "password_hash" not in body["user"]

    me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["access_role"] == AccessRole.ADMIN.value


def test_login_is_case_insensitive_on_email(client, users):
    admin = users[AccessRole.ADMIN]
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin.email.upper(), "password": TEST_PASSWORD},
    )
    assert response.status_code == 200


def test_wrong_password_is_rejected(client, users):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": users[AccessRole.NURSE].email, "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_unknown_and_known_emails_give_the_same_error(client, users):
    unknown = client.post(
        "/api/v1/auth/login", json={"email": "nobody@careos.example.com", "password": "whatever"}
    )
    known = client.post(
        "/api/v1/auth/login",
        json={"email": users[AccessRole.NURSE].email, "password": "wrong-password"},
    )
    assert unknown.status_code == known.status_code == 401
    # Identical wording, so the response cannot be used to enumerate accounts.
    assert unknown.json()["detail"] == known.json()["detail"]


def test_deactivated_account_cannot_log_in(client, user_repository):
    disabled = make_user(AccessRole.NURSE, active=False, email="gone@careos.example.com")
    user_repository._users[str(disabled.id)] = disabled

    response = client.post(
        "/api/v1/auth/login", json={"email": disabled.email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 401


def test_repeated_failures_trigger_lockout(client, users):
    email = users[AccessRole.CARE_WORKER].email
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": "wrong"}
            ).status_code
            == 401
        )

    locked = client.post("/api/v1/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert locked.status_code == 429
    assert "Retry-After" in locked.headers


def test_failed_login_is_audited(client, users, audit_entries):
    client.post(
        "/api/v1/auth/login",
        json={"email": users[AccessRole.NURSE].email, "password": "wrong"},
    )
    actions = [e.action for e in audit_entries]
    assert AuditAction.LOGIN_FAILED in actions


def test_successful_login_is_audited(client, users, audit_entries):
    client.post(
        "/api/v1/auth/login",
        json={"email": users[AccessRole.NURSE].email, "password": TEST_PASSWORD},
    )
    assert AuditAction.LOGIN in [e.action for e in audit_entries]


def test_protected_route_requires_a_token(client):
    response = client.get("/api/v1/residents")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_protected_route_rejects_a_forged_token(client):
    import jwt

    forged = jwt.encode({"sub": "whoever", "exp": 9999999999}, "wrong-key", algorithm="HS256")
    response = client.get("/api/v1/residents", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


def test_token_for_a_deleted_user_is_rejected(client, users, auth_header):
    nurse = users[AccessRole.NURSE]
    headers = auth_header(nurse)
    client.user_repository._users.pop(str(nurse.id))
    assert client.get("/api/v1/residents", headers=headers).status_code == 401


def test_token_for_a_deactivated_user_is_rejected(client, users, auth_header):
    nurse = users[AccessRole.NURSE]
    headers = auth_header(nurse)
    client.user_repository._users[str(nurse.id)] = nurse.model_copy(update={"active": False})
    assert client.get("/api/v1/residents", headers=headers).status_code == 401


def test_change_password_requires_the_current_one(client, users, auth_header):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_header(users[AccessRole.NURSE]),
        json={"current_password": "not-it", "new_password": "a-brand-new-password"},
    )
    assert response.status_code == 400


def test_change_password_succeeds_and_the_new_one_works(client, users, auth_header):
    nurse = users[AccessRole.NURSE]
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_header(nurse),
        json={"current_password": TEST_PASSWORD, "new_password": "a-brand-new-password"},
    )
    assert response.status_code == 204

    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": nurse.email, "password": "a-brand-new-password"},
        ).status_code
        == 200
    )


def test_short_passwords_are_rejected(client, users, auth_header):
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_header(users[AccessRole.NURSE]),
        json={"current_password": TEST_PASSWORD, "new_password": "short"},
    )
    assert response.status_code == 422


def test_password_change_does_not_record_the_password(client, users, auth_header, audit_entries):
    client.post(
        "/api/v1/auth/change-password",
        headers=auth_header(users[AccessRole.NURSE]),
        json={"current_password": TEST_PASSWORD, "new_password": "a-brand-new-password"},
    )
    serialised = " ".join(str(e.model_dump()) for e in audit_entries)
    assert "a-brand-new-password" not in serialised
    assert TEST_PASSWORD not in serialised
