import json
import pytest

from src.analyzer import Vacancy, VacancyAnalyzer


def test_vacancy_creation():
    """Тест создания вакансии мануально"""
    vacancy = Vacancy(
        id_number="1",
        search_query="Python",
        name="Developer",
        url="http://example.com",
        salary={"from": 100000, "to": 150000, "currency": "RUB"},
        description="Описание",
        experience="От 1 до 3 лет",
    )
    assert vacancy.salary["from"] == 100000
    assert "Developer" in str(vacancy)


def test_vacancy_cast_to_object_list(temp_dir):
    """Тест функции преобразования сырых данных в список объектов класса Vacancy"""
    with open(temp_dir / "hh.ru_Python_for_tests.json", "r", encoding="utf-8") as f:
        data_json = json.load(f)
    vacancies_test = Vacancy.cast_to_object_list(data_json, "Python")
    assert len(vacancies_test) == 4


def test_vacancy_comparison():
    """Тест сравнения вакансий по зарплате"""
    v1 = Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "", "")
    v2 = Vacancy("2", "Python", "Dev", "url", {"from": 150000}, "", "")
    assert v2 > v1


def test_empty_salary():
    """Тест вакансии без указанной зарплаты"""
    vacancy = Vacancy("1", "Python", "Dev", "url", None, "", "")
    assert vacancy.salary["from"] == 0


def test_filter_by_salary_invalid_input():
    """Тест обработки ввода неверного формата зарплаты"""
    analyzer = VacancyAnalyzer([Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "desc", "exp")])

    result = analyzer.filter_by_salary("not-a-range")
    assert len(result) == 1


@pytest.mark.parametrize(
    "input_salary,expected",
    [
        ({}, {"from": 0, "to": 0, "currency": " "}),
        ({"from": 10000, "to": 100000, "currency": "RUR"}, {"from": 10000, "to": 100000, "currency": "RUR"}),
        ({"from": ""}, {"from": 0, "to": 0, "currency": " "}),
        ({"to": ""}, {"from": 0, "to": 0, "currency": " "}),
        ({"from": 100000}, {"from": 100000, "to": 0, "currency": None}),
        ({"to": 100000, "currency": "RUR"}, {"from": 0, "to": 100000, "currency": "RUR"}),
        ({"from": 10000, "to": 100000}, {"from": 10000, "to": 100000}),
        ({"from": 10000, "to": None, "currency": "RUR"}, {"from": 10000, "to": 0, "currency": "RUR"}),
    ],
)
def test_validate_salary(input_salary, expected):
    """Тест валидации зарплаты в разных вариациях данных"""
    assert Vacancy._validate_salary(input_salary) == expected


def test_filter_by_salary_approximately():
    """Тест по диапазону зарплат при отсутствии прямого совпадения, но с допуском +20%"""
    analyzer = VacancyAnalyzer(
        [
            Vacancy("1", "Python", "Dev", "url", {"from": 110000, "to": 120000}, "desc", "exp"),
            Vacancy("2", "Python", "Dev", "url", {"from": 90000, "to": 95000}, "desc", "exp"),
        ]
    )
    filtered = analyzer.filter_by_salary("100000")
    assert len(filtered) == 1
    assert filtered[0].salary["from"] == 110000


def test_filter_by_salary_range():
    """Тест корректности отбора по диапазону зарплат"""
    analyzer = VacancyAnalyzer(
        [
            Vacancy("1", "Python", "Dev", "url", {"from": 100000, "to": 150000}, "desc", "exp"),
            Vacancy("2", "Python", "Dev", "url", {"from": 200000, "to": 250000}, "desc", "exp"),
        ]
    )
    filtered = analyzer.filter_by_salary("100000-200000")
    assert len(filtered) == 1
    assert filtered[0].salary["from"] == 100000


def test_filter_by_experience_negative():
    """Тест корректности отбора по стажу"""
    analyzer = VacancyAnalyzer([Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "desc", "exp")])
    assert analyzer.filter_by_experience(3.0) == []


def test_filter_by_keyword():
    """Тест по ключевому слову"""
    analyzer = VacancyAnalyzer(
        [
            Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "Python developer", "exp"),
            Vacancy("2", "Java", "Dev", "url", {"from": 90000}, "Java developer", "exp"),
        ]
    )
    filtered = analyzer.filter_by_keyword("Python")
    assert len(filtered) == 1
    assert filtered[0].name == "Dev"
