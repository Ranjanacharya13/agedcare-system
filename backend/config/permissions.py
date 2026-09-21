"""Who may read and who may write, per group of resources."""

from backend.models.user import AccessRole

ADMIN = AccessRole.ADMIN
MANAGER = AccessRole.MANAGER
NURSE = AccessRole.NURSE
CARE_WORKER = AccessRole.CARE_WORKER
FAMILY = AccessRole.FAMILY

ALL_STAFF = frozenset({ADMIN, MANAGER, NURSE, CARE_WORKER})
CLINICAL_STAFF = frozenset({ADMIN, MANAGER, NURSE})
LEADERSHIP = frozenset({ADMIN, MANAGER})
ADMIN_ONLY = frozenset({ADMIN})

READ = "read"
WRITE = "write"

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def action_for_method(method: str) -> str:
    return WRITE if method.upper() in _WRITE_METHODS else READ


#: resource group -> {READ: roles, WRITE: roles}
PERMISSIONS: dict[str, dict[str, frozenset[AccessRole]]] = {
    "residents": {READ: ALL_STAFF, WRITE: CLINICAL_STAFF},
    "resident_charts": {READ: ALL_STAFF, WRITE: ALL_STAFF},
    "resident_clinical": {READ: ALL_STAFF, WRITE: CLINICAL_STAFF},
    "assignments": {READ: ALL_STAFF, WRITE: CLINICAL_STAFF},
    "employees": {READ: ALL_STAFF, WRITE: LEADERSHIP},
    "employee_roster": {READ: ALL_STAFF, WRITE: LEADERSHIP},
    "employee_hr": {READ: LEADERSHIP, WRITE: LEADERSHIP},
    "complaints": {READ: LEADERSHIP, WRITE: LEADERSHIP},
    "appointments": {READ: ALL_STAFF, WRITE: LEADERSHIP},
    "analytics": {READ: ALL_STAFF, WRITE: frozenset()},
    "roster_planning": {READ: ALL_STAFF, WRITE: LEADERSHIP},
    "users": {READ: ADMIN_ONLY, WRITE: ADMIN_ONLY},
    "audit": {READ: LEADERSHIP, WRITE: frozenset()},
}


def roles_for(group: str, action: str) -> frozenset[AccessRole]:
    try:
        return PERMISSIONS[group][action]
    except KeyError as exc:  # pragma: no cover - guarded by test_permissions
        raise KeyError(f"Unknown permission group/action: {group}/{action}") from exc


def can(role: AccessRole, group: str, method: str) -> bool:
    return role in roles_for(group, action_for_method(method))
