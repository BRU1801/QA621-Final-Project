import json
from typing import List, Dict
from validator.exceptions import ConfigError
from validator.rules import Rule, RULES_REGISTRY


def load_rules(path: str) -> Dict[str, List[Rule]]:
    """Загружает rules.json и превращает в словарь {поле: [правила]}."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Файл правил не найден: {path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Битый JSON в '{path}': {e}")

    if not isinstance(config, dict) or "fields" not in config:
        raise ConfigError(f"Конфиг '{path}' должен содержать ключ 'fields'")

    fields_config = config["fields"]
    result: Dict[str, List[Rule]] = {}

    for field_name, rules_list in fields_config.items():
        if not isinstance(rules_list, list):
            raise ConfigError(f"Правила для поля '{field_name}' должны быть списком")

        rules = []
        for rule_dict in rules_list:
            if not isinstance(rule_dict, dict) or "rule" not in rule_dict:
                raise ConfigError(f"Правило для поля '{field_name}' должно содержать ключ 'rule'")

            rule_name = rule_dict["rule"]
            if rule_name not in RULES_REGISTRY:
                raise ConfigError(f"Неизвестное правило '{rule_name}' для поля '{field_name}'")

            rule_class = RULES_REGISTRY[rule_name]
            # Передаём все параметры кроме 'rule'
            params = {k: v for k, v in rule_dict.items() if k != "rule"}

            try:
                rule = rule_class(field=field_name, **params)
            except ConfigError:
                raise
            except Exception as e:
                raise ConfigError(f"Ошибка создания правила '{rule_name}' для поля '{field_name}': {e}")

            rules.append(rule)

        result[field_name] = rules

    return result
