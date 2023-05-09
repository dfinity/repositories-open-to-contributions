import os
import sys
from typing import Optional, TypeAlias

import github3

import messages

GHIssue: TypeAlias = github3.issues.issue.Issue
PENDING_LABEL = "cla:pending"
APPROVED_LABEL = "cla:approved"


class CLAHandler:
    def __init__(self, gh: github3.login, org: str) -> None:
        self.cla_repo = gh.repository(owner=org, repository="cla")
        self.cla_link = f"{self.cla_repo.html_url}/blob/main/CLA.md"

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
                    print(
                        "Double check that the sentence has been copied exactly, including punctuation."  # noqa
                    )
        print(f"CLA is pending for {user}")
        return False

    def get_cla_issue(self, user: str) -> Optional[GHIssue]:
        for issue in self.cla_repo.issues():
            if issue.title == f"cla: @{user}":
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
            labels=[PENDING_LABEL],
        )
        return issue

    def handle_cla_signed(self, issue: GHIssue, user: str) -> None:
        for label in issue.original_labels:
            if label.name == APPROVED_LABEL:
                return
            elif label.name == PENDING_LABEL:
                agreement_message = messages.AGREED_MESSAGE.format(user)
                issue.create_comment(agreement_message)
                issue.remove_label(PENDING_LABEL)
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
    pr = gh.pull_request(org, repo, pr_id)
    user = pr.user.login

    cla = CLAHandler(gh, "dfinity")

    issue = cla.get_cla_issue(user)
    if not issue:
        issue = cla.create_cla_issue(user)
        pr_comment = messages.CLA_MESSAGE.format(user, cla.cla_link, issue.html_url)
        pr.create_comment(pr_comment)

    cla_signed = cla.check_if_cla_signed(issue, user)
    if cla_signed:
        cla.handle_cla_signed(issue, user)

    else:
        print(
            f"The CLA has not been signed. Please sign the CLA agreement: {issue.html_url}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
