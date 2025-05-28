import json
import os
from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod
from fileinput import filename

import pandas as pd

from src.analyzer import Vacancy
from src.config import DATA_DIR, DEFAULT_JSON_FILE, setup_logging

modul_name = os.path.basename(__file__)
logger = setup_logging(modul_name)


class AbstractStorage(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        pass


class JSONSaver(AbstractStorage):
    """Класс чтения, сохранения, добавления, удаления"""

    def __init__(self, filename: str = DEFAULT_JSON_FILE, file_path: Path = DATA_DIR) -> None:
        self.file_path = file_path
        self._filename = self.file_path / f"{filename}_processed.json"

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавление вакансии с проверкой на дубликаты по id"""
        logger.info("Старт")
        data = self._load_data()
        if not any(v["id"] == vacancy.id for v in data):
            data.append(vacancy.to_dict())
            logger.info("Вакансии на дубликаты проверены и добавлены в файл")
            self._save_data(data)

    def _load_data(self) -> list[dict] | Any:
        """Открытие файла данных"""
        logger.info("Старт")
        if not self._filename.exists():
            logger.info(f"Файл {filename}_processed.json не обнаружен")
            return []
        with open(self._filename, "r", encoding="utf-8") as f:
            logger.info("Файл прочитан и возвращён")
            return json.load(f)

    def _save_data(self, data: list[dict]) -> None:
        """Сохранение данных в файлы в форматах JSON и XLSX"""
        logger.info("Старт")
        with open(self._filename, "w", encoding="utf-8") as f:
            logger.info(f"Файл {self._filename} сохранён")
            json.dump(data, f, indent=4, ensure_ascii=False)
            excel_path = self._filename.parent / f"{self._filename.stem}.xlsx"
            logger.info(f"Файл {self._filename.stem}.xlsx сохранён")
            pd.DataFrame(data).to_excel(excel_path, index=False)

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаляет вакансию из файла по id"""
        logger.info("Старт")
        data = self._load_data()
        data = [v for v in data if v["id"] != vacancy.id]
        logger.info(f"Вакансия id:{vacancy.id} исключена")
        self._save_data(data)
