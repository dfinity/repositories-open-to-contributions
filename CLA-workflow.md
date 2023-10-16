# CLA workflow

## Background
DFINITY maintains a subset of repositories which accept external contributions. However, these contributors must first sign the [CLA document](https://github.com/dfinity/cla/blob/main/CLA.md) before their contributions will be accepted. This is standard practice for many open-source projects. Once they have signed the CLA document, they can automatically contribute to all repositories within the `dfinity` org accepting external contributions.

## Workflow
The workflow works as follows:
1. Check if the PR was created by someone outside the dfinity org (all PRs from dfinity org members can automatically be merged)
2. Check if the repository accepts external contributions. If not, the PR will automatically be closed with an automated message.
3. If the repository does accept external contributions, check if the user has already signed the CLA. All CLAs are collected as issues [here](https://github.com/dfinity/cla/issues).
4. If the CLA issue exists and has been signed, the PR can be merged. Otherwise:
    - check if an issue exists, if not, create one
    - if an issue exists but has not been signed, post a link to the issue and remind the user to sign it

The code for the CLA workflow is located [here](.github/workflows/check_cla.yml) and is (will be) applied to all repositories within the `dfinity` org by default. For issues or feedback feel free to contact the IDX team.