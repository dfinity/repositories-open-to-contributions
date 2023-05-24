import io
import sys
from unittest import mock

import pytest
from github3.exceptions import NotFoundError

from custom_python_actions.compliance_checks import (
    BranchProtection,
    CodeOwners,
    ComplianceCheckHelper,
    get_code_owners,
    get_team_name,
    License,
    Readme,
    RepoPermissions,
)


def test_get_code_owners_succeeds():
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


def test_get_code_owners_fails():
    repo = mock.Mock()
    repo.file_contents = mock.Mock(
        side_effect=[NotFoundError(mock.Mock()), NotFoundError(mock.Mock())]
    )

    code_owners = get_code_owners(repo)

    assert repo.file_contents.call_count == 2
    repo.file_contents.assert_has_calls(
        [mock.call("/.github/CODEOWNERS"), mock.call("/CODEOWNERS")], any_order=True
    )
    assert code_owners == "not found"


def code_owners_test_file(n):
    code_owners = open(f".github/tests/test_data/CODEOWNERS{n}", "r").read()
    return code_owners


@pytest.mark.parametrize(
    "test_input,org_name,expected",
    [
        (code_owners_test_file(1), "dfinity", "idx"),
        (code_owners_test_file(2), "another-org", "another-team"),
        (code_owners_test_file(3), "dfinity-lab", "some-team"),
        (code_owners_test_file(8), "dfinity", "trust"),
    ],
)
def test_get_team_name_succeeds(test_input, org_name, expected):
    team_name = get_team_name(test_input, org_name)

    assert team_name == expected


too_many_teams_message = "Only one team can be listed for repo-level codeowners."
no_repo_owner_message = (
    "No repo-level team owner found. Double check the format of your CODEOWNERS file."
)


@pytest.mark.parametrize(
    "test_input,org_name,message",
    [
        (code_owners_test_file(4), "dfinity", too_many_teams_message),
        (code_owners_test_file(5), "dfinity", no_repo_owner_message),
        (code_owners_test_file(6), "dfinity", no_repo_owner_message),
        (code_owners_test_file(7), "dfinity", no_repo_owner_message),
    ],
)
def test_get_team_name_fails(test_input, org_name, message):
    with pytest.raises(Exception):
        capturedOutput = io.StringIO()
        get_team_name(test_input, org_name)
        sys.stdout = capturedOutput

        assert capturedOutput.getvalue() == message


@mock.patch(
    "custom_python_actions.compliance_checks.get_code_owners", return_value="code_path"
)
def test_compliance_check_helper_code_owners_not_set(get_code_owners_mock):
    repo = mock.Mock()
    org = mock.Mock()
    helper = ComplianceCheckHelper(repo, org)

    helper.get_code_owners()

    get_code_owners_mock.assert_called_once()
    get_code_owners_mock.assert_called_with(repo)
    assert helper.repo == repo
    assert helper.org == org
    assert helper.code_owners == "code_path"


@mock.patch(
    "custom_python_actions.compliance_checks.get_code_owners", return_value="code_path"
)
def test_compliance_check_helper_code_owners_set(get_code_owners_mock):
    helper = ComplianceCheckHelper(mock.Mock(), mock.Mock())
    helper.code_owners = "another_path"

    helper.get_code_owners()

    get_code_owners_mock.assert_not_called()
    assert helper.code_owners == "another_path"


def test_check_code_owners_succeeds():
    helper = mock.Mock()
    helper.get_code_owners.return_value = "* @dfinity/idx\n"
    code_owners_check = CodeOwners()

    code_owners_check.check(helper)

    assert code_owners_check.succeeds == True
    assert code_owners_check.name == "code_owners"
    assert code_owners_check.message == None


def test_check_code_owners_fails_not_found():
    helper = mock.Mock()
    helper.get_code_owners.return_value = "not found"
    code_owners_check = CodeOwners()

    code_owners_check.check(helper)

    assert code_owners_check.succeeds == False
    assert code_owners_check.message == "Codeowners file could not be found."


def test_check_code_owners_fails_other_error():
    helper = mock.Mock()
    helper.get_code_owners.side_effect = Exception("some other error")
    code_owners_check = CodeOwners()

    code_owners_check.check(helper)

    assert code_owners_check.succeeds == False
    assert code_owners_check.message == "Raised error: some other error"


