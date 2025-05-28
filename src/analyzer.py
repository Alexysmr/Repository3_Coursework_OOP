import os
import re
from typing import Any
from src.config import DEFAULT_TOP_N, MAX_TOP_N, setup_logging

modul_name = os.path.basename(__file__)
logger = setup_logging(modul_name)


class Vacancy:
    """Класс создающий экземпляр вакансии с атрибутами: id, слово-запрос, name, url, salary, description, experience.
    Имеет методы: валидации стажа(experience), удаления 'нечитаемых' HTML-тегов из описания(description),
    валидации зарплаты (salary), валидации url, преобразование списка словарей данных с hh.ru в список экземпляров
    класса Vacancy, сравнения зарплаты экземпляров по значению (salary: "from"), репрезентации и преобразования
    вакансии в словарь"""

    __slots__ = ["id", "search_query", "name", "url", "salary", "description", "experience"]

    def __init__(
        self, id_number: str, search_query: str, name: str, url: str, salary: Any, description: str, experience: str
    ):
        self.id = id_number
        self.search_query = search_query.strip()
        self.name = name.strip()
        self.url = self._validate_url(url)
        self.salary = self._validate_salary(salary)
        self.description = self._clean_html(description) if description else "Описание отсутствует"
        self.experience = self._validate_experience(experience)

    @staticmethod
    def _validate_experience(exp: str) -> str:
        """метод валидации и корректировка параметра experience"""
        valid_experiences = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет"]
        return exp if exp in valid_experiences else "Не указан"

    @staticmethod
    def _clean_html(text: str) -> str:
        """Удаляет HTML-теги вида <highlighttext>, </highlighttext> из текста self.description"""
        return re.sub(r"<[^>]+>", "", text)

    @staticmethod
    def _validate_salary(salary: dict) -> dict:
        """Метод валидации зарплаты"""
        if (
            not salary
            or (salary.get("from") is None and salary.get("to") is None)
            or (salary.get("from") is None and not salary.get("to"))
            or (not salary.get("from") and salary.get("to") is None)
        ):
            return {"from": 0, "to": 0, "currency": " "}
        if salary.get("from") is None and salary.get("to"):
            return {"from": 0, "to": salary.get("to"), "currency": salary.get("currency")}
        if salary.get("to") is None and salary.get("from"):
            return {"from": salary.get("from"), "to": 0, "currency": salary.get("currency")}
        return salary

    @staticmethod
    def _validate_url(url: str) -> str:
        """Метод валидации url"""
        return url if url.startswith(("http://", "https://")) else "URL невалиден"

    @staticmethod
    def cast_to_object_list(hh_data: list[dict], search_query: str) -> list:
        """Преобразование списка словарей данных с hh.ru в список экземпляров класса Vacancy"""
        vacancies = []
        for i in hh_data:
            vacancy = Vacancy(
                i["id"],
                search_query,
                i["name"],
                i["url"],
                i["salary"],
                i["snippet"]["requirement"],
                i["experience"]["name"],
            )
            vacancies.append(vacancy)
        return vacancies

    def __gt__(self, other: Any) -> bool | Any:
        """Метод сравнения зарплаты по значению "from" """
        logger.info('Сортировка зарплаты "from"')
        return self.salary["from"] > other.salary["from"]

    def __repr__(self) -> str:
        """Метод репрезентации"""
        from_currency = f"{self.salary['from']} {self.salary['currency']}" if self.salary["from"] > 0 else "не указано"
        to_currency = f"{self.salary['to']} {self.salary['currency']}" if self.salary["to"] > 0 else "не указано"
        logger.info("Вывод в консоль произведён")
        return (
            f"Vacancy {self.search_query}\n"
            f"Должность, уровень: {self.name}\n"
            f"Зарплата от: {from_currency} до: {to_currency}\n"
            f"Требования: Стаж: {self.experience};\n            Опыт: {self.description})\n"
            f"Ссылка: {self.url}\n"
        )

    def to_dict(self) -> dict:
        """Возвращает вакансию в виде словаря."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "salary": self.salary,
            "description": self.description,
            "experience": self.experience,
        }


class VacancyAnalyzer:
    """Класс анализа и фильтрации по: стажу, топ n по зарплате, по ключевому слову в описании(description) и
    по диапазону зарплат"""

    logger.info("VacancyAnalyzer init")

    def __init__(self, vacancies: list[Vacancy]):
        self.vacancies = vacancies

    def filter_by_experience(self, experience: str | int) -> list[Vacancy] | list[Any]:
        """Фильтрация по стажу с поддержкой дробных значений"""
        logger.info(f"Фильтрация по стажу {experience} лет")
        experience_float = (
            abs(float(experience)) if (str(experience).replace(".", "", 1).isdigit()) else 0.0
        )  # Защита от формата "1.2.3"
        ranges = (
            (0.0, 1.0, "Нет опыта"),
            (1.0, 3.0, "От 1 года до 3 лет"),
            (3.0, 6.0, "От 3 до 6 лет"),
            (6.0, float("inf"), "Более 6 лет"),
        )

        for min_exp, max_exp, label in ranges:
            if min_exp <= experience_float < max_exp:
                return [v for v in self.vacancies if v.experience == label]
        return []

    def get_top_n(self, input_top_n: int | str) -> list[Vacancy] | list[Any]:
        """Топ-N вакансий по зарплате."""
        logger.info("Топ зарплат")
        top_n = max(1, abs(int(input_top_n))) if input_top_n.isdigit() else DEFAULT_TOP_N
        top_n = min(MAX_TOP_N, top_n)
        return sorted(self.vacancies, reverse=True)[:top_n]

    def filter_by_keyword(self, keyword: str) -> list[Vacancy] | list[Any]:
        """Фильтрация по ключевому слову в описании."""
        logger.info(f"Фильтрация по слову {keyword}")
        return [v for v in self.vacancies if keyword.lower() in v.description.lower()]

    def filter_by_salary(self, salary_input: str) -> list[Vacancy] | list[Any]:
        """Фильтрация по диапазону зарплат. Формат ввода: '100000-150000', '100000'
        salary['from'] ограничено 20% превышением от вводимой величины"""
        try:
            salary_range = salary_input.split("-")
            min_s = int(salary_range[0])
            if len(salary_range) < 2:
                return [v for v in self.vacancies if min_s <= v.salary["from"] <= int(min_s * 1.2)]
            if len(salary_range) >= 2:
                max_s = int(salary_range[1])
                return [
                    v
                    for v in self.vacancies
                    if min_s <= v.salary["from"] <= int(min_s * 1.2) and v.salary["to"] <= max_s
                ]
            return []
        except Exception as err:
            logger.warning(f"Ошибка {err}")
            return self.vacancies
