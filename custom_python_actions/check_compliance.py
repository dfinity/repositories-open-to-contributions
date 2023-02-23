import os

import github3
import requests


def check_code_owners(repo: github3.github.repo) -> bool:
    repo_url = repo.html_url + f"/blob/{repo.default_branch}"
    valid_codowner_paths = [
        "/CODEOWNERS",
        "/.github/CODEOWNERS",
        "/.gitlab/CODEOWNERS",
    ]
    for path in valid_codowner_paths:
        x = requests.head(repo_url + path, allow_redirects=True)
        if x.status_code >= 200 and x.status_code < 300:
            return True
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
    except Exception as error:
        print(f"Raised error: {error}")
        return False


def check_readme(repo: github3.github.repo) -> bool:
    try:
        repo.readme()
        return True
    except github3.exceptions.NotFoundError:
        return False
    except Exception as error:
        print(f"Raised error: {error}")
        return False


def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    repo = os.environ["REPO"]

    gh = github3.login(token=gh_token)
    repo = gh.repository(owner=org, repository=repo)

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
