import json
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from src.config import HH_API_URL, HH_API_HEADERS, HH_API_AREA, PAGES, PER_PAGE, DATA_DIR, setup_logging

modul_name = os.path.basename(__file__)
logger = setup_logging(modul_name)


class AbstractAPIClient(ABC):
    @abstractmethod
    def get_vacancies(self, search_query: str) -> list[dict]:
        pass


class HHAPIClient(AbstractAPIClient):
    """Класс создаёт файл с полученными по запросу данными о вакансиях. В сценарий по умолчанию заложено:
    3 последовательных запроса страниц с 0 по 2 с 100 вакансиями на страницу. Все полученные 'сырые' данные
    записываются в файл. В случае возникновения ошибок в получении данных с сайта выбрасывается исключение"""

    logger.info("Старт api-клиента")
    BASE_URL = HH_API_URL

    def __init__(self, search_query: str, area: int = None, page: int = 0, per_page: int = PER_PAGE,
                 file_path: Path | None = None, filename: str | None = None):
        self.area = area if area else HH_API_AREA
        self._page = page
        self.per_page = per_page
        self.headers = HH_API_HEADERS
        self.file_path = file_path if file_path else DATA_DIR
        self.filename = f"hh.ru_{filename}.json" if filename else f"hh.ru_{search_query}.json"
        logger.info("Инициализатор")
        self.get_vacancies(search_query)

    def get_vacancies(self, search_query: str, pages: int = PAGES) -> list | None:
        """Получение списка вакансий по ключевому слову-запросу"""
        data_file = self.file_path / self.filename
        json_data = []
        logger.info(f"Старт запроса {search_query}")
        base_params = {"text": search_query,
                       "area": self.area,
                       "per_page": self.per_page}
        try:
            delay = 0.5 if pages >= 20 else 0.1  # уважаем чужой API
            for i in range(pages):
                current_params = {**base_params, "page": i}
                response = requests.get(self.BASE_URL, params=current_params,
                                        headers=self.headers)  # Передаём заголовки
                response.raise_for_status()
                items = response.json().get("items", [])
                if not items:
                    logger.info(f"Страница {i} пуста, завершаем сбор")
                    break
                json_data.extend(items)
                logger.info(f"Получена страница {i}, вакансий: {len(items)}")
                if i < pages - 1:
                    time.sleep(delay)
            logger.info(f"Всего собрано вакансий: {len(json_data)}")
            with open(data_file, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
                logger.info(f"Файл данных по запросу \"{search_query}\" создан")
                return json_data
        except requests.exceptions.RequestException as err:
            logger.warning(f"Ошибка запроса: {err}")
            print(f"Ошибка запроса: {err}")
