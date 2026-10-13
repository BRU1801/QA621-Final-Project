import functools
import time
import logging
import os

LOG_DIR = "reports"
LOG_FILE = os.path.join(LOG_DIR, "runs.log")


def timed(func):
    """Декоратор для замера времени выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        if hasattr(result, 'elapsed_time'):
            result.elapsed_time = round(elapsed, 3)
        return result
    return wrapper


def log_run(func):
    """Декоратор: пишет строку о каждом запуске в reports/runs.log."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] Запуск: {func.__name__}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
        return func(*args, **kwargs)
    return wrapper
