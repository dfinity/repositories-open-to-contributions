import io
import sys
from unittest import mock

from github3.exceptions import NotFoundError

from custom_python_actions.check_compliance import (
    check_code_owners,
    check_license,
    check_readme,
)


@mock.patch("requests.head")
def test_check_code_owners_succeeds(mock_head):
    repo = mock.MagicMock()
    repo.html_url = "github_url"
    repo.default_branch = "main"

    response = mock.MagicMock()
    response.status_code = 200
    mock_head.return_value = response

    code_owners_check = check_code_owners(repo)

    mock_head.assert_called_with(
        "github_url/blob/main/CODEOWNERS", allow_redirects=True
    )
    assert code_owners_check == True


@mock.patch("requests.head")
def test_check_code_owners_fails(mock_head):
    repo = mock.MagicMock()
    repo.html_url = "github_url"
    repo.default_branch = "main"
    response = mock.MagicMock()
    response.status_code = 404
    mock_head.return_value = response

    code_owners_check = check_code_owners(repo)

    assert code_owners_check == False


def test_check_license_exists():
    repo = mock.MagicMock()
    repo.license.return_value = "license"

    license = check_license(repo)

    assert license == True


def test_check_license_is_missing():
    repo = mock.MagicMock()
    repo.license.side_effect = NotFoundError

    license = check_license(repo)

    assert license == False


def test_check_license_other_error():
    repo = mock.MagicMock()
    repo.license.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    license = check_license(repo)
    sys.stdout = sys.__stdout__

    assert license == False
    assert capturedOutput.getvalue() == "Raised error: some exception\n"


def test_check_readme_exists():
    repo = mock.MagicMock()
    repo.readme.return_value = "readme"

    readme = check_readme(repo)

    assert readme == True


def test_check_readme_is_missing():
    repo = mock.MagicMock()
    repo.readme.side_effect = NotFoundError

    readme = check_readme(repo)

    assert readme == False


def test_check_readme_other_error():
    repo = mock.MagicMock()
    repo.readme.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    readme = check_readme(repo)
    sys.stdout = sys.__stdout__

    assert readme == False
    assert capturedOutput.getvalue() == "Raised error: some exception\n"
