"""Authorisation: the permission matrix, and its application to real routes."""

import pytest
from fastapi.routing import APIRoute

from backend.config.permissions import (
    PERMISSIONS,
    READ,
    WRITE,
    action_for_method,
    can,
    roles_for,
)
from backend.main import app
from backend.models.user import AccessRole

# Routes that are intentionally reachable without a token.
PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/appointments/public",
}

_GUARD_QUALNAMES = {
    "require_permission.<locals>._check",
    "require_roles.<locals>._check",
    "get_current_user",
}


def all_api_routes() -> list[dict]:
    """Flatten every mounted API route to {path, methods, guards}."""
    collected: list[dict] = []

    def guards_of(dependant) -> list[str]:
        names = []
        for dep in dependant.dependencies:
            qualname = getattr(dep.call, "__qualname__", "")
            if qualname in _GUARD_QUALNAMES:
                names.append(qualname)
        return names

    def visit(routes) -> None:
        for route in routes:
            if isinstance(route, APIRoute):
                collected.append(
                    {
                        "path": route.path,
                        "methods": set(route.methods or []),
                        "guards": guards_of(route.dependant),
                    }
                )
            elif hasattr(route, "effective_route_contexts"):
                for ctx in route.effective_route_contexts():
                    collected.append(
                        {
                            "path": ctx.path,
                            "methods": set(ctx.methods or []),
                            "guards": guards_of(ctx.dependant),
                        }
                    )
            elif hasattr(route, "routes"):
                visit(route.routes)

    visit(app.routes)
    return [r for r in collected if r["path"].startswith("/api/v1")]


def test_every_group_defines_both_actions():
    for group, actions in PERMISSIONS.items():
        assert READ in actions, f"{group} has no read audience"
        assert WRITE in actions, f"{group} has no write audience"


def test_admin_can_reach_everything_that_anyone_can():
    for group, actions in PERMISSIONS.items():
        for action, roles in actions.items():
            if roles and AccessRole.ADMIN not in roles:
                pytest.fail(f"Admin excluded from {group}/{action}")


def test_write_audience_is_never_wider_than_read():
    """Being able to change something you cannot see is incoherent."""
    for group, actions in PERMISSIONS.items():
        assert actions[WRITE] <= actions[READ], f"{group}: writers who cannot read"


@pytest.mark.parametrize(
    "method,expected",
    [
        ("GET", READ),
        ("HEAD", READ),
        ("OPTIONS", READ),
        ("POST", WRITE),
        ("PATCH", WRITE),
        ("PUT", WRITE),
        ("DELETE", WRITE),
        ("get", READ),
    ],
)
def test_method_maps_to_action(method, expected):
    assert action_for_method(method) == expected


def test_audit_log_cannot_be_written_by_anyone():
    """Append-only is enforced at three layers; this is the API one."""
    assert roles_for("audit", WRITE) == frozenset()
    for role in AccessRole:
        assert not can(role, "audit", "POST")
        assert not can(role, "audit", "DELETE")


def test_unknown_group_raises():
    with pytest.raises(KeyError):
        roles_for("no-such-group", READ)


def test_care_workers_can_chart_but_not_prescribe():
    assert can(AccessRole.CARE_WORKER, "resident_charts", "POST")
    assert can(AccessRole.CARE_WORKER, "resident_clinical", "GET")
    assert not can(AccessRole.CARE_WORKER, "resident_clinical", "POST")


def test_clinical_staff_cannot_read_hr_records():
    assert not can(AccessRole.NURSE, "employee_hr", "GET")
    assert not can(AccessRole.CARE_WORKER, "employee_hr", "GET")
    assert can(AccessRole.MANAGER, "employee_hr", "GET")


def test_all_staff_can_see_the_roster_but_only_leadership_changes_it():
    for role in (AccessRole.NURSE, AccessRole.CARE_WORKER):
        assert can(role, "employee_roster", "GET")
        assert not can(role, "employee_roster", "PATCH")
    assert can(AccessRole.MANAGER, "employee_roster", "PATCH")


def test_only_admins_touch_accounts():
    assert can(AccessRole.ADMIN, "users", "GET")
    for role in (AccessRole.MANAGER, AccessRole.NURSE, AccessRole.CARE_WORKER, AccessRole.FAMILY):
        assert not can(role, "users", "GET")


def test_family_role_has_no_staff_access():
    """The family role exists for a future portal."""
    for group in ("residents", "resident_charts", "resident_clinical", "employees", "users"):
        assert not can(AccessRole.FAMILY, group, "GET"), f"Family can read {group}"


def test_care_worker_is_refused_payroll(client, users, auth_header):
    response = client.get("/api/v1/payroll", headers=auth_header(users[AccessRole.CARE_WORKER]))
    assert response.status_code == 403
    assert "Care Worker" in response.json()["detail"]


def test_nurse_is_refused_user_administration(client, users, auth_header):
    assert (
        client.get("/api/v1/users", headers=auth_header(users[AccessRole.NURSE])).status_code == 403
    )


def test_denied_access_is_audited(client, users, auth_header, audit_entries):
    from backend.models.audit_log import AuditAction

    client.get("/api/v1/payroll", headers=auth_header(users[AccessRole.CARE_WORKER]))
    assert AuditAction.ACCESS_DENIED in [e.action for e in audit_entries]


def test_public_appointment_endpoint_is_mounted_and_open():
    routes = {(r["path"], m) for r in all_api_routes() for m in r["methods"]}
    assert ("/api/v1/appointments/public", "POST") in routes


def test_admin_appointment_routes_are_not_public():
    """The public endpoint must not have accidentally opened its neighbours."""
    for route in all_api_routes():
        if route["path"] == "/api/v1/appointments" or route["path"].startswith(
            "/api/v1/appointments/{"
        ):
            assert route["guards"], f"{route['methods']} {route['path']} is unguarded"


def test_no_route_is_left_unguarded():
    """Walks every mounted route."""
    unguarded = [
        f"{sorted(r['methods'])} {r['path']}"
        for r in all_api_routes()
        if r["path"] not in PUBLIC_PATHS and not r["guards"]
    ]
    assert not unguarded, "Unguarded routes: " + ", ".join(sorted(unguarded))


def test_the_route_walk_actually_finds_routes():
    routes = all_api_routes()
    assert len(routes) > 100, f"Only found {len(routes)} routes; the walk is broken"
    assert any(r["path"] == "/api/v1/residents" for r in routes)