def test_branch_protection_enabled():
    helper = mock.Mock()
    repo = mock.Mock()
    repo.default_branch = "main"
    branch = mock.Mock()
    branch.protected = True
    helper.repo.branch.return_value = branch
    branch_protection_check = BranchProtection()

    branch_protection_check.check(helper)

    assert repo.branch.called_with("main")
    assert branch_protection_check.name == "branch_protection"
    assert branch_protection_check.succeeds == True


def test_branch_protection_disabled():
    helper = mock.Mock()
    repo = mock.Mock()
    repo.default_branch = "main"
    branch = mock.Mock()
    branch.protected = False
    helper.repo.branch.return_value = branch
    branch_protection_check = BranchProtection()

    branch_protection_check.check(helper)

    assert repo.branch.called_with("main")
    assert branch_protection_check.succeeds == False


def test_check_license_exists():
    repo = mock.Mock()
    repo.license.return_value = "license"
    helper = mock.Mock()
    helper.repo = repo
    license_check = License()

    license_check.check(helper)

    assert license_check.succeeds == True
    assert license_check.name == "license"


def test_check_license_is_missing():
    repo = mock.Mock()
    repo.license.side_effect = NotFoundError(mock.Mock())
    helper = mock.Mock()
    helper.repo = repo
    license_check = License()

    license_check.check(helper)

    assert license_check.succeeds == False
    assert license_check.message == "No license file found"


def test_check_license_other_error():
    repo = mock.Mock()
    repo.license.side_effect = Exception("some exception")
    helper = mock.Mock()
    helper.repo = repo
    license_check = License()

    license_check.check(helper)

    assert license_check.succeeds == False
    assert license_check.message == "Raised error: some exception"


def test_check_readme_exists():
    repo = mock.Mock()
    repo.readme.return_value = "readme"
    helper = mock.Mock()
    helper.repo = repo
    readme_check = Readme()

    readme_check.check(helper)

    assert readme_check.succeeds == True
    assert readme_check.name == "readme"


def test_check_readme_is_missing():
    repo = mock.Mock()
    repo.readme.side_effect = NotFoundError(mock.Mock())
    helper = mock.Mock()
    helper.repo = repo
    readme_check = Readme()

    readme_check.check(helper)

    assert readme_check.succeeds == False


def test_check_readme_other_error():
    repo = mock.Mock()
    repo.readme.side_effect = Exception("some exception")
    helper = mock.Mock()
    helper.repo = repo
    readme_check = Readme()

    readme_check.check(helper)

    assert readme_check.succeeds == False
    assert readme_check.message == "Raised error: some exception"


@mock.patch(
    "custom_python_actions.compliance_checks.get_team_name", return_value="my_team"
)
def test_repo_permissions_succesds(get_team_name_mock):
    org = mock.Mock()
    org.name = "my_org"
    repo = mock.Mock()
    repo.name = "my_repo"
    permissions = mock.Mock()
    permissions.role_name = "maintain"
    team = mock.Mock()
    team.permissions_for.return_value = permissions
    org.team_by_name.return_value = team
    helper = mock.Mock()
    helper.get_code_owners.return_value = "code_owners_path"
    helper.repo = repo
    helper.org = org
    repo_permissions_check = RepoPermissions()

    repo_permissions_check.check(helper)

    assert repo_permissions_check.name == "repo_permissions"
    assert repo_permissions_check.succeeds == True
    org.team_by_name.assert_called_with("my_team")
    team.permissions_for.assert_called_with("my_org/my_repo")
    get_team_name_mock.assert_called_with("code_owners_path", "my_org")


@mock.patch(
    "custom_python_actions.compliance_checks.get_team_name", return_value="my_team"
)
def test_repo_permissions_team_name_not_found(get_team_name_mock):
    org = mock.Mock()
    org.name = "my_org"
    helper = mock.Mock()
    helper.get_code_owners.return_value = "code_owners_path"
    helper.repo = mock.Mock()
    helper.org = org
    get_team_name_mock.side_effect = Exception(
        "Only one team can be listed for repo-level codeowners."
    )
    repo_permissions_check = RepoPermissions()

    repo_permissions_check.check(helper)
    assert repo_permissions_check.succeeds == False
    assert (
        repo_permissions_check.message
        == "Raised error: Only one team can be listed for repo-level codeowners."
    )
