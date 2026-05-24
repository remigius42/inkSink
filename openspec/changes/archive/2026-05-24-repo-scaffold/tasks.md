## Notes

- [notes/pyproject-toml.md](notes/pyproject-toml.md) — current `pyproject.toml`
  state and the exact `[project]` section to add (task 1.1)

## 1. Python Package

- [x] 1.1 Add `[project]` section to `pyproject.toml` (name, version, requires-python, dependencies)
- [x] 1.2 Create `src/inksink/__init__.py` and `src/inksink/__main__.py` (stub entry point)
- [x] 1.3 Create `src/inksink/core/__init__.py` with stub modules: `display.py`, `input.py`, `renderer.py`, `state.py`
- [x] 1.4 Create `src/inksink/anki/__init__.py` with stub modules: `client.py`, `app.py`
- [x] 1.5 Create `tests/conftest.py`, `tests/core/test_stub.py`, `tests/anki/test_stub.py`
- [x] 1.6 Add `pytest` to `requirements-dev.txt` and update `AGENTS.md` to replace unittest with pytest
- [x] 1.7 Verify `python3 -m inksink` runs without error and `pytest` collects with zero failures

## 2. Ansible Infrastructure

- [x] 2.1 Create `ansible.cfg` at repo root (inventory path, remote user `pi`, vault password file; lives at root so ansible-lint finds it)
- [x] 2.2 Create `ansible/inventory/hosts.yml` and `ansible/group_vars/all/vars.yml`
- [x] 2.3 Create `ansible/group_vars/all/vault.yml` (encrypted placeholder) and `ansible/group_vars/all/vault.yml.example`
- [x] 2.4 Create `ansible/roles/base/` role (OS packages, locale, SSH hardening, UFW)
- [x] 2.4a Create `vendor/waveshare_epd/` with stub `VENDOR.md` (source URL, commit SHA TBD, date, files); add placeholder `epd7in5_V2.py` and `epdconfig.py` with header comments
- [x] 2.5 Create `ansible/roles/inksink/` role (synchronize src/, config template, shell wrapper, systemd service as `pi`)
- [x] 2.6 Create `ansible/playbooks/setup.yml` (applies base + inksink)
- [x] 2.7 Create `ansible/playbooks/deploy.yml` (applies inksink role only)
- [x] 2.8 Create `ansible/playbooks/verify.yml` (asserts packages, files, service running)

## 3. Hardware Case

- [x] 3.1 Create `hardware/bom.md` (move/consolidate from build guide)
- [x] 3.2 Create `hardware/case/params.scad` with named dimension variables from build guide
- [x] 3.3 Create `hardware/case/front.scad` (stub referencing params.scad)
- [x] 3.4 Create `hardware/case/back.scad` (stub referencing params.scad)
- [x] 3.5 Create `hardware/case/assembly.scad` (imports front + back, positions for inspection)

## 4. Documentation

- [x] 4.1 Create `docs/setup.md` (vault setup, run setup.yml, deploy.yml,
  verify.yml; cross-ref Raspberry Pi Imager / firstrun.sh for OS bootstrap)
- [x] 4.2 Create `docs/development.md` (one-time venv setup, `source .venv/bin/activate` reminder, pre-commit install with `--hook-type pre-commit --hook-type commit-msg`, pytest, linting, OpenSpec workflow); point `README.md ## Development` to it

## 5. CI

- [x] 5.1 Create `.github/workflows/ci.yml` — on push/PR to main: setup-python
  3.13, `pip install -r requirements-dev.txt`, `pre-commit run --all-files`,
  `pytest`; skip forks on PRs; `persist-credentials: false`; pip cache keyed
  on requirements hash

## 6. Post-review fixes

- [x] 6.1 `ansible/roles/inksink/tasks/main.yml` — add `ansible.builtin.file`
  ownership tasks (`owner: pi, group: pi, recurse: true`) after each
  `synchronize` task
- [x] 6.2 `hardware/case/params.scad` — clamp `wall` with `max(min_wall, …)`
  to guard against zero/negative wall thickness
- [x] 6.3 `pyproject.toml` — fix `requires-python` to `">=3.13"` to match
  tooling targets; device runs Raspberry Pi OS Trixie (Python 3.13)
- [x] 6.4 `hardware/case/` — wrap stub geometry in named modules so
  `assembly.scad` can compose via `use <>` instead of `import()`

## 7. Ansible linting

- [x] 7.1 Add `ansible-lint` pre-commit hook to `.pre-commit-config.yaml`; update `docs/development.md` hooks list
- [x] 7.2 Fix `ansible-lint` violations: rename `ansible.builtin.locale_gen` →
  `community.general.locale_gen`; add `ansible/collections/requirements.yml`
  (`community.general`, `ansible.posix`) so ansible-lint resolves collections;
  add `.ansible-lint` with `mock_roles` so role resolution works from repo root
- [x] 7.3 Move vault password file from `~/.ansible-vault-password` to
  `.vault-password` at repo root; gitignore it; update `ansible.cfg`
  and `docs/setup.md`
