import os

import github3

from check_cla_pr import CLAHandler


def main() -> None:
    gh_token = os.environ["GH_TOKEN"]
    issue_id = os.environ["ISSUE_ID"]

    gh = github3.login(token=gh_token)
    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    issue = gh.issue("dfinity", "cla", issue_id)
    user = issue.title.replace("cla: @", "")

    cla = CLAHandler(gh)

    cla_signed = cla.check_if_cla_signed(issue, user)
    if not cla_signed:
        cla.comment_on_issue(issue)
    else:
        cla.handle_cla_signed(issue, user)


if __name__ == "__main__":
    main()
