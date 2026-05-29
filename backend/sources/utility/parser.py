import csv
from ..base import BaseParser


class Parser(BaseParser):
    def parse(self, file_obj):
        text = file_obj.read().decode("utf-8") if hasattr(file_obj, "read") else str(file_obj)
        reader = csv.DictReader(text.splitlines())
        out = []
        for row in reader:
            rec = {
                "amount": row.get("kWh") or row.get("consumption") or 0,
                "unit": "kWh",
                "period": row.get("date") or row.get("period"),
                "scope": "2",
                "source_ref": {"row": row},
                "source_type": "utility",
                "status": "pending",
            }
            out.append(rec)
        return out
