"""The audit layer: what gets recorded, and what deliberately does not."""

from backend.services.audit import SENSITIVE_FIELDS, diff_changes


def test_diff_records_only_what_changed():
    changes = diff_changes(
        {"status": "Pending", "full_name": "Ada", "email": "a@careos.example.com"},
        {"status": "Confirmed", "full_name": "Ada", "email": "a@careos.example.com"},
    )
    assert changes == {"status": {"from": "Pending", "to": "Confirmed"}}


def test_diff_of_identical_records_is_empty():
    row = {"a": 1, "b": [1, 2], "c": None}
    assert diff_changes(row, dict(row)) == {}


def test_diff_captures_added_and_removed_fields():
    changes = diff_changes({"a": 1}, {"b": 2})
    assert changes["a"] == {"from": 1, "to": None}
    assert changes["b"] == {"from": None, "to": 2}


def test_creation_diff_has_no_before_side():
    changes = diff_changes(None, {"full_name": "Ada"})
    assert changes == {"full_name": {"from": None, "to": "Ada"}}


def test_sensitive_fields_are_redacted_in_both_directions():
    changes = diff_changes(
        {"password_hash": "$2b$old", "email": "a@careos.example.com"},
        {"password_hash": "$2b$new", "email": "b@careos.example.com"},
    )
    assert changes["password_hash"] == {"from": "***redacted***", "to": "***redacted***"}
    # Non-sensitive fields still show real values, or the log is useless.
    assert changes["email"] == {"from": "a@careos.example.com", "to": "b@careos.example.com"}


def test_redaction_is_case_insensitive():
    changes = diff_changes({"Password": "a"}, {"Password": "b"})
    assert changes["Password"]["to"] == "***redacted***"


def test_every_credential_field_name_is_covered():
    for field in ("password", "password_hash", "token", "access_token", "secret"):
        assert field in SENSITIVE_FIELDS


def test_audit_failure_does_not_propagate(monkeypatch):
    import anyio

    from backend.models.audit_log import AuditAction
    from backend.services import audit

    class BrokenRepository:
        async def create(self, entry):
            raise RuntimeError("audit table is unreachable")

    monkeypatch.setattr(audit, "AuditRepository", lambda client: BrokenRepository())
    monkeypatch.setattr(audit, "get_supabase", lambda: object())

    async def _run():
        # Should log and return, not raise.
        await audit.record_data_change(
            action=AuditAction.CREATE, table_name="residents", record_id="1", after={"a": 1}
        )

    anyio.run(_run)
