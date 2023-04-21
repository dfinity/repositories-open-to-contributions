#!/bin/bash

# Integration test to ensure CI fails when a non-existent repository is added

# git config --global user.name "dfinity"

git config user.name github-actions[bot]
git config user.email github-actions[bot]@users.noreply.github.com
git config user.password "$GH_TOKEN"

# create new branch
git checkout -b integration-test-1

echo "checked out branch"

# add a fake repository
echo "fake-repository" >> open-repositories.txt
git add open-repositories.txt
git commit -m 'add nonexistent repository'

echo "committed to repo"

# create pull request
#git remote add origin "https://$GH_TOKEN@github.com/dfinity/repositories-open-to-contributions.git"
git push --set-upstream origin integration-test-1
hub pull-request --draft -m 'Integration Test 1'

echo "made it to the end"

# # check CI
# while true
# do
#     status=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=integration-test-1 | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | max_by(.run_number) | .status')
#     if [[ $status == '"completed"' ]]
#     then
#         break
#     fi
# done
# result=$(curl -L -H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GH_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"   https://api.github.com/repos/dfinity/repositories-open-to-contributions/actions/runs?branch=integration-test-1 | jq '[.workflow_runs[] | select(.name=="Check New Repo")] | max_by(.run_number) | .conclusion')
# if [[ $result == '"failure"' ]]
#     then echo "test passed"
# else
#     echo "test failed, expected Check New Repo to result in failure but got $result"
# fi

# delete branch and close PR
# git push origin -d integration-test-1