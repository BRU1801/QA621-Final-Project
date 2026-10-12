import csv
import json
import os
from abc import ABC, abstractmethod
from validator.models import ValidationResult
from validator.exceptions import ReportError


class Reporter(ABC):
    @abstractmethod
    def report(self, result: ValidationResult, output_path: str):
        pass


class ConsoleReporter(Reporter):
    def report(self, result: ValidationResult, output_path: str = ""):
        print(f"Проверка {result.source} по правилам {result.rules_source}")
        print()
        for v in sorted(result.violations):
            print(v)
        print()
        s = result.to_dict()["summary"]
        print(f"Итого: записей {s['records']}, без ошибок {s['valid']}, "
              f"с ошибками {s['invalid']}, нарушений {s['violations']}")
        if result.elapsed_time:
            print(f"Время проверки: {result.elapsed_time} сек.")


class JsonReporter(Reporter):
    def report(self, result: ValidationResult, output_path: str):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)


class CsvReporter(Reporter):
    def report(self, result: ValidationResult, output_path: str):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["record_no", "field", "rule", "value", "message"])
            writer.writeheader()
            for v in sorted(result.violations):
                writer.writerow({
                    "record_no": v.record_no,
                    "field": v.field,
                    "rule": v.rule,
                    "value": v.value if v.value is not None else "",
                    "message": v.message,
                })


class MarkdownReporter(Reporter):
    def report(self, result: ValidationResult, output_path: str):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Отчёт валидации\n\n")
            f.write(f"**Источник:** {result.source}\n\n")
            f.write(f"**Правила:** {result.rules_source}\n\n")
            f.write(f"## Нарушения\n\n")
            f.write("| Запись | Поле | Правило | Значение | Сообщение |\n")
            f.write("|--------|------|---------|----------|-----------|\n")
            for v in sorted(result.violations):
                val = v.value if v.value is not None else ""
                f.write(f"| {v.record_no} | {v.field} | {v.rule} | {val} | {v.message} |\n")
            f.write("\n")
            s = result.to_dict()["summary"]
            f.write(f"## Сводка\n\n")
            f.write(f"- Всего записей: {s['records']}\n")
            f.write(f"- Без ошибок: {s['valid']}\n")
            f.write(f"- С ошибками: {s['invalid']}\n")
            f.write(f"- Нарушений: {s['violations']}\n")
            if result.elapsed_time:
                f.write(f"- Время проверки: {result.elapsed_time} сек.\n")


# Реестр репортёров
REPORTERS_REGISTRY = {
    "console": ConsoleReporter,
    "json": JsonReporter,
    "csv": CsvReporter,
    "md": MarkdownReporter,
}


def get_reporter(format_name: str) -> Reporter:
    if format_name not in REPORTERS_REGISTRY:
        raise ReportError(f"Неизвестный формат отчёта: '{format_name}'. "
                          f"Поддерживаются: {', '.join(REPORTERS_REGISTRY.keys())}")
    return REPORTERS_REGISTRY[format_name]()
