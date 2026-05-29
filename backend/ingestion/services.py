import importlib
import traceback
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.utils import timezone

from .models import IngestionJob


NORMALIZATION_VERSION = "sap-v2"
DEFAULT_SUSPICIOUS_AMOUNT_THRESHOLD = Decimal("100000")


def _to_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_decimal(value):
    text = _to_text(value)
    if text is None:
        raise ValueError("Missing amount value")
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid amount value: {text}")


def _normalize_unit(value):
    cleaned = _to_text(value)
    if cleaned is None:
        raise ValueError("Missing unit value")

    unit_key = cleaned.lower().replace("_", "").replace(" ", "")
    unit_map = {
        "kgco2e": "kgCO2e",
        "tco2e": "tCO2e",
        "gco2e": "gCO2e",
    }
    normalized = unit_map.get(unit_key)
    if not normalized:
        raise ValueError(f"Invalid unit value: {cleaned}")
    return normalized, cleaned != normalized


def _normalize_scope(value):
    cleaned = _to_text(value)
    if cleaned is None:
        raise ValueError("Missing scope value")

    scope_map = {
        "1": "scope_1",
        "2": "scope_2",
        "3": "scope_3",
        "scope_1": "scope_1",
        "scope_2": "scope_2",
        "scope_3": "scope_3",
    }
    normalized = scope_map.get(cleaned.lower())
    if not normalized:
        raise ValueError(f"Unsupported scope value: {cleaned}")
    return normalized


def _normalize_period(value):
    cleaned = _to_text(value)
    if cleaned is None:
        raise ValueError("Invalid date: missing period value")
    return cleaned


def _build_error_entry(row_number, errors, source_ref, raw_row):
    return {
        "row": row_number,
        "errors": errors,
        "source_ref": source_ref,
        "raw": raw_row,
    }


def _get_suspicious_threshold():
    configured = getattr(settings, "INGESTION_SUSPICIOUS_AMOUNT_THRESHOLD", DEFAULT_SUSPICIOUS_AMOUNT_THRESHOLD)
    try:
        return Decimal(str(configured))
    except (InvalidOperation, ValueError, TypeError):
        return DEFAULT_SUSPICIOUS_AMOUNT_THRESHOLD


def _extract_plant_code(record):
    plant_code = record.get("plant_code")
    if plant_code:
        return _to_text(plant_code)

    source_ref = record.get("source_ref") or {}
    row = source_ref.get("row") or {}
    if not isinstance(row, dict):
        return None

    for key, value in row.items():
        if key and key.strip().lower() in {"plant", "plant_code", "werk", "werks", "plantid"}:
            return _to_text(value)
    return None


def _collect_existing_plant_period_pairs(job):
    pairs = set()
    for existing in job.organization.emission_records.filter(source_type=job.source_type).only(
        "period",
        "source_ref",
        "normalized_payload",
    ):
        payload = existing.normalized_payload or {}
        source_ref = existing.source_ref or {}
        row = source_ref.get("row") if isinstance(source_ref, dict) else {}
        plant_code = payload.get("plant_code")
        if not plant_code and isinstance(row, dict):
            for key, value in row.items():
                if key and key.strip().lower() in {"plant", "plant_code", "werk", "werks", "plantid"}:
                    plant_code = _to_text(value)
                    break
        if plant_code and existing.period:
            pairs.add((plant_code, _to_text(existing.period)))
    return pairs


def _get_parser_for_source(source_type):
    mapping = {
        "sap": "sources.sap.parser",
        "utility": "sources.utility.parser",
        "travel": "sources.travel.parser",
    }
    module_path = mapping.get(source_type)
    if not module_path:
        raise ValueError(f"Unknown source_type: {source_type}")

    module = importlib.import_module(module_path)
    return getattr(module, "Parser")()


