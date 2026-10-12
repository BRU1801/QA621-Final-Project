class ValidatorError(Exception):
    """Базовое исключение для всех ошибок валидатора."""
    pass

class DataFileError(ValidatorError):
    """Ошибка чтения или формата файла с данными."""
    pass

class ConfigError(ValidatorError):
    """Ошибка в конфигурации правил (rules.json)."""
    pass

class ReportError(ValidatorError):
    """Ошибка при генерации или сохранении отчёта."""
    pass
