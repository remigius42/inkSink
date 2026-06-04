<!-- spellchecker:ignore addopts -->

# Development

Local setup for working on this project: dev environment, running tests,
linting, and the OpenSpec change workflow used to evolve the codebase.

## Dev environment

Requires Python 3.13+. One-time setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt -e .
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

For subsequent sessions, activate the venv before running any commands below:

```bash
source .venv/bin/activate
```

## Running tests

```bash
pytest
```

Coverage is reported automatically (configured via `addopts` in `pyproject.toml`).

## Linting and formatting

Pre-commit runs automatically on `git commit`. To run manually:

```bash
pre-commit run --all-files
```

Hooks include: Black, Ruff, Pyright, markdownlint, cspell, ansible-lint and
openspec validation.

Pure formatting commits are listed in `.git-blame-ignore-revs`. To have `git blame` skip them
automatically:

```bash
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

## Commit messages

Conventional Commits enforced by commitlint (`commitlint.config.js`). Examples:

```text
feat: add anki card display
fix: correct partial refresh timing
docs: update docs/setup.md
```

## CI

GitHub Actions runs all pre-commit hooks and pytest on every push to `main` and
on pull requests from branches in the same repository (fork PRs are excluded).

## OpenSpec workflow

Changes are managed with [OpenSpec](https://openspec.dev). The typical cycle:

```bash
openspec new      # create a new change (proposal → design → specs → tasks)
openspec apply    # work through implementation tasks
openspec verify   # check completeness before archiving
openspec archive  # finalize the change
```

Changes live under `openspec/changes/<name>/`. Main specs live under
`openspec/specs/`.
