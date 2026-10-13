import pytest
from validator.config import load_rules
from validator.exceptions import ConfigError
from validator.rules import RequiredRule, TypeRule, EmailRule


def test_load_rules_valid_config(tmp_path):
    config_file = tmp_path / "rules.json"
    config_file.write_text('''
    {
        "dataset": "test",
        "fields": {
            "name": [{"rule": "required"}],
            "email": [{"rule": "required"}, {"rule": "email"}]
        }
    }
    ''', encoding='utf-8')

    rules = load_rules(str(config_file))

    assert "name" in rules
    assert "email" in rules
    assert len(rules["name"]) == 1
    assert isinstance(rules["name"][0], RequiredRule)
    assert len(rules["email"]) == 2
    assert isinstance(rules["email"][1], EmailRule)


def test_load_rules_file_not_found():
    with pytest.raises(ConfigError) as exc_info:
        load_rules("nonexistent.json")
    assert "не найден" in str(exc_info.value)


def test_load_rules_unknown_rule(tmp_path):
    config_file = tmp_path / "bad.json"
    config_file.write_text('''
    {
        "fields": {
            "name": [{"rule": "unknown_rule"}]
        }
    }
    ''', encoding='utf-8')

    with pytest.raises(ConfigError) as exc_info:
        load_rules(str(config_file))
    assert "Неизвестное правило" in str(exc_info.value)


def test_load_rules_missing_fields_key(tmp_path):
    config_file = tmp_path / "bad.json"
    config_file.write_text('{"dataset": "test"}', encoding='utf-8')

    with pytest.raises(ConfigError):
        load_rules(str(config_file))