def run_ingestion_job(job: IngestionJob, file_obj, tenant=None):
    """Run ingestion synchronously: parse file, normalize, save EmissionRecords.

    Records that fail validation are logged in job.error_log and counted as failed.
    """
    job.records_total = 0
    job.records_failed = 0
    job.error_log = {}
    job.save()

    parser = _get_parser_for_source(job.source_type)
    try:
        records = parser.parse(file_obj)
    except Exception as e:
        job.error_log = {"fatal": str(e), "traceback": traceback.format_exc()}
        job.records_failed = 0
        job.records_total = 0
        job.save()
        return {"status": "failed", "error": str(e)}

    job.records_total = len(records)
    saved = 0
    failed = 0
    errors = []
    suspicious_threshold = _get_suspicious_threshold()
    seen_plant_period_pairs = set()
    existing_plant_period_pairs = _collect_existing_plant_period_pairs(job)

    from emissions.models import EmissionRecord, RecordStatus

    for idx, rec in enumerate(records, start=1):
        try:
            source_ref = rec.get("source_ref") or {"row_number": idx}
            raw_row = source_ref.get("row") or rec.get("raw_payload") or rec
            row_errors = []

            parse_errors = rec.get("parse_errors") or []
            row_errors.extend(parse_errors)

            missing_required_columns = rec.get("missing_required_columns") or []
            if missing_required_columns:
                row_errors.append(f"Missing required columns: {', '.join(sorted(set(missing_required_columns)))}")

            amount = Decimal("0")
            try:
                amount = _to_decimal(rec.get("amount"))
                if amount < 0:
                    row_errors.append("Negative emission value")
            except ValueError as exc:
                row_errors.append(str(exc))

            unit = "kgCO2e"
            unit_was_normalized = False
            try:
                unit, unit_was_normalized = _normalize_unit(rec.get("unit"))
            except ValueError as exc:
                row_errors.append(str(exc))

            period = ""
            try:
                period = _normalize_period(rec.get("period"))
            except ValueError as exc:
                row_errors.append(str(exc))

            scope_value = None
            try:
                scope_value = _normalize_scope(rec.get("scope"))
            except ValueError as exc:
                row_errors.append(str(exc))

            plant_code = _extract_plant_code(rec)

            if row_errors:
                raise ValueError("; ".join(dict.fromkeys(row_errors)))

            scope_choice = scope_value

            normalized_payload = {
                "amount": str(amount),
                "unit": unit,
                "period": period,
                "scope": scope_value,
                "plant_code": plant_code,
                "source_type": job.source_type,
            }

            flag_reasons = []
            if amount == 0:
                flag_reasons.append("amount is zero")
            if amount > suspicious_threshold:
                flag_reasons.append(f"amount exceeds threshold ({suspicious_threshold})")
            if plant_code is None:
                flag_reasons.append("missing plant code")
            if unit_was_normalized:
                flag_reasons.append("malformed units")

            if plant_code and period:
                plant_period = (plant_code, period)
                if plant_period in seen_plant_period_pairs or plant_period in existing_plant_period_pairs:
                    flag_reasons.append("duplicate plant + period exists")
                seen_plant_period_pairs.add(plant_period)

            EmissionRecord.objects.create(
                organization=job.organization,
                upload_batch=job.upload_batch,
                ingestion_job=job,
                amount=amount,
                unit=unit,
                period=period,
                scope=scope_choice,
                source_type=job.source_type,
                source_ref=source_ref,
                raw_payload=raw_row,
                normalized_payload=normalized_payload,
                flag_reasons=flag_reasons,
                normalization_version=NORMALIZATION_VERSION,
                normalized_at=timezone.now(),
                normalization_notes="SAP normalization v2 applied" if job.source_type == "sap" else "Ingestion normalization applied",
                status=RecordStatus.PENDING_REVIEW if flag_reasons else RecordStatus.PENDING,
            )
            saved += 1
        except Exception as e:
            failed += 1
            error_row_number = source_ref.get("row_number", idx)
            errors.append(_build_error_entry(error_row_number, [str(e)], source_ref, raw_row))

    job.records_failed = failed
    job.error_log = {"errors": errors, "summary": {"saved": saved, "failed": failed, "total": job.records_total}}
    job.save()

    return {"status": "done", "total": job.records_total, "saved": saved, "failed": failed}
