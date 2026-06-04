<!-- spellchecker:ignore selfsigned -->

> See [notes/implementation-context.md](notes/implementation-context.md) for
> `render()` signature, `__main__.py` insertion points, and the missing
> `community.crypto` collection before starting.

## 1. Config defaults

- [x] 1.1 Add `apps.display_server` defaults to `DEFAULTS` in `core/config.py`
  (`enabled`, `http_port`, `https_port`, `token`, `orientation: "portrait"`)
- [x] 1.2 Add tests for the new config defaults

## 2. Compositor API change

- [x] 2.1 Add optional `mode: str | None = None` parameter to
  `Compositor.set_content()` in `core/ui/compositor.py`; when `mode` is provided
  use it in place of `self._display_mode` for that call only; when `None`, fall
  back to `self._display_mode`; existing callers pass no argument and are
  unaffected
- [x] 2.2 Update `Compositor.set_content()` tests to cover explicit
  `mode="4gray"` and `mode="1bit"` arguments

## 3. Display Server module

- [x] 3.1 Create `src/inksink/display_server/__init__.py`
- [x] 3.2 Implement `RequestHandler` with `do_POST` handling `/render`; parse
  `?mode` query parameter (default `"1bit"`, return 400 for unknown values);
  parse `Content-Type` as media type only (ignore parameters such as `charset`);
  return 415 for unsupported media types, 400 for invalid bodies; for HTML
  bodies call `core.renderer.render(html, mode=mode, orientation=orientation)`
  where `orientation` is read from
  `settings["apps"]["display_server"]["orientation"]`
- [x] 3.3 Implement bearer token check on HTTPS handler (skip if token empty or
  request is HTTP)
- [x] 3.4 Implement `DisplayServer` class with an `Optional[tuple[Image.Image,
  str]]` slot protected by a `threading.Lock`; expose `take() ->
  Optional[tuple[Image, str]]`; use `try_set(image, mode)` — return 429 if slot
  occupied; create HTTP and HTTPS `HTTPServer` instances on daemon threads,
  wrapping HTTPS with `ssl.SSLContext`
- [x] 3.5 Add unit tests: valid PNG (200), invalid PNG (400), valid HTML (200),
  empty HTML (400), unsupported type (415), `text/html; charset=utf-8` (200),
  `?mode=4gray` stored correctly, `?mode=color` (400), second push while
  occupied (429), cleared slot accepted (200), HTTPS token enforced, HTTP
  ignores token, body over 5 MiB (413)

## 4. Main process integration

- [x] 4.1 In `__main__.py`, conditionally instantiate and start `DisplayServer`
  when `apps.display_server.enabled` is `true`
- [x] 4.2 At the top of the main Launcher loop call `display_server.take()`; if
  not `None`, unpack `(img, mode)`, call `compositor.set_content(img, mode=mode)`,
  then block on `input_handler.wait_for_action(display_server_event)`; `continue`
  if it returns `""` (new image arrived); otherwise fall through to Launcher
- [x] 4.3 Ensure `DisplayServer` is stopped cleanly in the `finally` block
  alongside `compositor.stop()`
- [x] 4.4 Add integration test: Display Server disabled by default (no listeners
  started)
- [x] 4.5 Update `test_keyboard_interrupt_sleeps_display_and_exits` in
  `tests/test_main.py` to patch `DisplayServer` so it does not bind a real port;
  assert `display.sleep()` is still called exactly once
- [x] 4.6 Add `threading.Event` (`display_server_event`) shared between
  `DisplayServer` and the main loop; pass as `notify_event` to `DisplayServer`
  and as `stop_event` to `Launcher`; clear before each Launcher run
- [x] 4.7 Extract main event loop body into `_render_loop()` to reduce cyclomatic
  complexity of `main()`
- [x] 4.8 Add scenario tests in `tests/test_main.py`: (a) Launcher interrupted by
  image, image shown until button, back to Launcher; (b) new image replaces shown
  image without passing through Launcher; (c) Launcher → image → button →
  Launcher → image shown

## 4b. Handler and InputHandler improvements

- [x] 4b.1 Add `stop_event: threading.Event | None = None` to
  `InputHandler.wait_for_action()`; return `""` when the event is set
- [x] 4b.2 Add `stop_event` to `Launcher.__init__()` and thread it through all
  internal `wait_for_action()` calls via a `_wait_action()` helper; inner loops
  treat `""` as an exit signal
- [x] 4b.3 Add `notify_event: threading.Event | None = None` to
  `DisplayServer.__init__()`; call `event.set()` in `try_set()` on success
- [x] 4b.4 Split HTTPS auth: missing `Authorization` header → 401; wrong token →
  403; extract into `_validate_render_auth()`
- [x] 4b.5 Fix HTML render failure response: `renderer.render()` exception →
  500 (was incorrectly 400)
- [x] 4b.6 Refactor `do_POST` into `_validate_render_request()`,
  `_validate_render_auth()`, and `_do_post_render()` to reduce cyclomatic
  complexity below Codacy limit

## 5. Ansible role

- [x] 5.1 Add `community.crypto >= 2.0.0` to
  `ansible/collections/requirements.yml` (not yet present — role will fail
  without it)
- [x] 5.2 Create `ansible/roles/display_server/tasks/main.yml`: (a) create
  `/etc/inksink/display_server/` directory (mode `0755`, owner `pi`); (b)
  generate `key.pem` with `community.crypto.openssl_privatekey` (`force: false`,
  mode `0600`, owner `pi`); (c) generate `cert.pem` with
  `community.crypto.x509_certificate` (`provider: selfsigned`, `privatekey_path:
  key.pem`, `force: false`, mode `0644`, owner `pi`)
- [x] 5.3 Add `display_server` role to `playbooks/setup.yml`
- [x] 5.4 Update `ansible/playbooks/verify.yml` to assert `cert.pem` exists at
  `/etc/inksink/display_server/`

## 6. Documentation

- [x] 6.1 Update `README.md` Display Server section to remove `_(planned)_`
  marker once implemented
- [x] 6.2 Run pre-commit hooks and fix any issues
