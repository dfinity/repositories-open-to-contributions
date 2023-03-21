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
)


def test_check_code_owners_succeeds():
    repo = mock.Mock()
    code_owners_file = "* @dfinity/idx\n"
    repo.file_contents = mock.Mock(
        side_effect=[NotFoundError(mock.Mock()), code_owners_file]
    )

    code_owners_check = check_code_owners(repo)

    assert repo.file_contents.call_count == 2
    repo.file_contents.assert_has_calls(
        [mock.call("/.github/CODEOWNERS"), mock.call("/CODEOWNERS")], any_order=True
    )
    assert code_owners_check == True


def test_check_code_owners_fails():
    repo = mock.Mock()
    repo.file_contents = mock.Mock(
        side_effect=[NotFoundError(mock.Mock()), NotFoundError(mock.Mock())]
    )

    code_owners_check = check_code_owners(repo)

    assert repo.file_contents.call_count == 2
    repo.file_contents.assert_has_calls(
        [mock.call("/.github/CODEOWNERS"), mock.call("/CODEOWNERS")], any_order=True
    )
    assert code_owners_check == False


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
    repo = mock.Mock()
    repo.readme.side_effect = Exception("some exception")
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    with pytest.raises(Exception):
        readme = check_readme(repo)


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
