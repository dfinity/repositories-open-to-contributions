import os
from unittest import mock

import pytest

from custom_python_actions.messages import (
    AGREED_MESSAGE,
    CLA_AGREEMENT_MESSAGE,
    USER_AGREEMENT_MESSAGE,
)
from custom_python_actions.check_cla import CLAHandler, main


def test_init():
    gh = mock.Mock()
    cla_repo = mock.Mock()
    cla_repo.html_url = "repo_url"
    gh.repository.return_value = cla_repo

    cla = CLAHandler(gh)

    assert cla.cla_repo == cla_repo
    assert cla.cla_link == "repo_url/blob/main/CLA.md"
    gh.repository.assert_called_with(owner="dfinity", repository="cla")


def test_cla_is_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    comment.user.login = "username"
    agreement_message = USER_AGREEMENT_MESSAGE.format("username")
    comment.body = agreement_message
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response == True
    assert out == "CLA has been agreed to by username\n"


def test_cla_is_incorrectly_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    comment.user.login = "username"
    comment.body = "incorrect message"
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response == False
    assert (
        out
        == "Comment created by username does not match CLA agreement.\nCLA is pending for username\n"
    )


def test_cla_is_not_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    comment.user.login = "bot"
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response == False
    assert out == "CLA is pending for username\n"


def test_get_cla_issue_success():
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    issue.title = "cla: @username"
    cla_repo.issues.return_value = [mock.Mock(), issue]
    cla.cla_repo = cla_repo

    assert issue == cla.get_cla_issue("username")


def test_get_cla_issue_fails(capfd):
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    issue.title = "cla: @another-username"
    cla_repo.issues.return_value = [mock.Mock(), issue]
    cla.cla_repo = cla_repo

    assert cla.get_cla_issue("username") == None
    out, err = capfd.readouterr()
    assert out == "No CLA issue for username\n"


def test_create_cla_issue():
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    cla_repo.create_issue.return_value = issue
    cla.cla_repo = cla_repo
    cla.cla_link = "cla_repo_link"
    user_agreement_message = USER_AGREEMENT_MESSAGE.format("username")
    cla_agreement_message = CLA_AGREEMENT_MESSAGE.format(
        "username", cla.cla_link, user_agreement_message
    )

    new_issue = cla.create_cla_issue("username")

    assert new_issue == issue
    cla_repo.create_issue.assert_called_with(
        "cla: @username", body=cla_agreement_message, labels=["cla:pending"]
    )
