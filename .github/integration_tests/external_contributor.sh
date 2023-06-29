#!/bin/bash

set -euo pipefail

# Integration test to ensure CLA closes PR for an external contributor

# set git credentials
git config user.name dfinity
git config user.email dfinity@dfinity.org

# get updates for forked repo
git fetch upstream
git checkout -b integration-test-3
git merge upstream/master integration-test-3

# create new branch with commit
touch test.txt
git add test.txt
git commit --author="dfinity <dfinity@dfinity.org>" -m 'add empty file'

# create pull request
git remote -v
git push --set-upstream origin integration-test-3
gh auth login --with-token <<< $AUTH_TOKEN
gh pr create --repo dfinity/repositories-open-to-contributions --base master --head dfinity-sandbox/repositories-open-to-contributions:integration-test-3 --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
git push origin -d integration-test-3

#gh pr create --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
#gh pr create --base dfinity/repositories-open-to-contributions:master --head dfinity-sandox/repositories-open-to-contributions:integration-test-3 --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
#gh pr create --repo dfinity/repositories-open-to-contributions --base master --head integration-test-3 --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"

