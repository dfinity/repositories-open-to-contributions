import base64
import os
import time
from typing import Dict, List, NoReturn, Union

import requests


def download_file(url: str) -> Union[Dict, NoReturn]:
    s = requests.Session()

    # sometimes the request does not work the first time, so set a retry
    for attempt in range(5):
        x = s.get(url)
        data = x.json()
        try:
            data["content"]
            data["encoding"]
            break
        except KeyError as error:
            if attempt < 4:
                time.sleep(3)
                continue
            else:
                # if it hasn't succeeded after 5 tries, raise the error
                raise error
    return data


def decode_file(data: Dict) -> str:
    file_content = data["content"]
    if data.get("encoding") == "base64":
        file_content = base64.b64decode(file_content).decode()
    return file_content


def get_repos_open_to_contributions() -> List[str]:
    owner = "dfinity"
    repo_name = "repositories-open-to-contributions"
    file_path = "open-repositories.txt"
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"

    data = download_file(url)
    file_content = decode_file(data)

    # convert .txt file to list
    repo_list = file_content.split("\n")
    repo_list.remove("")
    return repo_list


def main() -> None:
    repo = os.environ["REPO"]

    repo_list = get_repos_open_to_contributions()
    accepts_contrib = repo in repo_list

    os.system(f"""echo 'accepts_contrib={accepts_contrib}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
