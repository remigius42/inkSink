#!/usr/bin/env bash
set -euo pipefail

CODACY=$(command -v codacy) || { echo "codacy binary not found — run 'codacy login' or ensure it is on PATH" >&2; exit 1; }

# Parse org/repo from remote URL (handles both SSH and HTTPS)
REMOTE_URL=$(git remote get-url origin)
REPO_PATH=$(echo "$REMOTE_URL" | sed 's|git@github.com:||; s|https://github.com/||; s|\.git$||')
ORG=$(echo "$REPO_PATH" | cut -d/ -f1)
REPO=$(echo "$REPO_PATH" | cut -d/ -f2)

BRANCH=$(git branch --show-current)
[ -z "$BRANCH" ] && { echo "Cannot determine branch — detached HEAD?" >&2; exit 1; }

echo "Looking up PR for ${ORG}/${REPO} on branch: ${BRANCH}"

PR_NUMBER=$(curl -sf "https://api.github.com/repos/${REPO_PATH}/pulls?state=open&head=${ORG}:${BRANCH}" \
  | python3 -c "import sys, json; prs = json.load(sys.stdin); print(prs[0]['number'] if prs else '')")

if [ -z "$PR_NUMBER" ]; then
    echo "No open PR found for branch: ${BRANCH}" >&2
    exit 1
fi

echo "Found PR #${PR_NUMBER} — fetching Codacy issues..."
"$CODACY" pr gh "$ORG" "$REPO" "$PR_NUMBER"
