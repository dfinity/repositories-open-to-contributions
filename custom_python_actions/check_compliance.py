import os

import github3


def check_code_owners(repo: github3.github.repo) -> bool:
    valid_codowner_paths = [
        "/CODEOWNERS",
        "/.github/CODEOWNERS",
    ]
    for path in valid_codowner_paths:
        try:
            repo.file_contents(path)
            return True
        except github3.exceptions.NotFoundError:
            pass
    return False


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


def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo_name = os.environ["REPO"]

    gh = github3.login(token=gh_token)
    try:
        repo = gh.repository(owner=org, repository=repo_name)
    except github3.exceptions.NotFoundError as e:
        raise Exception(
            f"Github repo {repo_name} not found. Double check the spelling and that your repository is public."  # noqa
        ) from e

    has_codeowners = check_code_owners(repo)
    has_readme = check_readme(repo)
    has_license = check_license(repo)
    is_branch_protected = check_branch_protection(repo)

    os.system(f"""echo 'has_codeowners={has_codeowners}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'has_readme={has_readme}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'has_license={has_license}' >> $GITHUB_OUTPUT""")
    os.system(f"""echo 'is_branch_protected={is_branch_protected}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
