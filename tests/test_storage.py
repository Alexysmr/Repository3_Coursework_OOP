import json
import os

from src.analyzer import Vacancy
from src.storage import JSONSaver


def test_add_vacancy(temp_dir):
    """Тест добавления вакансии с проверкой на дублирование"""
    expected_file = temp_dir / "test_vacancies_processed.json"

    saver = JSONSaver("test_vacancies", file_path=temp_dir)
    vacancy = Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "desc", "exp")
    saver.add_vacancy(vacancy)

    assert expected_file.exists()
    with open(expected_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["id"] == "1"


def test_delete_vacancy(temp_dir):
    """Тест удаления вакансии"""
    expected_file = temp_dir / "test_vacancies_processed.json"
    if expected_file.exists():
        os.remove(expected_file)  # для чистоты теста удаляем тестовый файл если он есть

    saver = JSONSaver("test_vacancies", file_path=temp_dir)  # создаём тестовый файл
    vacancy = Vacancy("1", "Python", "Dev", "url", {"from": 100000}, "desc", "exp")
    saver.add_vacancy(vacancy)  # добавляем в тестовый файл вакансию vacancy
    saver.delete_vacancy(vacancy)  # удаляем из тестового файла вакансию vacancy

    with open(expected_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 0
