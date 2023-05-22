import os
from unittest import mock

from custom_python_actions.check_cla_issue import main
from custom_python_actions.messages import USER_AGREEMENT_MESSAGE


@mock.patch.dict(
    os.environ,
    {"GH_TOKEN": "secret", "ISSUE_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("custom_python_actions.check_cla_issue.CLAHandler")
def test_end_to_end_cla_signed(cla_mock, gh_login_mock):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    issue = mock.Mock()
    issue.title = "cla: @username"
    comment = mock.Mock()
    comment.user.login = "username"
    agreement_message = USER_AGREEMENT_MESSAGE.format("username")
    comment.body = agreement_message
    issue.comments.return_value = [mock.Mock(), comment]
    label = mock.Mock()
    label.name = "cla:agreed"
    issue.original_labels = [label]
    gh.issue.return_value = issue
    cla = mock.Mock()
    cla_mock.return_value = cla

    main()

    cla.check_if_cla_signed.assert_called_with(issue, "username")
    cla.comment_on_issue.assert_not_called()
    cla.handle_cla_signed.assert_called_once()


@mock.patch.dict(
    os.environ,
    {"GH_TOKEN": "secret", "ISSUE_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("custom_python_actions.check_cla_issue.CLAHandler")
def test_end_to_end_cla_not_signed(cla_mock, gh_login_mock):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    issue = mock.Mock()
    issue.title = "cla: @username"
    gh.issue.return_value = issue
    cla = mock.Mock()
    cla_mock.return_value = cla
    cla.check_if_cla_signed.return_value = False

    main()

    cla.check_if_cla_signed.assert_called_with(issue, "username")
    cla.comment_on_issue.assert_called_once()
    cla.handle_cla_signed.assert_not_called()
