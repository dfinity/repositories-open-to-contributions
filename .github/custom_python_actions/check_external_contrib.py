import os
from typing import List

import github3

from utils import download_gh_file


def get_repos_open_to_contributions(gh: github3.login) -> List[str]:
    org = "dfinity"
    repo_name = "repositories-open-to-contributions"
    file_path = "open-repositories.txt"

    repo = gh.repository(owner=org, repository=repo_name)

    file_content = download_gh_file(repo, file_path)

    # convert .txt file to list
    repo_list = file_content.split("\n")
    repo_list.remove("")
    return repo_list


def main() -> None:
    repo = os.environ["REPO"]
    gh_token = os.environ["GH_TOKEN"]

    gh = github3.login(token=gh_token)

    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    repo_list = get_repos_open_to_contributions(gh)
    accepts_contrib = repo in repo_list

    os.system(f"""echo 'accepts_contrib={accepts_contrib}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
