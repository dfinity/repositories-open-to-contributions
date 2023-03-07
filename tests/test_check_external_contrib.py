import base64
from unittest import mock

import pytest

from custom_python_actions.check_external_contrib import download_file, decode_file


@mock.patch("requests.get")
def test_download_file_succeeds_first_try(mock_get):
    data_response = {"content": "file_contents", "encoding": "base64"}
    response_mock = mock.MagicMock()
    response_mock.json.return_value = data_response
    mock_get.return_value = response_mock

    data = download_file("some_url")

    assert data == data_response
    assert mock_get.call_count == 1


@pytest.mark.slow
@mock.patch("requests.get")
def test_download_file_succeeds_third_try(mock_get):
    data_response = {"content": "file_contents", "encoding": "base64"}
    response_mock = mock.MagicMock()
    response_mock.json.side_effect = [{}, {}, data_response]
    mock_get.return_value = response_mock

    data = download_file("some_url")

    assert data == data_response
    assert mock_get.call_count == 3


@pytest.mark.slow
@mock.patch("requests.get")
def test_download_file_fails(mock_get):
    response_mock = mock.MagicMock()
    response_mock.json.return_value = {}
    mock_get.return_value = response_mock

    with pytest.raises( (KeyError, Exception) ):
        download_file("some_url")

    assert mock_get.call_count == 5


def test_decode_file():
    data_response = {"content": "file_contents", "encoding": "base64"}
    data_response["content"] = base64.b64encode("file_contents".encode("ascii"))

    file_content = decode_file(data_response)

    assert "file_contents" == file_content


def test_file_not_decoded():
    data_response = {"content": "file_contents"}
    data_response["content"] = base64.b64encode("file_contents".encode("ascii"))

    file_content = decode_file(data_response)

    assert data_response["content"] == file_content
