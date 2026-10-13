import pytest
from validator.core import Validator
from validator.rules import RequiredRule, TypeRule, EmailRule
from validator.models import Violation


def test_validator_finds_violations():
    rules = {
        "name": [RequiredRule(field="name")],
        "email": [RequiredRule(field="email"), EmailRule(field="email")],
    }
    validator = Validator(rules)

    records = [
        {"name": "Анна", "email": "anna@example.com"},
        {"name": "", "email": "bad@"},
    ]

    result = validator.validate(records)
    result.total_records = len(records)

    assert len(result) == 2  # 2 нарушения
    assert result.invalid_count == 1  # 1 запись с ошибками
    assert result.valid_count == 1  # 1 запись без ошибок


def test_validator_empty_records():
    rules = {"name": [RequiredRule(field="name")]}
    validator = Validator(rules)

    result = validator.validate([])
    result.total_records = 0

    assert len(result) == 0
    assert result.valid_count == 0


def test_validator_all_valid():
    rules = {
        "name": [RequiredRule(field="name")],
        "age": [TypeRule(field="age", type="int")],
    }
    validator = Validator(rules)

    records = [
        {"name": "Анна", "age": "25"},
        {"name": "Борис", "age": "30"},
    ]

    result = validator.validate(records)
    result.total_records = len(records)

    assert len(result) == 0
    assert result.valid_count == 2