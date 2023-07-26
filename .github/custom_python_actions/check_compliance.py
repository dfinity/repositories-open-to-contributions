import os
import sys

import github3

from compliance_checks import (
    BranchProtection,
    ComplianceCheckHelper,
    CodeOwners,
    License,
    Readme,
    RepoPermissions,
)


def main() -> None:
    org_name = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo_name = os.environ["REPO"]

    gh = github3.login(token=gh_token)
    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    try:
        repo = gh.repository(owner=org_name, repository=repo_name)
        org = gh.organization(username=org_name)
    except github3.exceptions.NotFoundError as e:
        raise Exception(
            f"Github repo {repo_name} not found. Double check the spelling and that your repository is public."  # noqa
        ) from e

    checks_passed = True
    for compliance_check in [
        BranchProtection(),
        CodeOwners(),
        License(),
        Readme(),
        RepoPermissions(),  # Repo Permissions needs to be after CodeOwners
    ]:
        helper = ComplianceCheckHelper(repo, org)
        print(f"Checking {compliance_check.name}")
        compliance_check.check(helper)
        if compliance_check.succeeds:
            print("Check succeeded")
        else:
            print("Check failed")
            checks_passed = False
        if compliance_check.message is not None:
            print(compliance_check.message)
    if not checks_passed:
        print("One or more checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
