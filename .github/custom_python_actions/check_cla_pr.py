import os
import sys
from typing import Optional, TypeAlias

import github3

import messages

GHIssue: TypeAlias = github3.issues.issue.Issue
GHPullRequest: TypeAlias = github3.github.pulls.PullRequest
PENDING_LABEL = "cla:pending"
APPROVED_LABEL = "cla:agreed"
GH_WORKFLOW_LABEL = "cla:gh-wf-pending"

DFINITY_BOT_NAME = "sa-github-api"
DFINITY_BOT_NAME_OLD = "dfinity-droid-prod[bot]"


class CLAHandler:
    def __init__(self, gh: github3.login) -> None:
        self.cla_repo = gh.repository(owner="dfinity", repository="cla")
        self.cla_link = f"{self.cla_repo.html_url}/blob/main/CLA.md"

    def check_comment_already_exists(
        self, comments: github3.structs.GitHubIterator
    ) -> bool:
        for comment in comments:
            if comment.user.login == DFINITY_BOT_NAME:
                return True
        return False

    def comment_on_issue(self, issue: GHIssue):
        # check if bot has already left a message to avoid spam
        issue_comments = issue.comments()
        bot_comment = self.check_comment_already_exists(issue_comments)
        if not bot_comment:
            issue.create_comment(messages.FAILED_COMMENT)

    def comment_on_pr(self, pr: GHPullRequest, pr_comment):
        bot_comment = self.check_comment_already_exists(pr.issue_comments())
        if not bot_comment:
            pr.create_comment(pr_comment)

    def check_if_cla_signed(self, issue: GHIssue, user: str) -> bool:
        for comment in issue.comments():
            if comment.user.login == user:
                agreement_message = messages.USER_AGREEMENT_MESSAGE.format(user)
                comment_body = comment.body.strip()
                if comment_body == agreement_message:
                    print(f"CLA has been agreed to by {user}")
                    return True
                else:
                    print(f"Comment created by {user} does not match CLA agreement.")
        print(f"CLA is pending for {user}")
        return False

    def get_cla_issue(self, user: str) -> Optional[GHIssue]:
        for issue in self.cla_repo.issues():
            if issue.title == f"cla: @{user}" and issue.user.login in [
                DFINITY_BOT_NAME,
                DFINITY_BOT_NAME_OLD,
            ]:
                return issue
        print(f"No CLA issue for {user}")
        return None  # to make linter happy

    def create_cla_issue(self, user: str) -> GHIssue:
        user_agreement_message = messages.USER_AGREEMENT_MESSAGE.format(user)
        issue = self.cla_repo.create_issue(
            f"cla: @{user}",
            body=messages.CLA_AGREEMENT_MESSAGE.format(
                user, self.cla_link, user_agreement_message
            ),
        )
        # replace with PENDING, once new bot has been released
        issue.add_labels(GH_WORKFLOW_LABEL)
        return issue

    def handle_cla_signed(self, issue: GHIssue, user: str) -> None:
        for label in issue.original_labels:
            if label.name == APPROVED_LABEL:
                return
            elif label.name == GH_WORKFLOW_LABEL:
                agreement_message = messages.AGREED_MESSAGE.format(user)
                issue.create_comment(agreement_message)
                issue.remove_label(GH_WORKFLOW_LABEL)
                issue.add_labels(APPROVED_LABEL)
                return
        print(
            "No cla labels found - manually check the cla issue to see what state it is in. Exiting program."  # noqa
        )
        sys.exit(1)


def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo = os.environ["REPO"]
    pr_id = os.environ["PR_ID"]

    gh = github3.login(token=gh_token)
    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    pr = gh.pull_request(org, repo, pr_id)
    user = pr.user.login

    cla = CLAHandler(gh)

    issue = cla.get_cla_issue(user)
    if not issue:
        issue = cla.create_cla_issue(user)

    cla_signed = cla.check_if_cla_signed(issue, user)
    if cla_signed:
        print("CLA has been signed.")
    else:
        pr_comment = messages.CLA_MESSAGE.format(user, cla.cla_link, issue.html_url)
        cla.comment_on_pr(pr, pr_comment)
        print(
            f"The CLA has not been signed. Please sign the CLA agreement: {issue.html_url}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
