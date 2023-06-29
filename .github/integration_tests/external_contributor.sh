#!/bin/bash

set -euo pipefail

# Integration test to ensure CLA closes PR for an external contributor

# set git credentials
git config user.name dfinity
git config user.email dfinity@dfinity.org

gh auth login --with-token <<< $ACCESS_TOKEN

# create new branch
#git clone git@github.com:dfinity-sandbox/repositories-open-to-contributions.git
#cd repositories-open-to-contributions

echo "success"
git checkout -b integration-test-3

# add a fake repository
touch test.txt
git add test.txt
git commit -m 'add empty file'

git push --set-upstream origin integration-test-3

# get updates for forked repo
# git remote add upstream https://github.com/dfinity/repositories-open-to-contributions.git
# git fetch upstream
# git merge upstream/master master

# create pull request
#gh pr create --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
#gh pr create --base dfinity/repositories-open-to-contributions:master --head dfinity-sandox/repositories-open-to-contributions:integration-test-3 --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
gh pr create --repo dfinity/repositories-open-to-contributions --base master --head integration-test-3 --draft --title "Integration Test 3" --body "generated by integration test from branch $GITHUB_HEAD_REF"
#git push origin -d integration-test-3
