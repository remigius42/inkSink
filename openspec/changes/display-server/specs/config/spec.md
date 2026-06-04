## ADDED Requirements

### Requirement: `apps.display_server` defaults are defined

`DEFAULTS` in `core/config.py` SHALL include the following keys under
`apps.display_server`:

- `enabled`: `false`
- `http_port`: `8080`
- `https_port`: `8443`
- `token`: `""` (empty string; empty string means no token enforcement)

#### Scenario: Display Server defaults present when config is absent

- **WHEN** `load_settings()` is called and no config file exists
- **THEN** `settings["apps"]["display_server"]["enabled"]` is `false`
- **AND** `settings["apps"]["display_server"]["http_port"]` is `8080`
- **AND** `settings["apps"]["display_server"]["https_port"]` is `8443`
- **AND** `settings["apps"]["display_server"]["token"]` is `""`
