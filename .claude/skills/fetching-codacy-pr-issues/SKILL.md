---
name: fetching-codacy-pr-issues
description: Fetches Codacy analysis for the open PR associated with the current branch. Use when the user asks about Codacy issues, PR quality, or code analysis results for the current branch.
---

Run `scripts/fetch-codacy-issues.sh` from this skill's directory.

## Gotchas

- Must be on a named branch — detached HEAD yields an empty branch name and "no PR found"
- Requires an open PR on GitHub for the current branch; exits with a clear error if none found
- If Codacy returns an auth error, run `codacy login` first
