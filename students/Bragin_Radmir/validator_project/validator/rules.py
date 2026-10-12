from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional
from validator.models import Violation
from validator.exceptions import ConfigError


class Rule(ABC):
    def __init__(self, field: str, **kwargs):
        self.field = field
        self._validate_params(**kwargs)
        self._params = kwargs

    @abstractmethod
    def _validate_params(self, **kwargs):
        pass

    @abstractmethod
    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        pass

    def __repr__(self):
        params = ", ".join(f"{k}={v}" for k, v in self._params.items())
        return f"<{self.__class__.__name__}(field='{self.field}', {params})>"


class RequiredRule(Rule):
    def _validate_params(self, **kwargs):
        if kwargs:
            raise ConfigError(f"Правило 'required' не принимает параметров, получено: {kwargs}")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return Violation(record_no, self.field, "required", value, "обязательное поле пустое")
        return None


class TypeRule(Rule):
    ALLOWED_TYPES = {"int", "float", "bool", "str"}

    def _validate_params(self, **kwargs):
        if "type" not in kwargs:
            raise ConfigError(f"Правило 'type' требует параметр 'type'")
        if kwargs["type"] not in self.ALLOWED_TYPES:
            raise ConfigError(f"Неизвестный тип в правиле 'type': {kwargs['type']}")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        target_type = self._params["type"]

        if isinstance(value, str):
            value = value.strip()
            if target_type == "int":
                try:
                    int(value)
                except ValueError:
                    return Violation(record_no, self.field, "type", value, "ожидали int")
            elif target_type == "float":
                try:
                    float(value)
                except ValueError:
                    return Violation(record_no, self.field, "type", value, "ожидали float")
            elif target_type == "bool":
                if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                    return Violation(record_no, self.field, "type", value, "ожидали bool")
        else:
            if target_type == "int" and not isinstance(value, int):
                return Violation(record_no, self.field, "type", value, "ожидали int")
            if target_type == "float" and not isinstance(value, (int, float)):
                return Violation(record_no, self.field, "type", value, "ожидали float")
            if target_type == "bool" and not isinstance(value, bool):
                return Violation(record_no, self.field, "type", value, "ожидали bool")

        return None


class RangeRule(Rule):
    def _validate_params(self, **kwargs):
        if "min" not in kwargs and "max" not in kwargs:
            raise ConfigError(f"Правило 'range' требует хотя бы один параметр: min или max")
        if "min" in kwargs and "max" in kwargs:
            if kwargs["min"] > kwargs["max"]:
                raise ConfigError(f"Правило 'range': min ({kwargs['min']}) больше max ({kwargs['max']})")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        try:
            num = float(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            return None  # тип проверяет TypeRule

        min_val = self._params.get("min")
        max_val = self._params.get("max")

        if min_val is not None and num < min_val:
            return Violation(record_no, self.field, "range", value, f"вне диапазона {min_val}..{max_val if max_val is not None else '∞'}")
        if max_val is not None and num > max_val:
            return Violation(record_no, self.field, "range", value, f"вне диапазона {min_val if min_val is not None else '-∞'}..{max_val}")
        return None


class LengthRule(Rule):
    def _validate_params(self, **kwargs):
        if "min" not in kwargs and "max" not in kwargs:
            raise ConfigError(f"Правило 'length' требует хотя бы один параметр: min или max")
        if "min" in kwargs and "max" in kwargs:
            if kwargs["min"] > kwargs["max"]:
                raise ConfigError(f"Правило 'length': min ({kwargs['min']}) больше max ({kwargs['max']})")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        str_val = str(value)
        length = len(str_val)

        min_len = self._params.get("min")
        max_len = self._params.get("max")

        if min_len is not None and length < min_len:
            return Violation(record_no, self.field, "length", value, f"длина меньше минимальной {min_len}")
        if max_len is not None and length > max_len:
            return Violation(record_no, self.field, "length", value, f"длина больше максимальной {max_len}")
        return None


class EmailRule(Rule):
    def _validate_params(self, **kwargs):
        if kwargs:
            raise ConfigError(f"Правило 'email' не принимает параметров, получено: {kwargs}")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        s = str(value).strip()

        # Без пробелов
        if " " in s:
            return Violation(record_no, self.field, "email", value, "некорректный email")

        # Ровно одна @
        if s.count("@") != 1:
            return Violation(record_no, self.field, "email", value, "некорректный email")

        local, domain = s.split("@")

        # Непустая часть до @
        if not local:
            return Violation(record_no, self.field, "email", value, "некорректный email")

        # В домене точка не в начале и не в конце
        if not domain or domain.startswith(".") or domain.endswith("."):
            return Violation(record_no, self.field, "email", value, "некорректный email")

        if "." not in domain:
            return Violation(record_no, self.field, "email", value, "некорректный email")

        return None


class OneOfRule(Rule):
    def _validate_params(self, **kwargs):
        if "values" not in kwargs:
            raise ConfigError(f"Правило 'one_of' требует параметр 'values'")
        if not kwargs["values"]:
            raise ConfigError(f"Правило 'one_of': список values не может быть пустым")

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        allowed = self._params["values"]
        if value not in allowed:
            allowed_str = ", ".join(str(v) for v in allowed)
            return Violation(record_no, self.field, "one_of", value, f"нет в списке: {allowed_str}")
        return None


class UniqueRule(Rule):
    def __init__(self, field: str, **kwargs):
        self._seen: Dict[Any, int] = {}  # значение -> номер первой записи
        super().__init__(field, **kwargs)

    def _validate_params(self, **kwargs):
        if kwargs:
            raise ConfigError(f"Правило 'unique' не принимает параметров, получено: {kwargs}")

    def reset(self):
        """Сброс памяти между прогонами."""
        self._seen.clear()

    def check(self, value: Any, record_no: int) -> Optional[Violation]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        if value in self._seen:
            first_no = self._seen[value]
            return Violation(record_no, self.field, "unique", value, f" уже встречался в записи {first_no}")

        self._seen[value] = record_no
        return None


# Реестр правил (Фабрика)
RULES_REGISTRY: Dict[str, Type[Rule]] = {
    "required": RequiredRule,
    "type": TypeRule,
    "range": RangeRule,
    "length": LengthRule,
    "email": EmailRule,
    "one_of": OneOfRule,
    "unique": UniqueRule,
}
