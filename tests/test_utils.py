import os
from datetime import datetime, timedelta
from unittest.mock import patch
from src.utils import check_exist_data
from src.config import CACHE_EXPIRE_HOURS


def test_check_exist_data_with_fresh_cache(monkeypatch, temp_dir, mock_json_file):
    mock_json_file
    # Меняем время модификации файла на текущее
    new_time = datetime.now().timestamp()
    monkeypatch.setattr("os.path.getmtime", lambda _: new_time)

    # Мокаем HHAPIClient.get_vacancies, чтобы он возвращал тестовые данные
    with patch("src.utils.HHAPIClient") as mock_client:
        mock_client.return_value.get_vacancies.return_value = [{"id": "1"}]  # pages здесь не передаётся, используется значение по умолчанию
        result = check_exist_data("Python", temp_dir)
    assert len(result) == 1


def test_check_exist_data_with_expired_cache(temp_dir):
    search_query = "Python"
    expired_file = temp_dir / f"test_cashe_hh.ru_{search_query}.json"
    expired_file.write_text('[{"id": "1"}]')

    old_time = datetime.now() - timedelta(hours=CACHE_EXPIRE_HOURS + 1)
    os.utime(expired_file, (old_time.timestamp(), old_time.timestamp()))

    with patch("src.utils.HHAPIClient") as mock_client:
        mock_client.return_value.get_vacancies.return_value = [{"id": "1"}]
        result = check_exist_data(search_query, temp_dir, f"test_cashe_hh.ru_{search_query}.json")

    assert result == [{"id": "1"}]
    mock_client.assert_called_once_with(search_query)
