"""Test fixtures."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api import deps
from backend.api.auth_deps import get_auth_service
from backend.config.security import create_access_token, hash_password
from backend.main import app
from backend.models.user import AccessRole, User
from backend.services import audit
from backend.services.login_throttle import LoginThrottle

TEST_PASSWORD = "correct-horse-battery"


def make_user(role: AccessRole, *, active: bool = True, email: str | None = None) -> User:
    return User(
        id=uuid4(),
        email=email or f"{role.value.lower().replace(' ', '.')}@careos.example.com",
        password_hash=hash_password(TEST_PASSWORD),
        access_role=role,
        full_name=role.value,
        active=active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class FakeUserRepository:
    """In-memory stand-in with the same surface the service uses."""

    def __init__(self, users: list[User] | None = None):
        self._users = {str(u.id): u for u in (users or [])}

    async def create(self, user: User) -> User:
        user = user.model_copy(update={"id": user.id or uuid4()})
        self._users[str(user.id)] = user
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(str(user_id))

    async def get_by_email(self, email: str) -> User | None:
        wanted = email.strip().lower()
        return next((u for u in self._users.values() if u.email.lower() == wanted), None)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return list(self._users.values())[skip : skip + limit]

    async def update(self, user_id: str, updates: dict) -> User | None:
        user = self._users.get(str(user_id))
        if user is None:
            return None
        updated = User.model_validate({**user.model_dump(), **updates})
        self._users[str(user_id)] = updated
        return updated

    async def delete(self, user_id: str) -> bool:
        return self._users.pop(str(user_id), None) is not None


@pytest.fixture(autouse=True)
def silence_audit(monkeypatch):
    """Audit writes go to Supabase."""
    written = []

    class CollectingAuditRepository:
        def __init__(self, client=None):
            pass

        async def create(self, entry):
            written.append(entry)
            return entry

    monkeypatch.setattr(audit, "AuditRepository", CollectingAuditRepository)
    monkeypatch.setattr(audit, "get_supabase", lambda: None)
    return written


@pytest.fixture
def audit_entries(silence_audit):
    return silence_audit


@pytest.fixture
def users() -> dict[AccessRole, User]:
    return {role: make_user(role) for role in AccessRole}


@pytest.fixture
def user_repository(users) -> FakeUserRepository:
    return FakeUserRepository(list(users.values()))


@pytest.fixture(autouse=True)
def no_supabase(monkeypatch):
    """Entering TestClient runs the app lifespan, which would dial Supabase."""

    async def _noop():
        return None

    monkeypatch.setattr("backend.main.connect_to_supabase", _noop)
    monkeypatch.setattr("backend.main.close_supabase_connection", _noop)


@pytest.fixture
def client(user_repository, no_supabase):
    from backend.services.auth_service import AuthService

    service = AuthService(user_repository, LoginThrottle())
    app.dependency_overrides[get_auth_service] = lambda: service
    app.dependency_overrides[deps.get_db] = _explode

    with TestClient(app) as test_client:
        test_client.auth_service = service
        test_client.user_repository = user_repository
        yield test_client

    app.dependency_overrides.clear()


def _explode(*args, **kwargs):  # pragma: no cover
    raise AssertionError("Test reached the database layer unexpectedly")


@pytest.fixture
def token_for():
    def _make(user: User) -> str:
        return create_access_token(
            subject=str(user.id), role=user.access_role.value, email=user.email
        )

    return _make


@pytest.fixture
def auth_header(token_for):
    def _make(user: User) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_for(user)}"}

    return _make


@pytest.fixture
def anyio_backend():
    """Run `@pytest.mark.anyio` tests on asyncio only."""
    return "asyncio"
