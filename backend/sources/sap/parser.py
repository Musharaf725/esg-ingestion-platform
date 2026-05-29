import csv
from datetime import datetime

from ..base import BaseParser
from .schema import COLUMN_ALIASES, DATE_FORMATS, SCOPE_ALIASES, UNIT_ALIASES


def _clean(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _find_value(row, aliases):
    for alias in aliases:
        for key, value in row.items():
            if key is None:
                continue
            if key.strip().lower() == alias:
                return value, key
    return None, None


def _parse_date(value):
    cleaned = _clean(value)
    if not cleaned:
        return None, "Missing date value"

    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, date_format).date().isoformat(), None
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(cleaned).date().isoformat(), None
    except ValueError:
        return None, f"Invalid date format: {cleaned}"


def _normalize_unit(value):
    cleaned = _clean(value)
    if not cleaned:
        return None, "Missing unit value", None

    compact = cleaned.lower().replace("_", "").replace(" ", "")
    normalized = UNIT_ALIASES.get(compact)
    if normalized:
        return normalized, None, cleaned != normalized

    return None, f"Invalid unit value: {cleaned}", None


def _normalize_scope(value):
    cleaned = _clean(value)
    if not cleaned:
        return None, "Missing scope value"

    normalized = SCOPE_ALIASES.get(cleaned.lower())
    if normalized:
        return normalized, None

    return None, f"Unsupported scope value: {cleaned}"


def _normalize_amount(value):
    cleaned = _clean(value)
    if not cleaned:
        return None, "Missing amount value"

    try:
        float(cleaned)
    except ValueError:
        return None, f"Invalid amount value: {cleaned}"
    return cleaned, None


class Parser(BaseParser):
    def parse(self, file_obj):
        text = file_obj.read().decode("utf-8") if hasattr(file_obj, "read") else str(file_obj)
        reader = csv.DictReader(text.splitlines())
        out = []
        for row_number, row in enumerate(reader, start=2):
            parse_errors = []

            amount_raw, amount_column = _find_value(row, COLUMN_ALIASES["amount"])
            unit_raw, unit_column = _find_value(row, COLUMN_ALIASES["unit"])
            period_raw, period_column = _find_value(row, COLUMN_ALIASES["period"])
            scope_raw, scope_column = _find_value(row, COLUMN_ALIASES["scope"])
            plant_raw, plant_column = _find_value(row, COLUMN_ALIASES["plant_code"])

            amount, amount_error = _normalize_amount(amount_raw)
            if amount_error:
                parse_errors.append(amount_error)

            unit, unit_error, unit_malformed = _normalize_unit(unit_raw)
            if unit_error:
                parse_errors.append(unit_error)

            period, period_error = _parse_date(period_raw)
            if period_error:
                parse_errors.append(period_error)

            scope, scope_error = _normalize_scope(scope_raw)
            if scope_error:
                parse_errors.append(scope_error)

            missing_required_columns = [
                field_name
                for field_name, matched_column in {
                    "amount": amount_column,
                    "unit": unit_column,
                    "period": period_column,
                    "scope": scope_column,
                }.items()
                if matched_column is None
            ]

            rec = {
                "amount": amount,
                "unit": unit,
                "period": period,
                "scope": scope,
                "plant_code": _clean(plant_raw),
                "amount_raw": _clean(amount_raw),
                "unit_raw": _clean(unit_raw),
                "period_raw": _clean(period_raw),
                "scope_raw": _clean(scope_raw),
                "plant_raw": _clean(plant_raw),
                "unit_malformed": bool(unit_malformed),
                "missing_required_columns": missing_required_columns,
                "parse_errors": parse_errors,
                "source_ref": {
                    "row_number": row_number,
                    "row": row,
                    "columns": {
                        "amount": amount_column,
                        "unit": unit_column,
                        "period": period_column,
                        "scope": scope_column,
                        "plant_code": plant_column,
                    },
                },
                "raw_payload": row,
                "source_type": "sap",
                "status": "pending",
            }
            out.append(rec)
        return out
