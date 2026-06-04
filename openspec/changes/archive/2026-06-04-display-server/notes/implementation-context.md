# Implementation Context

Notes from the design session that save re-reading source files.

## `render()` takes an HTML string, not a file path

`core.renderer.render()` takes a complete HTML document **string** and returns
a `PIL Image`:

```python
def render(
    html: str,
    mode: str = "1bit",
    orientation: Orientation = Orientation.PORTRAIT,
) -> Image.Image:
```

For HTML payloads, decode the request body to a string and pass it directly.
Pass the `mode` from the `?mode` query parameter. Read orientation from
`settings["apps"]["display_server"]["orientation"]` (default `"portrait"`,
same pattern as `anki` and `weather` apps).

## `Compositor.set_content()` gains a `mode` parameter

The existing signature is `set_content(img: Image)`. This change adds
`mode: str = "1bit"`. The `mode` argument replaces `self._display_mode` for
that call only — existing App callers pass no argument and are unaffected.

`DisplayServer.take()` returns `Optional[tuple[Image.Image, str]]`. Unpack
before calling `set_content`:

```python
if (pending := display_server.take()) is not None:
    img, mode = pending
    compositor.set_content(img, mode=mode)
```

## `__main__.py` insertion points

Read from source at time of design. Startup sequence:

```python
settings = load_settings()
display = Display(...)
compositor = startup(settings, display, active_app="launcher")
input_handler = InputHandler()
# signal handler setup
input_handler.setup()
display.init()
compositor.start()
# ← start DisplayServer here, after compositor.start()

while True:
    # ← if (pending := display_server.take()): img, mode = pending; compositor.set_content(img, mode=mode)
    try:
        Launcher(...).run()
    except KeyboardInterrupt:
        break
    except Exception as e:
        _handle_app_exception(...)

# finally block:
compositor.stop()
# ← stop DisplayServer here alongside compositor.stop()
display.sleep()
```

## `community.crypto` collection is missing

`ansible/collections/requirements.yml` currently lists only:

- `community.general >= 8.0.0`
- `ansible.posix >= 1.0.0`

Task 4.1 uses `community.crypto.x509_certificate`. **Add the collection to
`requirements.yml` before writing the role** — the role will fail in CI
otherwise. Add:

```yaml
- name: community.crypto
  version: ">=2.0.0"
```

## `setup.yml` roles list

Currently: `[base, inksink]`. Task 4.2 adds `display_server` as a third role.
The role runs unconditionally (cert generation is cheap and idempotent); the
Display Server process only starts when `apps.display_server.enabled: true`.
