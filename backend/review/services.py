from django.db import transaction
from django.utils import timezone

from emissions.models import EmissionRecord, RecordStatus
from .models import AuditLog


class InvalidTransition(Exception):
    pass


ALLOWED_TRANSITIONS = {
    RecordStatus.PENDING: {RecordStatus.PENDING_REVIEW},
    RecordStatus.PENDING_REVIEW: {RecordStatus.APPROVED, RecordStatus.REJECTED},
}


def _record_snapshot(record: EmissionRecord):
    return {
        "status": record.status,
        "flag_reasons": list(record.flag_reasons or []),
        "reviewed_by_id": record.reviewed_by_id,
        "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else None,
        "rejection_reason": record.rejection_reason,
    }


def _create_audit_log(record: EmissionRecord, action: str, user, old_value, new_value, note=""):
    AuditLog.objects.create(
        organization=record.organization,
        record=record,
        action=action,
        old_value=old_value,
        new_value=new_value,
        performed_by=user,
        note=note,
    )


def _validate_transition(record: EmissionRecord, target_status: str):
    allowed = ALLOWED_TRANSITIONS.get(record.status, set())
    if target_status not in allowed:
        raise InvalidTransition(f"Cannot transition from '{record.status}' to '{target_status}'")


def _ensure_reviewable(record: EmissionRecord):
    if record.status == RecordStatus.APPROVED:
        raise InvalidTransition("Approved records are immutable")


def approve_record(record: EmissionRecord, user, note=""):
    _validate_transition(record, RecordStatus.APPROVED)

    old_value = _record_snapshot(record)
    record.status = RecordStatus.APPROVED
    record.reviewed_by = user
    record.reviewed_at = timezone.now()
    with transaction.atomic():
        record.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        _create_audit_log(
            record,
            "approved",
            user,
            old_value,
            {
                "status": RecordStatus.APPROVED,
                "reviewed_by_id": user.id if user else None,
                "reviewed_at": record.reviewed_at.isoformat(),
                "note": note,
            },
            note=note,
        )
    return record


def reject_record(record: EmissionRecord, user, reason):
    _validate_transition(record, RecordStatus.REJECTED)

    old_value = _record_snapshot(record)
    record.status = RecordStatus.REJECTED
    record.reviewed_by = user
    record.reviewed_at = timezone.now()
    record.rejection_reason = reason
    with transaction.atomic():
        record.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])
        _create_audit_log(
            record,
            "rejected",
            user,
            old_value,
            {
                "status": RecordStatus.REJECTED,
                "reviewed_by_id": user.id if user else None,
                "reviewed_at": record.reviewed_at.isoformat(),
                "reason": reason,
            },
            note=reason,
        )
    return record


def flag_record(record: EmissionRecord, user, reason: str, note: str = ""):
    if record.status not in {RecordStatus.PENDING, RecordStatus.PENDING_REVIEW}:
        raise InvalidTransition(f"Cannot flag from '{record.status}'")

    if not reason or not str(reason).strip():
        raise ValueError("Reason is required")

    old_value = _record_snapshot(record)
    flag_reasons = list(record.flag_reasons or [])
    clean_reason = str(reason).strip()
    if clean_reason not in flag_reasons:
        flag_reasons.append(clean_reason)

    target_status = record.status
    if record.status == RecordStatus.PENDING:
        _validate_transition(record, RecordStatus.PENDING_REVIEW)
        target_status = RecordStatus.PENDING_REVIEW

    record.flag_reasons = flag_reasons
    record.status = target_status
    with transaction.atomic():
        record.save(update_fields=["flag_reasons", "status"])
        _create_audit_log(
            record,
            "flagged",
            user,
            old_value,
            {
                "status": record.status,
                "flag_reasons": flag_reasons,
                "reason": clean_reason,
                "note": note,
            },
            note=note or clean_reason,
        )
    return record


def bulk_approve_records(records, user, note=""):
    approved = []
    errors = []

    with transaction.atomic():
        for record in records:
            try:
                approved.append(approve_record(record, user, note=note))
            except Exception as exc:
                errors.append({"record_id": str(record.id), "error": str(exc)})

    return {"approved": approved, "errors": errors, "count": len(approved)}
