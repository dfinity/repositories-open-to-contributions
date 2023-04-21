#!/bin/bash

# Integration test to ensure CI fails when a non-existent repository is added

# set git credentials
# git config user.name github-actions[bot]
# git config user.email github-actions[bot]@users.noreply.github.com
git config user.name dfinity
git config user.email dfinity@dfinity.org
# git config user.password $GH_TOKEN

gh auth login
gh auth setup-git

# create new branch
git checkout -b integration-test-1

# add a fake repository
echo "fake-repository" >> open-repositories.txt
git add open-repositories.txt
git commit -m 'add nonexistent repository'

# create pull request
git push --set-upstream origin integration-test-1
gh pr create --draft --title "Integration Test 1" --body "generated by integration test"

commit_sha=$(git rev-parse HEAD)

# check CI
while true
do
    status=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=integration-test-1 | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .status')
    echo $status
    if [[ $status == '"completed"' ]]
    then
        break
    fi
done
result=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=integration-test-1 | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | | map(select(.head_sha=='\"$commit_sha\"')) | max_by(.run_number) | .conclusion')
if [[ $result == '"failure"' ]]
    echo $result
    then echo "test passed"
else
    echo "test failed, expected Check New Repo to result in failure but got $result"
fi

# delete branch and close PR
#git push origin -d integration-test-1