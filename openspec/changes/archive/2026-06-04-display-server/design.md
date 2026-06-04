<!-- spellchecker:ignore stdlib -->

## Context

The main process (`__main__.py`) owns the Compositor, Display, and InputHandler.
It runs the Launcher in a loop on the main thread. A Display Server must share
the Compositor to call `set_content()` without duplicating the rendering
pipeline.

The Pi Zero 2W has a single SPI bus; the Waveshare library is not thread-safe.
The Compositor is also not currently thread-safe. The Display Server must not
call display or compositor methods concurrently with the main thread.

## Goals / Non-Goals

**Goals:**

- Accept POST `/render` with `image/png` or `text/html` over HTTP and HTTPS
- Feed content to the Compositor from a background thread safely
- Generate the self-signed cert via Ansible (once; not on every deploy)
- Optional bearer token on HTTPS only

**Non-Goals:**

- Authentication on the HTTP listener (LAN trust; see ADR 0017)
- Persisting pushed content across reboots
- Rate limiting or queuing multiple simultaneous pushes

## Decisions

### Threading model: queue-based handoff with event interrupt

The Display Server runs an HTTP server on a daemon thread. It does **not** call
`compositor.set_content()` directly — that would race with the main thread.
Instead it writes to a single `Optional[tuple[Image.Image, str]]` slot on the
`DisplayServer` instance, protected by a `threading.Lock`, where the string is
the display mode (`"1bit"` or `"4gray"`, from the `?mode` query parameter,
defaulting to `"1bit"`). If the slot is already occupied, the handler returns
HTTP 429 immediately — no buffering of stale content, immediate feedback to
retry.

A `threading.Event` (`display_server_event`) is shared between `DisplayServer`
and the main loop. `DisplayServer.try_set()` calls `event.set()` on success,
which unblocks any `wait_for_action(stop_event)` call that is currently polling.
`InputHandler.wait_for_action()` accepts an optional `stop_event` and returns
`""` when it is set. `Launcher` accepts a `stop_event` and threads it through
all internal `wait_for_action()` calls, returning early when interrupted.

The main loop in `__main__.py`:

```python
display_server_event = threading.Event()
# ...
def _render_loop(display_server, compositor, input_handler, display, settings, display_server_event):
    while True:
        if display_server is not None:
            pending = display_server.take()
            if pending is not None:
                img, mode = pending
                if compositor is not None:
                    compositor.set_content(img, mode=mode)
                    if input_handler.wait_for_action(display_server_event) == "":
                        continue  # new image arrived — show it without going through Launcher
        display_server_event.clear()
        try:
            Launcher(..., stop_event=display_server_event).run()
        except KeyboardInterrupt:
            break
        except Exception as e:
            _handle_app_exception(...)
```

This keeps all Compositor and Display calls on the main thread with no locking
required. Images stay visible until the user presses a button or a new push
arrives.

**Alternative considered:** a threading.Lock around Compositor calls. Rejected —
the SPI bus and Waveshare library make concurrent display operations unsafe
regardless of Python-level locking.

### HTTP server: stdlib `http.server`

`http.server.HTTPServer` from the standard library handles the single `POST
/render` route. No external dependency (Flask, FastAPI) needed for one endpoint
on a Pi Zero. HTTPS wraps the same server with `ssl.SSLContext`.

**Alternative considered:** Flask. Rejected — adds a dependency and process
overhead for a single endpoint.

### Two listeners, one handler class

HTTP and HTTPS each get their own `HTTPServer` instance on separate ports, both
on separate daemon threads. The handler class is shared; it checks
`self.server.is_https` (a flag set at construction) to decide whether to enforce
the bearer token.

### Cert generation: Ansible, idempotent

The `display_server` Ansible role uses `community.crypto.x509_certificate` with
`force: false` so the cert is generated once and not regenerated on re-runs
(regenerating would break client trust). Cert and key are stored at
`/etc/inksink/display_server/cert.pem` and `key.pem`, owned by the `pi` user.

### Display mode: query parameter, not content negotiation

An optional `?mode=1bit|4gray` query parameter controls both the HTML render
pipeline (`renderer.render(mode=...)`) and the display method
(`compositor.set_content(mode=...)`). A query parameter is simpler than a custom
header and visible in `curl` commands without extra flags.
`Compositor.set_content()` gains an optional `mode` parameter (default `"1bit"`)
that overrides `self._display_mode` for that call only — existing callers (all
Apps) pass no argument and are unaffected.

### HTML rendering: wkhtmltoimage via existing `render()`

`text/html` bodies are decoded to a string and passed directly to
`core.renderer.render(html, orientation=...)`. The resulting PIL Image is placed
on the queue. Rendering happens on the HTTP handler thread (background), not the
main thread — this is safe because `render()` only calls wkhtmltoimage and
returns a PIL Image; it does not touch the Display or Compositor.

### Ports

- HTTP: `apps.display_server.http_port` (default `8080`)
- HTTPS: `apps.display_server.https_port` (default `8443`)

Port 443/80 require root; 8080/8443 work as the `pi` user.

## Risks / Trade-offs

**Compositor interrupt with no recovery hint** → When a push lands, the current
App's screen is replaced with no visual cue to the user. Mitigation: the
`display_server` module logs the interrupt; a future enhancement could overlay a
small "press Menu to return" hint.

**wkhtmltoimage latency on Pi Zero** → Rendering HTML on the background thread
blocks that thread for 2–5 s; subsequent pushes queue up behind it. Acceptable
for the expected use case (infrequent pushes). The queue depth is unbounded but
practically limited by push rate.

**Cert regeneration on Ansible role changes** → If the Ansible role task is ever
re-written without `force: false`, the cert silently rotates and all clients
break. Mitigation: the `force: false` flag is documented in the role task
comment.

**429 drops pushes during rendering** → A caller that pushes faster than the
display renders will see 429s and must retry. For the expected use case (home
automation, cron scripts at regular intervals) this is preferable to silently
queuing and rendering stale content.
