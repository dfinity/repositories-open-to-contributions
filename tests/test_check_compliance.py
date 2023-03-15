import io
import sys
from unittest import mock

import pytest
from github3.exceptions import NotFoundError

from custom_python_actions.check_compliance import (
    check_code_owners,
    check_license,
    check_readme,
    get_code_owners,
    get_team_name,
)


def test_check_get_code_owners_succeeds():
    repo = mock.Mock()
    code_owners_file = mock.Mock()
    code_owners_file.decoded.decode.return_value = "* @dfinity/idx\n"
    repo.file_contents = mock.Mock(
        side_effect=[NotFoundError(mock.Mock()), code_owners_file]
    )

    code_owners = get_code_owners(repo)

    assert repo.file_contents.call_count == 2
    assert code_owners_file.decoded.decode.call_count == 1
    repo.file_contents.assert_has_calls(
        [mock.call("/.github/CODEOWNERS"), mock.call("/CODEOWNERS")], any_order=True
    )
    assert code_owners == "* @dfinity/idx\n"


def test_check_get_code_owners_fails():
    repo = mock.Mock()
    repo.file_contents = mock.Mock(
        side_effect=[NotFoundError(mock.Mock()), NotFoundError(mock.Mock())]
    )

    code_owners = get_code_owners(repo)

    assert repo.file_contents.call_count == 2
    repo.file_contents.assert_has_calls(
        [mock.call("/.github/CODEOWNERS"), mock.call("/CODEOWNERS")], any_order=True
    )
    assert code_owners == None


def test_check_code_owners_succeeds():
    repo = mock.Mock()
    code_owners_file = mock.Mock()
    code_owners_file.decoded.decode.return_value = "* @dfinity/idx\n"
    repo.file_contents.return_value = code_owners_file

    check_succeeds = check_code_owners(repo)

    assert repo.file_contents.call_count == 1
    assert check_succeeds == True


def test_check_code_owners_fails():
    repo = mock.Mock()
    repo.file_contents.side_effect = NotFoundError(mock.Mock())

    check_succeeds = check_code_owners(repo)

    assert repo.file_contents.call_count == 2
    assert check_succeeds == False


def test_check_license_exists():
    repo = mock.MagicMock()
    repo.license.return_value = "license"

    license = check_license(repo)

    assert license == True


def test_check_license_is_missing():
    repo = mock.MagicMock()
    repo.license.side_effect = NotFoundError(mock.Mock())

    license = check_license(repo)

    assert license == False


def test_check_license_other_error():
    repo = mock.MagicMock()
    repo.license.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    with pytest.raises(Exception):
        readme = check_license(repo)


def test_check_readme_exists():
    repo = mock.MagicMock()
    repo.readme.return_value = "readme"

    readme = check_readme(repo)

    assert readme == True


def test_check_readme_is_missing():
    repo = mock.MagicMock()
    repo.readme.side_effect = NotFoundError(mock.Mock())

    readme = check_readme(repo)

    assert readme == False


def test_check_readme_other_error():
    repo = mock.MagicMock()
    repo.readme.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    with pytest.raises(Exception):
        readme = check_readme(repo)


code_owners_test_file_1 = "* @dfinity/idx\n"
code_owners_test_file_2 = "* @another-org/another-team # some comment"


def code_owners_test_file_3():
    code_owners = open("tests/test_data/CODEOWNERS3", "r").read()
    return code_owners


@pytest.mark.parametrize(
    "test_input,org_name,expected",
    [
        (code_owners_test_file_1, "dfinity", "idx"),
        (code_owners_test_file_2, "another-org", "another-team"),
        (code_owners_test_file_3(), "dfinity-lab", "some-team"),
    ],
)
def test_get_team_name_succeeds(test_input, org_name, expected):
    team_name = get_team_name(test_input, org_name)

    assert team_name == expected
