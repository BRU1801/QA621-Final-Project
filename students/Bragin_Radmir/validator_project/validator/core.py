from validator.models import Violation, ValidationResult
from validator.decorators import timed
from validator.exceptions import ConfigError


class Validator:
    def __init__(self, rules_by_field: dict):
        self._rules_by_field = rules_by_field
        # Сбрасываем unique-правила перед прогоном
        for rules in rules_by_field.values():
            for rule in rules:
                if hasattr(rule, 'reset'):
                    rule.reset()

    @timed
    def validate(self, records: list) -> ValidationResult:
        result = ValidationResult(source="", rules_source="")
        result.total_records = len(records)

        for record_no, record in enumerate(records, start=1):
            for field_name, rules in self._rules_by_field.items():
                value = record.get(field_name)
                for rule in rules:
                    violation = rule.check(value, record_no)
                    if violation is not None:
                        result.add_violation(violation)

        return result
