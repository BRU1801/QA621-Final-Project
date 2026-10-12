import pytest
from validator.config import load_rules
from validator.loaders import get_loader
from validator.core import Validator


def test_users_csv_has_7_violations():
    """Интеграционный тест: users.csv (22 записи) должен иметь ровно 7 нарушений."""
    rules = load_rules("rules/users.json")
    loader = get_loader("data/users.csv")
    records = loader.load("data/users.csv")

    validator = Validator(rules)
    result = validator.validate(records)
    result.total_records = len(records)

    assert len(result) == 7, f"Ожидалось 7 нарушений, получено {len(result)}"
    assert result.invalid_count == 5  # 5 записей содержат ошибки
    assert result.valid_count == 17  # 22 всего - 5 с ошибками = 17


def test_orders_json_has_6_violations():
    """Интеграционный тест: orders.json (21 запись) должен иметь ровно 6 нарушений."""
    rules = load_rules("rules/orders.json")
    loader = get_loader("data/orders.json")
    records = loader.load("data/orders.json")

    validator = Validator(rules)
    result = validator.validate(records)
    result.total_records = len(records)

    assert len(result) == 6, f"Ожидалось 6 нарушений, получено {len(result)}"
    assert result.invalid_count == 4  # 4 записи содержат ошибки
    assert result.valid_count == 17  # 21 всего - 4 с ошибками = 17