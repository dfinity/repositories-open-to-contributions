import os

import github3


def is_member_of_org(gh: github3.login, org: str, user: str) -> bool:
    """
    Return whether the user is a member of the organisation.
    """
    try:
        return gh.organization(org).is_member(user)
    except Exception as error:
        print(f"Failed with error: {error}")
        return False


def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    user = os.environ["USER"]

    gh = github3.login(token=gh_token)

    is_member = is_member_of_org(gh, org, user)

    if is_member:
        print(f"{user} is member of {org} and can contribute.")
    else:
        print(f"{user} is an external contributor.")

    os.system(f"""echo 'is_member={is_member}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
