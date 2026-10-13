import csv
import json
import pytest
from validator.models import Violation, ValidationResult
from validator.reporters import JsonReporter, CsvReporter, MarkdownReporter


@pytest.fixture
def sample_result():
    """Создаёт тестовый результат с нарушениями."""
    result = ValidationResult(source="data/test.csv", rules_source="rules/test.json")
    result.total_records = 3
    result.add_violation(Violation(1, "email", "email", "bad@", "некорректный email"))
    result.add_violation(Violation(2, "name", "required", "", "обязательное поле пустое"))
    result.elapsed_time = 0.001
    return result


@pytest.fixture
def tmp_output(tmp_path):
    """Возвращает путь для временного файла отчёта."""
    return str(tmp_path / "report")


def test_json_reporter_creates_file(sample_result, tmp_output):
    reporter = JsonReporter()
    output_path = tmp_output + ".json"
    reporter.report(sample_result, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data["source"] == "data/test.csv"
    assert data["summary"]["records"] == 3
    assert data["summary"]["violations"] == 2
    assert len(data["violations"]) == 2


def test_csv_reporter_creates_file(sample_result, tmp_output):
    reporter = CsvReporter()
    output_path = tmp_output + ".csv"
    reporter.report(sample_result, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["field"] == "email"
    assert rows[1]["field"] == "name"


def test_markdown_reporter_creates_file(sample_result, tmp_output):
    reporter = MarkdownReporter()
    output_path = tmp_output + ".md"
    reporter.report(sample_result, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "# Отчёт валидации" in content
    assert "data/test.csv" in content
    assert "email" in content
    assert "name" in content