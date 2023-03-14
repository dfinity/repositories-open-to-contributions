import os
import time
from typing import List

import github3


def download_gh_file(repo: github3.github.repo, file_path: str) -> str:
    # sometimes the request does not work the first time, so set a retry
    for attempt in range(5):
        try:
            file_content = repo.file_contents(file_path)
            break
        except ConnectionResetError as error:
            if attempt < 4:
                time.sleep(3)
                continue
            else:
                # if it hasn't succeeded after 5 tries, raise the error
                raise Exception(
                    "Error downloading data. Try rerunning the CI job"
                ) from error

    file_decoded = file_content.decoded.decode()
    return file_decoded


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

    repo_list = get_repos_open_to_contributions(gh)
    accepts_contrib = repo in repo_list

    os.system(f"""echo 'accepts_contrib={accepts_contrib}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
