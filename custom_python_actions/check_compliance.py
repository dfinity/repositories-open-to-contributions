import os
import re
import sys
from typing import Union

import github3


def get_code_owners(repo: github3.github.repo) -> Union[str, None]:
    valid_codowner_paths = [
        "/CODEOWNERS",
        "/.github/CODEOWNERS",
    ]
    for path in valid_codowner_paths:
        try:
            code_owners_file = repo.file_contents(path)
            code_owners = code_owners_file.decoded.decode()
            return code_owners
        except github3.exceptions.NotFoundError:
            pass
    return None


def check_code_owners(repo: github3.github.repo) -> bool:
    return True if get_code_owners(repo) else False


def check_branch_protection(repo: github3.github.repo) -> bool:
    branch = repo.branch(repo.default_branch)
    return branch.protected


def check_license(repo: github3.github.repo) -> bool:
    try:
        repo.license()
        return True
    except github3.exceptions.NotFoundError:
        return False


def check_readme(repo: github3.github.repo) -> bool:
    try:
        repo.readme()
        return True
    except github3.exceptions.NotFoundError:
        return False


def get_team_name(code_owners: str, org_name: str) -> str:
    code_owner_file = code_owners.strip("\n")
    regex_output = re.findall(
        # If anyone is a regex wizard, please help me out here!
        r"(?=\*. *@).*(@\S*).*(@\S*)|(?=\*. *@).*(@\S*)",
        code_owner_file,
    )
    print(f"Codeowners found {regex_output}")
    if len(regex_output) == 0:
        print(
            "No repo-level team owner found. Double check the format of your CODEOWNERS file."
        )
        sys.exit(1)
    team_handle = [a for a in regex_output[0] if a != ""]
    if len(team_handle) > 1:
        print("Only one team can be listed for repo-level codeowners.")
        sys.exit(1)
    codeowner_team = team_handle[0]
    team_name = codeowner_team.strip(f"@{org_name}").strip("/")

    return team_name


def check_permissions(repo_name: str, team_name: str, org: github3.github.orgs) -> bool:
    try:
        role = (
            org.team_by_name(team_name)
            .permissions_for(f"{org.name}/{repo_name}")
            .role_name
        )
    except github3.exceptions.NotFoundError:
        print("Repository Permissions could not be found")
        return False

    if role in ["admin", "write"]:
        print(f"Team {team_name} has {role} permissions.")
        return True
    else:
        print(
            f"Insufficient permissions. Requires write or admin, but team {team_name} has {role}."
        )
        return False


def main() -> None:
    org_name = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo_name = os.environ["REPO"]

    gh = github3.login(token=gh_token)
    try:
        repo = gh.repository(owner=org_name, repository=repo_name)
        org = gh.organization(username=org_name)
    except github3.exceptions.NotFoundError as e:
        raise Exception(
            f"Github repo {repo_name} not found. Double check the spelling and that your repository is public."  # noqa
        ) from e

    has_codeowners = check_code_owners(repo)
    has_readme = check_readme(repo)
    has_license = check_license(repo)
    is_branch_protected = check_branch_protection(repo)

    if has_codeowners:
        code_owners = get_code_owners()
        team_name = get_team_name(code_owners, org_name)
        has_permissions = check_permissions(repo_name, team_name, org)
    else:
        has_permissions = False

    os.system(f"""echo 'has_codeowners={has_codeowners}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'has_readme={has_readme}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'has_license={has_license}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'is_branch_protected={is_branch_protected}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'has_permissions={has_permissions}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
