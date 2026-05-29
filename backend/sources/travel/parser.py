import json
from ..base import BaseParser


class Parser(BaseParser):
    def parse(self, file_obj):
        text = file_obj.read()
        try:
            data = json.loads(text)
        except Exception:
            # assume JSON lines
            text_str = text.decode("utf-8") if isinstance(text, bytes) else str(text)
            data = [json.loads(l) for l in text_str.splitlines() if l.strip()]

        out = []
        for item in data:
            rec = {
                "amount": item.get("kg_co2") or item.get("co2e") or 0,
                "unit": "kgCO2e",
                "period": item.get("date") or item.get("start_date"),
                "scope": "3",
                "source_ref": {"item": item},
                "source_type": "travel",
                "status": "pending",
            }
            out.append(rec)
        return out
