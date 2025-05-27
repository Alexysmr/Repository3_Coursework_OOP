from pathlib import Path
import logging

# Пути к файлам
BASE_DIR = Path(__file__).resolve().parent.parent  # Корень проекта
DATA_DIR = BASE_DIR / "data"                       # Директория с данными
LOGS_DIR = BASE_DIR / "logs"                       # Директория с логами

# Настройки API HH.ru
HH_API_URL = "https://api.hh.ru/vacancies"
HH_API_HEADERS = {"User-Agent": "MyVacancyParser/1.0 (alexxsmr@yandex.ru)"}
HH_API_AREA = 1  # Код региона по умолчанию (1 — Москва)
CACHE_EXPIRE_HOURS = 1  # Время существования файла 'сырых' данных
PAGES = 3  # Количество запрашиваемых страниц
PER_PAGE = 100  # Количество строк на странице

DEFAULT_TOP_N = 10   # Количество Топ-n вакансий по умолчанию
MAX_TOP_N = 50   # Максимальное количество Топ-n вакансий

# Настройки файлов
DEFAULT_JSON_FILE = "vacancies"  # Имя файла по умолчанию для сохранения отфильтрованных данных

# Логирование
LOG_FORMAT = "%(asctime)s | %(levelname)s %(name)s, def: %(funcName)s, line:%(lineno)d, inf: %(message)s"


def setup_logging(logger_name: str):
    """Централизованная конфигурация логирования для всего проекта"""
    log_filename = f"{logger_name.split('.')[0]}.log"
    log_filepath = LOGS_DIR / log_filename
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    file_handler = logging.FileHandler(log_filepath, "w", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    return logger
