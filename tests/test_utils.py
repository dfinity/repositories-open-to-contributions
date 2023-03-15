from unittest import mock

import pytest

from custom_python_actions.utils import download_gh_file


def test_download_file_succeeds_first_try():
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    file_content_obj.decoded = b"file_contents"
    repo.file_contents.return_value = file_content_obj

    data = download_gh_file(repo, "file_path")

    assert data == "file_contents"
    assert repo.file_contents.called_with("file_path")
    assert repo.file_contents.call_count == 1


@pytest.mark.slow
def test_download_file_succeeds_third_try():
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    file_content_obj.decoded = b"file_contents"
    repo.file_contents = mock.Mock(
        side_effect=[ConnectionResetError, ConnectionResetError, file_content_obj]
    )

    data = download_gh_file(repo, "file_path")

    assert data == "file_contents"
    assert repo.file_contents.called_with("file_path")
    assert repo.file_contents.call_count == 3


@pytest.mark.slow
@mock.patch("requests.get")
def test_download_file_fails(mock_get):
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    repo.file_contents = mock.Mock(side_effect=ConnectionResetError)

    with pytest.raises((ConnectionResetError, Exception)):
        download_gh_file(repo, "file_path")

    assert repo.file_contents.call_count == 5
    file_content_obj.decoded.assert_not_called
