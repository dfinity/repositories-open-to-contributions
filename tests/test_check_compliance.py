import io
import sys
from unittest import mock

import pytest
from github3.exceptions import NotFoundError

from custom_python_actions.check_compliance import (
    check_branch_protection,
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
    code_owners = "* @dfinity/idx\n"

    check_succeeds = check_code_owners(code_owners)

    assert check_succeeds == True


def test_check_code_owners_fails():
    code_owners = None

    check_succeeds = check_code_owners(code_owners)

    assert check_succeeds == False


def test_check_license_exists():
    repo = mock.Mock()
    repo.license.return_value = "license"

    license = check_license(repo)

    assert license == True


def test_check_license_is_missing():
    repo = mock.Mock()
    repo.license.side_effect = NotFoundError(mock.Mock())

    license = check_license(repo)

    assert license == False


def test_check_license_other_error():
    repo = mock.Mock()
    repo.license.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    with pytest.raises(Exception):
        readme = check_license(repo)


def test_check_readme_exists():
    repo = mock.Mock()
    repo.readme.return_value = "readme"

    readme = check_readme(repo)

    assert readme == True


def test_check_readme_is_missing():
    repo = mock.Mock()
    repo.readme.side_effect = NotFoundError(mock.Mock())

    readme = check_readme(repo)

    assert readme == False


def test_check_readme_other_error():
    repo = mock.Mock()
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


code_owners_test_file_4 = "* @dfinity/idx @dfinity/another-team \n"
code_owners_test_file_5 = "/build/logs/ @doctocat"
code_owners_test_file_6 = "*.js    @js-owner #This is an inline comment."

too_many_teams_message = "Only one team can be listed for repo-level codeowners."
no_repo_owner_message = (
    "No repo-level team owner found. Double check the format of your CODEOWNERS file."
)


@pytest.mark.parametrize(
    "test_input,org_name,message",
    [
        (code_owners_test_file_4, "dfinity", too_many_teams_message),
        (code_owners_test_file_5, "dfinity", no_repo_owner_message),
        (code_owners_test_file_6, "dfinity", no_repo_owner_message),
    ],
)
def test_get_team_name_fails(test_input, org_name, message):
    with pytest.raises(SystemExit):
        capturedOutput = io.StringIO()
        get_team_name(test_input, org_name)
        sys.stdout = capturedOutput

        assert capturedOutput.getvalue() == message

def test_branch_protection_enabled():
    repo = mock.Mock()
    repo.default_branch = "main"
    branch = mock.Mock()
    branch.protected = True
    repo.branch.return_value = branch

    branch_protection = check_branch_protection(repo)

    assert repo.branch.called_with("main")
    assert branch_protection == True


def test_branch_protection_disabled():
    repo = mock.Mock()
    repo.default_branch = "main"
    branch = mock.Mock()
    branch.protected = False
    repo.branch.return_value = branch

    branch_protection = check_branch_protection(repo)

    assert repo.branch.called_with("main")
    assert branch_protection == False
