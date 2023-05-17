import os
from unittest import mock

from github3.exceptions import NotFoundError
import pytest

from custom_python_actions.check_membership import main


@mock.patch.dict(
    os.environ, {"GH_ORG": "my_org", "GH_TOKEN": "secret", "USER": "username"}
)
@mock.patch("github3.login")
@mock.patch("os.system")
def test_end_to_end_is_member(os_system, github_login_mock, capfd):
    gh = mock.Mock()
    gh_org = mock.Mock()
    gh.organization.return_value = gh_org
    gh_org.is_member.return_value = True
    github_login_mock.return_value = gh

    main()
    out, err = capfd.readouterr()

    github_login_mock.assert_called_with(token="secret")
    gh.organization.assert_called_with("my_org")
    gh_org.is_member.assert_called_with("username")
    assert out == "username is member of my_org and can contribute.\n"
    os_system.assert_called_once_with("echo 'is_member=True' >> $GITHUB_OUTPUT")


@mock.patch.dict(
    os.environ, {"GH_ORG": "my_org", "GH_TOKEN": "secret", "USER": "username"}
)
@mock.patch("github3.login")
@mock.patch("os.system")
def test_end_to_end_is_not_member(os_system, github_login_mock, capfd):
    gh = mock.Mock()
    gh_org = mock.Mock()
    gh.organization.return_value = gh_org
    gh_org.is_member.return_value = False
    github_login_mock.return_value = gh

    main()
    out, err = capfd.readouterr()

    github_login_mock.assert_called_with(token="secret")
    gh.organization.assert_called_with("my_org")
    gh_org.is_member.assert_called_with("username")
    assert out == "username is an external contributor.\n"
    os_system.assert_called_once_with("echo 'is_member=False' >> $GITHUB_OUTPUT")


@mock.patch.dict(
    os.environ, {"GH_ORG": "my_org", "GH_TOKEN": "secret", "USER": "username"}
)
@mock.patch("github3.login")
@mock.patch("os.system")
def test_end_to_end_api_fails(os_system, github_login_mock, capfd):
    gh = mock.Mock()
    gh_org = mock.Mock()
    gh.organization.return_value = gh_org
    gh_org.is_member.side_effect = NotFoundError(mock.Mock())
    github_login_mock.return_value = gh

    with pytest.raises(NotFoundError):
        main()
        out, err = capfd.readouterr()
        os_system.assert_not_called()
        assert out == ""
