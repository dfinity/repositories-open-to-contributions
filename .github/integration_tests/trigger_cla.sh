#!/bin/bash

set -euo pipefail

CURRENT_BRANCH=${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}

curl \
-X POST \
-H "Accept: application/vnd.github.v3+json" \
-H "Authorization: token $AUTH_TOKEN" \
https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/workflows/check_cla.yml/dispatches \
-d '{"ref":"'"$CURRENT_BRANCH"'", "inputs":{"user":"dfinity"}}'

while true
do
    sleep 3
    status=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $AUTH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=$CURRENT_BRANCH | jq '[.workflow_runs[] | select(.name=="Check CLA")] | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .status')
    echo $status
    if [[ $status == '"completed"' ]]
    then
        break
    fi
done
result=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $AUTH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=$CURRENT_BRANCH | jq '[.workflow_runs[] | select(.name=="Check CLA")] | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .conclusion')

## we expect this to fail because no PR was created and it cannot close the PR
## However, it is enough to know that the Close PR step failed

if [[ $result == '"failure"' ]]
    then echo "test passed"
else
    echo "test failed, expected Check CLA to result in failure but got $result" >&2
    exit 1
fi