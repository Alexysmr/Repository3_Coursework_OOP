from os.path import exists

import requests
import pytest
from unittest.mock import Mock, patch
from src.api_client import HHAPIClient


def test_hh_api_client(mocker, temp_dir):
    # Мокаем requests.get
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"items": [{"id": "1", "name": "Python"}]}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.get", return_value=mock_response)

    # Тестируем
    client = HHAPIClient("Python", file_path=temp_dir)
    result = client.get_vacancies("Python")

    assert client.area == 1
    assert "hh.ru_Python.json" in str(client.filename)
    requests.get.assert_called()
    assert len(result) == 3
    assert result[0]["id"] == "1"

def test_hh_api_client_all_pages_empty(mocker, temp_dir):
    mock_response_empty = mocker.Mock()
    mock_response_empty.json.return_value = {"items": []}
    mock_get = mocker.patch("requests.get", return_value=mock_response_empty)

    client = HHAPIClient("Python_empty", file_path=temp_dir)
    result = client.get_vacancies("Python_empty", pages=3)
    assert len(result) == 0
    assert mock_get.call_count == 2
