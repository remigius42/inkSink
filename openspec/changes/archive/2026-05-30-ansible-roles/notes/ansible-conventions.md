<!-- spellchecker:ignore bantime findtime hotspot maxretry nocows -->

# Ansible Conventions

Project-wide conventions for all Ansible files.

## `ansible.cfg`

```ini
# spellchecker: ignore jsonfile tmpfiles

[defaults]
inventory = inventory/
vault_password_file = .vault_pass
roles_path = roles
log_path = .ansible/ansible.log
nocows = 1
retry_files_enabled = False
display_skipped_hosts = no
pipelining = True
allow_world_readable_tmpfiles = True
fact_caching = jsonfile
fact_caching_connection = .ansible/facts_cache
fact_caching_timeout = 86400
```

## `group_vars/all/vars.yml` structure

```yaml
# SPDX-License-Identifier: MIT
---
base_locale_timezone: "Europe/Zurich"
fail2ban_bantime: "1h"
fail2ban_findtime: "10m"
fail2ban_maxretry: 5
```

Note: no `ufw_lan_subnet` — UFW allows SSH from any source per ADR 0003
(device moves between networks; subnet restriction would block access on
guest/hotspot networks).

## Role directory structure (every role)

```text
roles/<name>/
├── defaults/main.yml     ← role variables with defaults
├── handlers/main.yml     ← restart/reload handlers
├── meta/main.yml         ← dependencies, galaxy metadata
├── tasks/main.yml        ← task list
├── templates/            ← Jinja2 .j2 files
├── files/                ← static files
└── README.md             ← variable reference
```

## Task file conventions

```yaml
# SPDX-License-Identifier: MIT
---
- name: Install <package>
  ansible.builtin.apt:
    name: <package>
    state: present
    update_cache: true
    cache_valid_time: 3600
  become: true

- name: Deploy config from template
  ansible.builtin.template:
    src: config.j2
    dest: /etc/<name>/config
    owner: "{{ service_user }}"
    group: "{{ service_group }}"
    mode: "0640"
  become: true
  notify: Restart <service>
```

- Always `# SPDX-License-Identifier: MIT` + `---` at top of every YAML
- Always fully-qualified module names (`ansible.builtin.*`)
- Always `become: true` on privileged tasks (never `become: true` at play level)
- Always `cache_valid_time: 3600` on apt tasks
- `changed_when: false` on read-only commands
- Notify handlers by exact name string

## Handler conventions (`handlers/main.yml`)

```yaml
# SPDX-License-Identifier: MIT
---
- name: Restart <service>
  ansible.builtin.systemd:
    name: <service>
    state: restarted
    daemon_reload: true
  become: true

- name: Reload systemd
  ansible.builtin.systemd:
    daemon_reload: true
  become: true
```

## `verify.yml` pattern

Pattern for each assertion:

```yaml
- name: Gather service facts
  ansible.builtin.service_facts:

- name: Assert <service> is running and enabled
  ansible.builtin.assert:
    that:
      - "ansible_facts.services['<service>.service'] is defined"
      - "ansible_facts.services['<service>.service'].state == 'running'"
      - "ansible_facts.services['<service>.service'].status == 'enabled'"
    fail_msg: "<service> is not running or not enabled"

- name: Assert package is installed
  ansible.builtin.package_facts:
    manager: auto

- name: Fail if <package> missing
  ansible.builtin.assert:
    that: "'<package>' in ansible_facts.packages"
    fail_msg: "<package> is not installed"
```
