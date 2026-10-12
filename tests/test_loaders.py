import pytest
from validator.loaders import CsvLoader, JsonLoader, get_loader
from validator.exceptions import DataFileError


def test_csv_loader_loads_valid_file(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age\nАнна,25\nБорис,30\n", encoding='utf-8')

    loader = CsvLoader()
    data = loader.load(str(csv_file))

    assert len(data) == 2
    assert data[0]["name"] == "Анна"
    assert data[1]["age"] == "30"


def test_csv_loader_file_not_found():
    loader = CsvLoader()
    with pytest.raises(DataFileError) as exc_info:
        loader.load("nonexistent.csv")
    assert "не найден" in str(exc_info.value)


def test_json_loader_loads_valid_file(tmp_path):
    json_file = tmp_path / "test.json"
    json_file.write_text('[{"id": 1, "name": "Анна"}, {"id": 2, "name": "Борис"}]', encoding='utf-8')

    loader = JsonLoader()
    data = loader.load(str(json_file))

    assert len(data) == 2
    assert data[0]["id"] == 1


def test_json_loader_file_not_found():
    loader = JsonLoader()
    with pytest.raises(DataFileError):
        loader.load("nonexistent.json")


def test_json_loader_not_a_list(tmp_path):
    json_file = tmp_path / "bad.json"
    json_file.write_text('{"name": "Анна"}', encoding='utf-8')

    loader = JsonLoader()
    with pytest.raises(DataFileError) as exc_info:
        loader.load(str(json_file))
    assert "должен быть списком" in str(exc_info.value)


def test_get_loader_csv():
    loader = get_loader("data.csv")
    assert isinstance(loader, CsvLoader)


def test_get_loader_json():
    loader = get_loader("data.json")
    assert isinstance(loader, JsonLoader)


def test_get_loader_unknown_format():
    with pytest.raises(DataFileError) as exc_info:
        get_loader("data.xml")
    assert "Неизвестный формат" in str(exc_info.value)