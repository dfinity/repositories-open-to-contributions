import os

import github3

import messages


def is_member_of_org(gh, org, user):
    """
    Return whether the user is a member of the organisation.
    """
    return gh.organization(org).is_member(user)


class CLAHandler:
    def __init__(self, gh, org):
        self.cla_repo = gh.repository(owner=org, repository="cla")
        self.cla_file = "CLA.md"

    def cla_signed(self, issue, user):
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

    def get_cla_issue(self, user):
        for issue in self.cla_repo.issues():
            if issue.title == f"cla: @{user}":
                return issue
        print(f"No CLA issue for {user}")

    def create_cla_issue(self, user):
        cla_link = f"{self.cla_repo.html_url}/blob/main/{self.cla_file}"
        user_agreement_message = messages.USER_AGREEMENT_MESSAGE.format(user)
        issue = self.cla_repo.create_issue(
            f"cla: @{user}",
            body=messages.CLA_AGREEMENT_MESSAGE.format(
                user, cla_link, user_agreement_message
            ),
            labels=["cla:pending"],
        )
        return issue


def main():
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo = os.environ["REPO"]
    pr_id = os.environ["PR_ID"]

    gh = github3.login(token=gh_token)
    pr = gh.pull_request(org, repo, pr_id)
    user = pr.user.login

    #  is_member = is_member_of_org(gh, org, user)

    can_contribute = False

    cla = CLAHandler(gh, "dfinity")

    is_member = False

    if not is_member:
        print(f"{user} is an external contributor.")
        #      pr.issue().add_labels("external_contributor")
        issue = cla.get_cla_issue(user)
        if not issue:
            issue = cla.create_cla_issue(user)
            pr_comment = messages.CLA_MESSAGE.format(user, issue.html_url)
            pr.create_comment(pr_comment)

        if cla.cla_signed(issue, user):
            can_contribute = True
    else:
        print("User is member of org and can contribute.")
        can_contribute = True

    os.system(f"""echo 'can_contribute={can_contribute}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
