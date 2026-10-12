from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True, order=True)
class Violation:
    record_no: int
    field: str
    rule: str
    value: Optional[str]
    message: str

    def __str__(self):
        val_repr = repr(self.value) if self.value is not None else "None"
        return f"Запись {self.record_no:2d}  {self.field:<8} {self.rule:<8} {val_repr} — {self.message}"


class ValidationResult:
    """Хранит результаты проверки одного набора данных."""
    def __init__(self, source: str, rules_source: str):
        self.source = source
        self.rules_source = rules_source
        self.violations: List[Violation] = []
        self.total_records = 0
        self.elapsed_time: float = 0.0

    def add_violation(self, violation: Violation):
        self.violations.append(violation)

    def __len__(self):
        return len(self.violations)

    def __iter__(self):
        return iter(sorted(self.violations))  # Сортировка благодаря order=True в dataclass

    def __bool__(self):
        # True, если нарушений НЕТ, False, если есть нарушения
        return len(self.violations) == 0

    @property
    def valid_count(self) -> int:
        unique_invalid_records = len(set(v.record_no for v in self.violations))
        return self.total_records - unique_invalid_records

    @property
    def invalid_count(self) -> int:
        return len(set(v.record_no for v in self.violations))

    @property
    def by_rule(self) -> dict:
        result = {}
        for v in self.violations:
            result[v.rule] = result.get(v.rule, 0) + 1
        return result

    @property
    def by_field(self) -> dict:
        result = {}
        for v in self.violations:
            result[v.field] = result.get(v.field, 0) + 1
        return result

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "rules": self.rules_source,
            "summary": {
                "records": self.total_records,
                "valid": self.valid_count,
                "invalid": self.invalid_count,
                "violations": len(self.violations),
                "by_rule": self.by_rule,
                "by_field": self.by_field,
            },
            "violations": [
                {
                    "record_no": v.record_no,
                    "field": v.field,
                    "rule": v.rule,
                    "value": v.value,
                    "message": v.message,
                }
                for v in sorted(self.violations)
            ],
        }
