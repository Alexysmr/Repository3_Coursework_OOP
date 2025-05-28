import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_temp_dir():
    """Возвращает путь к папке temp в проекте. Создаёт её, если не существует."""
    temp_path = Path(__file__).parent / "temp"
    temp_path.mkdir(exist_ok=True)
    return temp_path


@pytest.fixture
def temp_dir(project_temp_dir):
    """Фикстура для временной директории"""
    return project_temp_dir


@pytest.fixture
def temp_file(project_temp_dir):
    """Фикстура для перезаписываемых файлов в tests/temp/."""

    def _create(filename: str, content: str = None):
        file_path = project_temp_dir / filename
        if content:
            file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create


@pytest.fixture
def mock_json_file(temp_dir):
    data = [{"id": "1", "name": "Python Developer"}]
    file_path = temp_dir / "hh.ru_Python.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path
