#!/bin/bash

set -euo pipefail

# Integration test to ensure CI succeeds on a compliant repository

commit_sha="$(git rev-parse HEAD)"
branch_name="$(git rev-parse --abbrev-ref HEAD)"
curl -L -X POST -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/workflows/check_new_repo.yml/dispatches -d '{"ref":"'"$branch_name"'","inputs":{"repo-name":"test-compliant-repository"}}'

# check CI
while true
do
    sleep 3
    status=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=$branch_name | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .status')
    echo "$status"
    if [[ "$status" == '"completed"' ]]
    then
        break
    fi
done
result=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=$branch_name | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .conclusion')
if [[ "$result" == '"success"' ]]
    then echo "test passed"
else
    echo "test failed, expected Check New Repo to result in success but got $result" >&2
    git push origin -d integration-test-compliant-repo-$RUN_NUMBER
    exit 1
fi