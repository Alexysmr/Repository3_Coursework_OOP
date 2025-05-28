import json
import os
from typing import Any
from datetime import datetime
from pathlib import Path

from src.api_client import HHAPIClient
from src.config import CACHE_EXPIRE_HOURS, DATA_DIR, setup_logging

modul_name = os.path.basename(__file__)
logger = setup_logging(modul_name)


def check_exist_data(search_query: str, file_path: Path | None = None, filename: str | None = None) -> list[dict[Any, Any]] | Any:
    """Проверяет существование файла с данными соответствующих запросу и, если он существует менее часа, читает его,
    либо производится обращение к классу HHAPIClient(см. Докстринг), чтение новых данных и их возвращение
     в формате JSON"""
    logger.info(f"Старт.Ключевое слово запроса: {search_query}")
    file_path = file_path if file_path else DATA_DIR
    filename = filename if filename else f"hh.ru_{search_query}.json"
    data_file = file_path / filename
    if (
        data_file.exists()
        and ((datetime.now() - datetime.fromtimestamp(data_file.stat().st_mtime)).seconds / 3600) < CACHE_EXPIRE_HOURS
    ):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Ошибка чтения файла, запрашиваем новые данные")
            return HHAPIClient(search_query).get_vacancies(search_query)
    logger.info(f"Создаём новый файл по запросу {search_query}")
    HHAPIClient(search_query)
    with open(data_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        return json_data
