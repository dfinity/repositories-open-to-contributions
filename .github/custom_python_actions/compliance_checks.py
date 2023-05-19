import re
from dataclasses import dataclass
from typing import Optional


import github3


def get_code_owners(repo: github3.github.repo) -> str:
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
    return "not found"


def get_team_name(code_owners: str, org_name: str) -> str:
    code_owner_file = code_owners.strip("\n")
    regex_output = re.findall(
        # If anyone is a regex wizard, please help me out here!
        r"(?=^\*. *@).*(@\S*).*(@\S*)|(?=^\*. *@).*(@\S*)",
        code_owner_file,
        re.MULTILINE,
    )
    print(f"Codeowners found {regex_output}")
    if len(regex_output) == 0:
        raise Exception(
            "No repo-level team owner found. Double check the format of your CODEOWNERS file."
        )
    team_handle = [a for a in regex_output[0] if a != ""]
    if len(team_handle) > 1:
        raise Exception("Only one team can be listed for repo-level codeowners.")
    codeowner_team = team_handle[0].lower()
    team_name = codeowner_team.replace(f"@{org_name.lower()}/", "")
    return team_name


class ComplianceCheckHelper:
    def __init__(self, repo: github3.github.repo, org: github3.github.orgs):
        self.repo = repo
        self.org = org
        self.code_owners = None

    def get_code_owners(self) -> str:
        if not self.code_owners:
            self.code_owners = get_code_owners(self.repo)  # type: ignore
        return self.code_owners  # type: ignore


@dataclass
class ComplianceCheck:
    name: str
    succeeds: bool
    message: Optional[str]

    def check(self, helper: ComplianceCheckHelper) -> None:
        raise NotImplementedError()


@dataclass
class CodeOwners(ComplianceCheck):
    name: str = "code_owners"
    succeeds: bool = False
    message: Optional[str] = None

    def check(self, helper: ComplianceCheckHelper) -> None:
        try:
            code_owners_path = helper.get_code_owners()
        except Exception as error:
            self.message = f"Raised error: {error}"
            return

        if code_owners_path == "not found":
            self.message = "Codeowners file could not be found."
        elif code_owners_path != "not found":
            self.succeeds = True


@dataclass
class RepoPermissions(ComplianceCheck):
    name: str = "repo_permissions"
    succeeds: bool = False
    message: Optional[str] = None

    def check(self, helper: ComplianceCheckHelper) -> None:
        org = helper.org
        repo = helper.repo

        try:
            code_owners_path = helper.get_code_owners()
            team_name = get_team_name(code_owners_path, org.name)
        except Exception as error:
            self.message = f"Raised error: {error}"
            return

        try:
            team = org.team_by_name(team_name)
            permissions = team.permissions_for(f"{org.name}/{repo.name}")
            role = permissions.role_name
        except github3.exceptions.NotFoundError:
            self.message = "Repository Permissions could not be found"
            return
        except Exception as error:
            self.message = f"Raised error: {error}"
            return

        if role in ["maintain", "write"]:
            self.succeeds = True
            self.message = f"Team {team_name} has {role} permissions."
        else:
            self.message = f"Insufficient permissions. Requires write or maintain, but team {team_name} has {role}."  # noqa: E501


@dataclass
class BranchProtection(ComplianceCheck):
    name: str = "branch_protection"
    succeeds: bool = False
    message: Optional[str] = None

    def check(self, helper: ComplianceCheckHelper):
        repo = helper.repo
        branch = repo.branch(repo.default_branch)

        self.succeeds = branch.protected


@dataclass
class License(ComplianceCheck):
    name: str = "license"
    succeeds: bool = False
    message: Optional[str] = None

    def check(self, helper: ComplianceCheckHelper):
        try:
            helper.repo.license()
            self.succeeds = True
        except github3.exceptions.NotFoundError:
            self.message = "No license file found"
        except Exception as error:
            self.message = f"Raised error: {error}"


@dataclass
class Readme(ComplianceCheck):
    name: str = "readme"
    succeeds: bool = False
    message: Optional[str] = None

    def check(self, helper: ComplianceCheckHelper):
        try:
            helper.repo.readme()
            self.succeeds = True
        except github3.exceptions.NotFoundError:
            self.message = "No README found"
        except Exception as error:
            self.message = f"Raised error: {error}"
