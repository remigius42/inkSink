## Notes

- [notes/pyproject-toml.md](notes/pyproject-toml.md) — current `pyproject.toml`
  state and the exact `[project]` section to add (task 1.1)

## 1. Python Package

- [ ] 1.1 Add `[project]` section to `pyproject.toml` (name, version, requires-python, dependencies)
- [ ] 1.2 Create `src/inksink/__init__.py` and `src/inksink/__main__.py` (stub entry point)
- [ ] 1.3 Create `src/inksink/core/__init__.py` with stub modules: `display.py`, `input.py`, `renderer.py`, `state.py`
- [ ] 1.4 Create `src/inksink/anki/__init__.py` with stub modules: `client.py`, `app.py`
- [ ] 1.5 Create `tests/conftest.py`, `tests/core/test_stub.py`, `tests/anki/test_stub.py`
- [ ] 1.6 Add `pytest` to `requirements-dev.txt` and update `AGENTS.md` to replace unittest with pytest
- [ ] 1.7 Verify `python3 -m inksink` runs without error and `pytest` collects with zero failures

## 2. Ansible Infrastructure

- [ ] 2.1 Create `ansible/ansible.cfg` (inventory path, remote user `pi`, vault password file)
- [ ] 2.2 Create `ansible/inventory/hosts.yml` and `group_vars/all/vars.yml`
- [ ] 2.3 Create `group_vars/all/vault.yml` (encrypted placeholder) and `vault.yml.example`
- [ ] 2.4 Create `ansible/roles/base/` role (OS packages, locale, SSH hardening, UFW)
- [ ] 2.4a Create `vendor/waveshare_epd/` with stub `VENDOR.md` (source URL, commit SHA TBD, date, files); add placeholder `epd7in5_V2.py` and `epdconfig.py` with header comments
- [ ] 2.5 Create `ansible/roles/inksink/` role (synchronize src/, config template, shell wrapper, systemd service as `pi`)
- [ ] 2.6 Create `ansible/playbooks/setup.yml` (applies base + inksink)
- [ ] 2.7 Create `ansible/playbooks/deploy.yml` (applies inksink role only)
- [ ] 2.8 Create `ansible/playbooks/verify.yml` (asserts packages, files, service running)

## 3. Hardware Case

- [ ] 3.1 Create `hardware/bom.md` (move/consolidate from build guide)
- [ ] 3.2 Create `hardware/case/params.scad` with named dimension variables from build guide
- [ ] 3.3 Create `hardware/case/front.scad` (stub referencing params.scad)
- [ ] 3.4 Create `hardware/case/back.scad` (stub referencing params.scad)
- [ ] 3.5 Create `hardware/case/assembly.scad` (imports front + back, positions for inspection)

## 4. Documentation

- [ ] 4.1 Create `docs/setup.md` (vault setup, run setup.yml, deploy.yml,
  verify.yml; cross-ref Raspberry Pi Imager / firstrun.sh for OS bootstrap)

## 5. CI

- [ ] 5.1 Create `.github/workflows/ci.yml` — on push/PR to main: setup-python 3.13, `pip install -r requirements-dev.txt`, `pre-commit run --all-files`, `pytest`; skip forks on PRs
