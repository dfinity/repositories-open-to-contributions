import os
from pathlib import Path
import sys
from unittest import mock

import pytest

SCRIPT_DIR = file = f"{Path(__file__).parents[1]}/custom_python_actions/"
print(SCRIPT_DIR)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from custom_python_actions.check_external_contrib import (
    get_repos_open_to_contributions,
    main,
)  # noqa


def test_check_repos_open_to_contributions():
    gh = mock.Mock()
    gh_repo = mock.Mock()
    file_contents = mock.Mock()
    file_contents.decoded.decode.return_value = "one-repo\nanother-repo\n"
    gh_repo.file_contents.return_value = file_contents
    gh.repository.return_value = gh_repo

    repo_list = get_repos_open_to_contributions(gh)

    assert repo_list == ["one-repo", "another-repo"]
    gh.repository.assert_called_with(
        owner="dfinity", repository="repositories-open-to-contributions"
    )


@mock.patch.dict(os.environ, {"REPO": "repo-1", "GH_TOKEN": "token"})
@mock.patch("github3.login")
@mock.patch("os.system")
def test_end_to_end(os_system, github_login_mock):
    gh = mock.Mock()
    repo = mock.Mock()
    gh.repository.return_value = repo
    file_contents = mock.Mock()
    file_contents.decoded.decode.return_value = "repo-1\nrepo-2\n"
    repo.file_contents.return_value = file_contents
    github_login_mock.return_value = gh

    main()

    os_system.assert_called_with("echo 'accepts_contrib=True' >> $GITHUB_OUTPUT")


@mock.patch.dict(os.environ, {"REPO": "my_org", "GH_TOKEN": ""})
@mock.patch("github3.login")
def test_github_token_not_passed_in(github_login_mock):
    github_login_mock.return_value = None

    with pytest.raises(Exception) as exc:
        main()

    assert str(exc.value) == "GH_TOKEN not correctly set"
