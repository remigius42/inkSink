## 1. Package scaffold

- [ ] 1.1 Create `src/inksink/launcher/__init__.py`
- [ ] 1.2 Create `tests/launcher/` directory with `__init__.py` and
  `test_stub.py` (import smoke test)

## 2. `Launcher` class

- [ ] 2.1 Implement `APPS` registry in `launcher/app.py`: list of
  `(label, callable)` tuples; start with `("Anki", anki_run_stub)` where
  the stub raises `NotImplementedError` until `anki-app` is implemented
- [ ] 2.2 Implement `Launcher.__init__` — accept `Display`, `InputHandler`,
  `settings`; store
  `self._orientation = settings["apps"]["launcher"]["orientation"]` for use
  in `renderer.render()` calls
- [ ] 2.3 Implement `_render_menu()` — build content HTML (vertical App list);
  call `fill_default(content, buttons)` with btn_1="" (inactive), APPS
  labels at btn_2–btn_4, btn_5=Status, btn_6=Settings, btn_7="",
  btn_8=Sleep; call
  `renderer.render(html, orientation=self._orientation)` and
  `display.display_full()`
- [ ] 2.4 Implement `_render_status()` — call `datetime.now()`,
  `battery_percent()`, `wifi_status()`, `hostname()`, IP lookup (see
  notes/pi-ip-lookup.md), `bluetooth_status()`, `load_averages()`,
  `memory_info()`, `storage_info()`, `version_info()` (see
  notes/state-functions-reference.md); render sentinels as "unavailable";
  build content HTML table; call
  `fill_default(content, ["Menu","","","","","","",""])`; render and display
- [ ] 2.5 Implement `_render_settings()` — call `load_settings()`; mask
  credential values; compute `total_lines` (one per key); build content HTML
  list with `margin-top: -{offset * 20}px`; show "↓ more" when
  `offset + visible_lines < total_lines`, "↑ more" when `offset > 0`; call
  `fill_default(content, ["Menu","","","","","↓","↑",""])`; render and display.
  Run a sub-loop: wait for btn press; btn_6 → clamp-increment offset by 5 and
  re-render; btn_7 → clamp-decrement offset by 5 and re-render; btn_1 → return
- [ ] 2.6 Implement `_render_logs()` — fetch last 100 lines via
  `journalctl -u inksink -n 100 --no-pager --output=short` (2 s timeout);
  sentinel "unavailable" on `FileNotFoundError` or non-zero exit; initial
  offset at bottom (most recent visible); same scroll sub-loop as
  `_render_settings()`: btn_6=↓, btn_7=↑, 5-line clamp, ↓/↑ indicators;
  btn_1 returns; `fill_default(content, ["Menu","","","","","↓","↑",""])`
- [ ] 2.7 Implement `run()`: renders MENU, waits for btn press, routes to
  App call / STATUS render / SETTINGS render / LOGS render / SLEEP, then
  returns. App exceptions propagate to caller — no try/except in Launcher.
- [ ] 2.8 Implement SLEEP handling: call `display.sleep()` and return.
  Wake is automatic — `display_full()` calls `_wake_if_sleeping()` on the
  next Launcher cycle.

## 3. Entry point

- [ ] 3.1 Update `src/inksink/__main__.py`: `settings = load_settings()`;
  `startup(settings)`; instantiate `Display` with `idle_timeout`,
  `portrait_rotation`, `landscape_rotation`, `full_refresh_interval` from
  `settings["display"]`; instantiate `InputHandler`; call
  `input_handler.setup()` then `display.init()` once before the loop; enter
  `while True` loop: `Launcher(display, input_handler, settings).run()`;
  catch `Exception` (log, call `fill_error(message)` → render → display,
  wait for button press); catch `KeyboardInterrupt` → `display.sleep()` +
  break; register `signal.signal(signal.SIGTERM, handler)` before the loop
  where `handler` raises `KeyboardInterrupt` so SIGTERM takes the same
  cleanup path as `KeyboardInterrupt`
