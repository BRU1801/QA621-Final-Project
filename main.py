import sys
import os

# Добавляем корень проекта в пути
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validator.config import load_rules
from validator.loaders import get_loader
from validator.core import Validator
from validator.reporters import get_reporter, REPORTERS_REGISTRY
from validator.rules import RULES_REGISTRY
from validator.exceptions import ValidatorError


def print_rules_list():
    """Команда rules: печатает список доступных правил."""
    print("Доступные правила валидации:\n")
    for name, rule_class in sorted(RULES_REGISTRY.items()):
        params = []
        if hasattr(rule_class, '_validate_params'):
            # Показываем параметры из докстринга или из сигнатуры
            pass
        print(f"  {name:<12} — {rule_class.__name__}")
    print()


def run_check(data_path: str, rules_path: str, report_format: str = "console"):
    """Основная логика проверки."""
    # Загружаем правила
    rules_by_field = load_rules(rules_path)

    # Загружаем данные
    loader = get_loader(data_path)
    records = loader.load(data_path)

    # Валидация
    validator = Validator(rules_by_field)
    result = validator.validate(records)
    result.source = data_path
    result.rules_source = rules_path

    # Отчёт
    reporter = get_reporter(report_format)

    if report_format == "console":
        reporter.report (result)
    else:
        # Формируем путь отчёта
        base_name = os.path.splitext(os.path.basename(data_path))[0]
        output_path = os.path.join("reports", f"{base_name}_report.{report_format}")
        reporter.report(result, output_path)
        print(f"Отчёт сохранён: {output_path}")

    # Код выхода
    return 0 if len(result) == 0 else 1


def main():
    args = sys.argv[1:]

    if not args:
        print("Использование: python main.py check <data> --rules <rules.json> [--report format]")
        print("               python main.py rules")
        sys.exit(2)

    command = args[0]

    if command == "rules":
        print_rules_list()
        sys.exit(0)

    if command == "check":
        if len(args) < 2:
            print("Ошибка: укажите путь к файлу данных", file=sys.stderr)
            sys.exit(2)

        data_path = args[1]
        rules_path = None
        report_format = "console"

        i = 2
        while i < len(args):
            if args[i] == "--rules" and i + 1 < len(args):
                rules_path = args[i + 1]
                i += 2
            elif args[i] == "--report" and i + 1 < len(args):
                report_format = args[i + 1]
                i += 2
            else:
                i += 1

        if rules_path is None:
            print("Ошибка: укажите --rules <путь к rules.json>", file=sys.stderr)
            sys.exit(2)

        try:
            exit_code = run_check(data_path, rules_path, report_format)
            sys.exit(exit_code)
        except ValidatorError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        print(f"Неизвестная команда: {command}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()