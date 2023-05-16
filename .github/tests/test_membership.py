import os
from unittest import mock

from custom_python_actions.check_membership import main


@mock.patch.dict(
    os.environ, {"GH_ORG": "my_org", "GH_TOKEN": "secret", "USER": "username"}
)
@mock.patch("github3.login")
def test_end_to_end(github_login_mock, capfd):
    gh = mock.Mock()
    gh.organization.is_member.return_value = True
    github_login_mock.return_value = gh

    main()
    out, err = capfd.readouterr()

    github_login_mock.assert_called_with(token="secret")
    gh.organization.assert_called_with("my_org")
    gh.organization().is_member.assert_called_with("username")
    assert out == "username is member of my_org and can contribute.\n"
