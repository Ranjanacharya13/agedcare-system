"""Per-request ambient state."""

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Actor:
    id: UUID | None
    email: str | None
    role: str | None


_ANONYMOUS = Actor(id=None, email=None, role=None)

_actor: ContextVar[Actor] = ContextVar("actor", default=_ANONYMOUS)
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_ip_address: ContextVar[str | None] = ContextVar("ip_address", default=None)


def set_actor(actor: Actor) -> None:
    _actor.set(actor)


def get_actor() -> Actor:
    return _actor.get()


def set_request_id(request_id: str | None) -> None:
    _request_id.set(request_id)


def get_request_id() -> str | None:
    return _request_id.get()


def set_ip_address(ip: str | None) -> None:
    _ip_address.set(ip)


def get_ip_address() -> str | None:
    return _ip_address.get()


def reset() -> None:
    """Clear the context."""
    _actor.set(_ANONYMOUS)
    _request_id.set(None)
    _ip_address.set(None)
