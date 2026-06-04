<!-- spellchecker:ignore selfsigned -->

> See [notes/implementation-context.md](notes/implementation-context.md) for
> `render()` signature, `__main__.py` insertion points, and the missing
> `community.crypto` collection before starting.

## 1. Config defaults

- [ ] 1.1 Add `apps.display_server` defaults to `DEFAULTS` in `core/config.py`
  (`enabled`, `http_port`, `https_port`, `token`, `orientation: "portrait"`)
- [ ] 1.2 Add tests for the new config defaults

## 2. Compositor API change

- [ ] 2.1 Add optional `mode: str | None = None` parameter to
  `Compositor.set_content()` in `core/ui/compositor.py`; when `mode` is provided
  use it in place of `self._display_mode` for that call only; when `None`, fall
  back to `self._display_mode`; existing callers pass no argument and are
  unaffected
- [ ] 2.2 Update `Compositor.set_content()` tests to cover explicit
  `mode="4gray"` and `mode="1bit"` arguments

## 3. Display Server module

- [ ] 3.1 Create `src/inksink/display_server/__init__.py`
- [ ] 3.2 Implement `RequestHandler` with `do_POST` handling `/render`; parse
  `?mode` query parameter (default `"1bit"`, return 400 for unknown values);
  parse `Content-Type` as media type only (ignore parameters such as `charset`);
  return 415 for unsupported media types, 400 for invalid bodies; for HTML
  bodies call `core.renderer.render(html, mode=mode, orientation=orientation)`
  where `orientation` is read from
  `settings["apps"]["display_server"]["orientation"]`
- [ ] 3.3 Implement bearer token check on HTTPS handler (skip if token empty or
  request is HTTP)
- [ ] 3.4 Implement `DisplayServer` class with an `Optional[tuple[Image.Image,
  str]]` slot protected by a `threading.Lock`; expose `take() ->
  Optional[tuple[Image, str]]`; use `try_set(image, mode)` — return 429 if slot
  occupied; create HTTP and HTTPS `HTTPServer` instances on daemon threads,
  wrapping HTTPS with `ssl.SSLContext`
- [ ] 3.5 Add unit tests: valid PNG (200), invalid PNG (400), valid HTML (200),
  empty HTML (400), unsupported type (415), `text/html; charset=utf-8` (200),
  `?mode=4gray` stored correctly, `?mode=color` (400), second push while
  occupied (429), cleared slot accepted (200), HTTPS token enforced, HTTP
  ignores token, body over 5 MiB (413)

## 4. Main process integration

- [ ] 4.1 In `__main__.py`, conditionally instantiate and start `DisplayServer`
  when `apps.display_server.enabled` is `true`
- [ ] 4.2 At the top of the main Launcher loop call `display_server.take()`; if
  not `None`, unpack `(img, mode)` and call `compositor.set_content(img,
  mode=mode)`
- [ ] 4.3 Ensure `DisplayServer` is stopped cleanly in the `finally` block
  alongside `compositor.stop()`
- [ ] 4.4 Add integration test: Display Server disabled by default (no listeners
  started)
- [ ] 4.5 Update `test_keyboard_interrupt_sleeps_display_and_exits` in
  `tests/test_main.py` to patch `DisplayServer` so it does not bind a real port;
  assert `display.sleep()` is still called exactly once

## 5. Ansible role

- [ ] 5.1 Add `community.crypto >= 2.0.0` to
  `ansible/collections/requirements.yml` (not yet present — role will fail
  without it)
- [ ] 5.2 Create `ansible/roles/display_server/tasks/main.yml`: (a) create
  `/etc/inksink/display_server/` directory (mode `0755`, owner `pi`); (b)
  generate `key.pem` with `community.crypto.openssl_privatekey` (`force: false`,
  mode `0600`, owner `pi`); (c) generate `cert.pem` with
  `community.crypto.x509_certificate` (`provider: selfsigned`, `privatekey_path:
  key.pem`, `force: false`, mode `0644`, owner `pi`)
- [ ] 5.3 Add `display_server` role to `playbooks/setup.yml`
- [ ] 5.4 Update `ansible/playbooks/verify.yml` to assert `cert.pem` exists at
  `/etc/inksink/display_server/`

## 6. Documentation

- [ ] 6.1 Update `README.md` Display Server section to remove `_(planned)_`
  marker once implemented
- [ ] 6.2 Run pre-commit hooks and fix any issues
