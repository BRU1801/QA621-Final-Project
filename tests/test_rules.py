import pytest
from validator.rules import (
    RequiredRule, TypeRule, RangeRule, LengthRule,
    EmailRule, OneOfRule, UniqueRule
)
from validator.models import Violation
from validator.exceptions import ConfigError
class TestRequiredRule:

    def test_required_rule_accepts_valid_value(self):
        rule = RequiredRule(field="name")
        assert rule.check("Анна", 1) is None

    def test_required_rule_catches_empty_string(self):
        rule = RequiredRule(field="name")
        violation = rule.check("", 2)
        assert isinstance(violation, Violation)
        assert violation.record_no == 2
        assert violation.rule == "required"

    def test_required_rule_catches_none(self):
        rule = RequiredRule(field="name")
        violation = rule.check(None, 3)
        assert isinstance(violation, Violation)


class TestTypeRule:
    def test_type_rule_accepts_valid_int_string(self):
        rule = TypeRule(field="age", type="int")
        assert rule.check("25", 1) is None

    def test_type_rule_catches_invalid_int_string(self):
        rule = TypeRule(field="age", type="int")
        violation = rule.check("abc", 5)
        assert isinstance(violation, Violation)
        assert violation.rule == "type"
        assert "ожидали int" in violation.message

    def test_type_rule_skips_empty_values(self):
        rule = TypeRule(field="age", type="int")
        assert rule.check("", 1) is None
        assert rule.check(None, 1) is None

    def test_type_rule_config_error_missing_param(self):
        with pytest.raises(ConfigError) as exc_info:
            TypeRule(field="age")
        assert "требует параметр 'type'" in str(exc_info.value)

    def test_type_rule_config_error_unknown_type(self):
        with pytest.raises(ConfigError) as exc_info:
            TypeRule(field="age", type="datetime")
        assert "Неизвестный тип" in str(exc_info.value)

from validator.rules import RangeRule, LengthRule, EmailRule, OneOfRule, UniqueRule


class TestRangeRule:
    def test_range_rule_accepts_valid_value(self):
        rule = RangeRule(field="age", min=18, max=120)
        assert rule.check(25, 1) is None

    def test_range_rule_catches_below_min(self):
        rule = RangeRule(field="age", min=18, max=120)
        violation = rule.check(17, 2)
        assert isinstance(violation, Violation)
        assert violation.rule == "range"

    def test_range_rule_catches_above_max(self):
        rule = RangeRule(field="age", min=18, max=120)
        violation = rule.check(121, 3)
        assert isinstance(violation, Violation)

    def test_range_rule_skips_empty(self):
        rule = RangeRule(field="age", min=18, max=120)
        assert rule.check("", 1) is None
        assert rule.check(None, 1) is None

    def test_range_rule_config_error_min_greater_than_max(self):
        with pytest.raises(ConfigError):
            RangeRule(field="age", min=50, max=10)


class TestEmailRule:
    def test_email_rule_accepts_valid(self):
        rule = EmailRule(field="email")
        assert rule.check("user@example.com", 1) is None

    def test_email_rule_catches_no_at(self):
        rule = EmailRule(field="email")
        violation = rule.check("userexample.com", 2)
        assert isinstance(violation, Violation)
        assert violation.rule == "email"

    def test_email_rule_catches_no_dot_in_domain(self):
        rule = EmailRule(field="email")
        violation = rule.check("user@example", 3)
        assert isinstance(violation, Violation)

    def test_email_rule_catches_space(self):
        rule = EmailRule(field="email")
        violation = rule.check("us er@example.com", 4)
        assert isinstance(violation, Violation)


class TestOneOfRule:
    def test_one_of_accepts_valid(self):
        rule = OneOfRule(field="role", values=["admin", "user"])
        assert rule.check("admin", 1) is None

    def test_one_of_catches_invalid(self):
        rule = OneOfRule(field="role", values=["admin", "user"])
        violation = rule.check("manager", 2)
        assert isinstance(violation, Violation)
        assert "нет в списке" in violation.message


class TestUniqueRule:
    def test_unique_accepts_first(self):
        rule = UniqueRule(field="email")
        assert rule.check("a@b.com", 1) is None

    def test_unique_catches_duplicate(self):
        rule = UniqueRule(field="email")
        rule.check("a@b.com", 1)
        violation = rule.check("a@b.com", 2)
        assert isinstance(violation, Violation)
        assert "в записи 1" in violation.message

    def test_unique_skips_empty(self):
        rule = UniqueRule(field="email")
        assert rule.check("", 1) is None
        assert rule.check(None, 2) is None

from validator.rules import RangeRule, LengthRule, EmailRule, OneOfRule, UniqueRule


class TestRangeRule:
    def test_range_rule_accepts_valid_value(self):
        rule = RangeRule(field="age", min=18, max=120)
        assert rule.check(25, 1) is None

    def test_range_rule_catches_below_min(self):
        rule = RangeRule(field="age", min=18, max=120)
        violation = rule.check(17, 2)
        assert isinstance(violation, Violation)
        assert violation.rule == "range"

    def test_range_rule_catches_above_max(self):
        rule = RangeRule(field="age", min=18, max=120)
        violation = rule.check(121, 3)
        assert isinstance(violation, Violation)

    def test_range_rule_skips_empty(self):
        rule = RangeRule(field="age", min=18, max=120)
        assert rule.check("", 1) is None
        assert rule.check(None, 1) is None

    def test_range_rule_config_error_min_greater_than_max(self):
        with pytest.raises(ConfigError):
            RangeRule(field="age", min=50, max=10)


class TestEmailRule:
    def test_email_rule_accepts_valid(self):
        rule = EmailRule(field="email")
        assert rule.check("user@example.com", 1) is None

    def test_email_rule_catches_no_at(self):
        rule = EmailRule(field="email")
        violation = rule.check("userexample.com", 2)
        assert isinstance(violation, Violation)
        assert violation.rule == "email"

    def test_email_rule_catches_no_dot_in_domain(self):
        rule = EmailRule(field="email")
        violation = rule.check("user@example", 3)
        assert isinstance(violation, Violation)

    def test_email_rule_catches_space(self):
        rule = EmailRule(field="email")
        violation = rule.check("us er@example.com", 4)
        assert isinstance(violation, Violation)


class TestOneOfRule:
    def test_one_of_accepts_valid(self):
        rule = OneOfRule(field="role", values=["admin", "user"])
        assert rule.check("admin", 1) is None

    def test_one_of_catches_invalid(self):
        rule = OneOfRule(field="role", values=["admin", "user"])
        violation = rule.check("manager", 2)
        assert isinstance(violation, Violation)
        assert "нет в списке" in violation.message


class TestUniqueRule:
    def test_unique_accepts_first(self):
        rule = UniqueRule(field="email")
        assert rule.check("a@b.com", 1) is None

    def test_unique_catches_duplicate(self):
        rule = UniqueRule(field="email")
        rule.check("a@b.com", 1)
        violation = rule.check("a@b.com", 2)
        assert isinstance(violation, Violation)
        assert "в записи 1" in violation.message

    def test_unique_skips_empty(self):
        rule = UniqueRule(field="email")
        assert rule.check("", 1) is None
        assert rule.check(None, 2) is None