- [ ] 3.2 Handle `HardwareNotAvailable` from `input_handler.setup()` on
  non-Pi host: print diagnostic and exit cleanly before entering the loop
  (dev machine safety)
- [ ] 3.3 Add `fill_error(message: str) -> str` to `core/layout.py` —
  returns a fullscreen HTML document with the error message and
  "Press any button to continue…" below it; no status bar or button bar

## 4. Tests

- [ ] 4.1 Unit test `_render_settings()`: credential masking hides values
  containing `password` or `secret`
- [ ] 4.2 Integration test `__main__` loop: App exception → error screen →
  Launcher restarted (mock Display, InputHandler, App callable)
- [ ] 4.3 Unit test sleep: `btn_8` in MENU calls `display.sleep()` and
  `Launcher.run()` returns; verify `display.init()` is NOT called inside Launcher
- [ ] 4.4 Unit tests for new `core/state.py` functions — each must return its
  sentinel value (not raise) when the underlying resource is unavailable:
  `load_averages()` on non-Linux, `memory_info()` when `/proc/meminfo` absent,
  `storage_info()` on `OSError`, `bluetooth_status()` when `bluetoothctl`
  not found

## 5. New state functions (`core/state.py`)

- [ ] 5.1 Implement `ip_address() -> str` — `socket` outbound-connect
  approach (see notes/pi-ip-lookup.md Option A); fallback `"unavailable"` on
  `OSError` or loopback result
- [ ] 5.2 Implement `hostname() -> str` — `socket.gethostname()`, fallback
  `"unknown"`
- [ ] 5.3 Implement `version_info() -> str` — `os.environ.get("INKSINK_VERSION",
  "unknown")`
- [ ] 5.4 Implement `load_averages() -> tuple[float, float, float]` —
  `os.getloadavg()`; return `(-1.0, -1.0, -1.0)` on `OSError`
- [ ] 5.5 Add `MemoryInfo` dataclass; implement `memory_info() -> MemoryInfo`
  — parse `/proc/meminfo` for `MemTotal` / `MemAvailable` in MB; sentinel
  `MemoryInfo(total_mb=-1, free_mb=-1)` on any read error
- [ ] 5.6 Add `StorageInfo` dataclass; implement `storage_info() -> StorageInfo`
  — `shutil.disk_usage("/")` converted to GB; sentinel
  `StorageInfo(total_gb=-1.0, free_gb=-1.0)` on `OSError`
- [ ] 5.7 Add `BluetoothStatus` dataclass; implement
  `bluetooth_status() -> BluetoothStatus` — `bluetoothctl show` (powered
  on/off) + `bluetoothctl devices Connected` (device list); device label =
  friendly name, fallback MAC; 2 s timeout per call; sentinel
  `BluetoothStatus(enabled=False, connected_devices=[])` on any error

## 6. Display configuration

- [ ] 6.1 Add `full_refresh_interval: 20` to `settings["display"]` in
  `DEFAULTS` in `core/config.py` (display-level default; Apps override via
  `display.set_full_refresh_interval()`)
- [ ] 6.2 Add `Display.set_full_refresh_interval(n: int) -> None` — validates
  `n > 0`, updates `self._full_refresh_interval`; called by Apps that need a
  different interval (e.g. Anki uses `settings["apps"]["anki"]["full_refresh_interval"]`)

## 7. Docs, Ansible, and housekeeping

- [ ] 7.1 Update `CONTEXT.md` glossary if any terms need amending (Launcher,
  App, Status screen)
- [ ] 7.2 Update `ansible/playbooks/verify.yml`: add assertion that
  `INKSINK_VERSION=` is present and non-empty in the deployed systemd service
  unit (required by `version_info()`)
- [ ] 7.3 Run pre-commit hooks (`pre-commit run --all-files`) and fix any
  issues
