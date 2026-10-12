import csv
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from validator.exceptions import DataFileError


class DataLoader(ABC):
    @abstractmethod
    def load(self, path: str) -> List[Dict[str, Any]]:
        pass


class CsvLoader(DataLoader):
    def load(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            raise DataFileError(f"Файл не найден: {path}")
        except csv.Error as e:
            raise DataFileError(f"Ошибка чтения CSV '{path}': {e}")


class JsonLoader(DataLoader):
    def load(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise DataFileError(f"Файл не найден: {path}")
        except json.JSONDecodeError as e:
            raise DataFileError(f"Битый JSON '{path}': {e}")

        if not isinstance(data, list):
            raise DataFileError(f"JSON в '{path}' должен быть списком объектов, получено: {type(data).__name__}")

        return data


# Фабрика загрузчиков по расширению
LOADERS_REGISTRY = {
    ".csv": CsvLoader,
    ".json": JsonLoader,
}


def get_loader(path: str) -> DataLoader:
    import os
    ext = os.path.splitext(path)[1].lower()
    if ext not in LOADERS_REGISTRY:
        raise DataFileError(f"Неизвестный формат файла: '{ext}'. Поддерживаются: {', '.join(LOADERS_REGISTRY.keys())}")
    return LOADERS_REGISTRY[ext]()
