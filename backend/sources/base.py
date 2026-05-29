from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_obj):
        """Return a list of normalized dicts for EmissionRecord creation."""
        raise NotImplementedError()


class BaseValidator:
    def validate(self, record):
        required = ["amount", "unit", "period", "scope"]
        missing = [field for field in required if field not in record]
        if missing:
            raise ValueError(f"Missing fields: {missing}")
        return True
