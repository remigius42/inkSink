## ADDED Requirements

### Requirement: Display Server starts when enabled

When `apps.display_server.enabled` is `true`, `__main__.py` SHALL start the
Display Server before the main Launcher loop. The Display Server SHALL run HTTP
and HTTPS listeners on separate daemon threads and hold a single pending slot (a
`(PIL Image, mode)` tuple protected by a `threading.Lock`, where `mode` is
`"1bit"` or `"4gray"`). The main loop SHALL consume the pending slot between
Launcher iterations by calling `compositor.set_content(image, mode=mode)`.

#### Scenario: Server starts on enabled flag

- **WHEN** `apps.display_server.enabled` is `true` in config
- **THEN** HTTP and HTTPS listeners are running before the Launcher loop begins

#### Scenario: Server does not start when disabled

- **WHEN** `apps.display_server.enabled` is `false` or absent
- **THEN** no HTTP or HTTPS listener is started and the Launcher loop is
  unaffected

### Requirement: POST /render accepts an optional mode query parameter

`POST /render` SHALL accept an optional `mode` query parameter with values
`1bit` (default) or `4gray`. Any other value SHALL return HTTP 400. The mode is
stored alongside the image in the pending slot and passed to
`compositor.set_content()`.

#### Scenario: Default mode is 1bit

- **WHEN** `POST /render` is called without a `mode` parameter
- **THEN** the pending slot stores mode `"1bit"`

#### Scenario: mode=4gray is accepted

- **WHEN** `POST /render?mode=4gray` is called with a valid body
- **THEN** the pending slot stores mode `"4gray"`

#### Scenario: Invalid mode returns 400

- **WHEN** `POST /render?mode=color` is called
- **THEN** the server returns 400

### Requirement: POST /render enforces a 5 MiB body size limit

`POST /render` SHALL reject any request whose body exceeds 5 MiB (5 242 880
bytes). The check SHALL be applied before any decoding or rendering: if
`Content-Length` exceeds the limit, or if the number of bytes read while
streaming the body exceeds the limit, the server SHALL return HTTP 413 and
discard the remainder of the body.

#### Scenario: Oversized body returns 413

- **WHEN** a `POST /render` request is sent with a body larger than 5 MiB
- **THEN** the server returns 413 before attempting to decode or render the body

### Requirement: POST /render accepts image/png

`POST /render` with `Content-Type: image/png` SHALL decode the body as a PNG
image using Pillow, place the PIL Image in the pending slot, and return HTTP 200
with an empty body.

#### Scenario: Valid PNG is accepted

- **WHEN** a valid PNG body is POSTed to `/render`
- **THEN** the server returns 200 and the decoded image is in the pending slot

#### Scenario: Invalid PNG body returns 400

- **WHEN** a body that is not a valid PNG is POSTed with `Content-Type:
  image/png`
- **THEN** the server returns 400

### Requirement: POST /render accepts text/html

`POST /render` with `Content-Type: text/html` SHALL decode the body to a string
and call `core.renderer.render(html, mode=mode, orientation=orientation)` to
produce a PIL Image, place the image in the pending slot, and return HTTP 200
with an empty body. The `orientation` value SHALL be read from
`apps.display_server.orientation` in config (default `"portrait"`).

#### Scenario: HTML body is rendered and accepted

- **WHEN** a valid HTML body is POSTed to `/render`
- **THEN** the server returns 200 and the rendered image is in the pending slot

#### Scenario: Empty HTML body returns 400

- **WHEN** an empty body is POSTed with `Content-Type: text/html`
- **THEN** the server returns 400

### Requirement: Unsupported content type returns 415

`POST /render` SHALL match on the media type (type/subtype) of the
`Content-Type` header, ignoring parameters such as `charset`. It SHALL return
HTTP 415 when the media type is neither `image/png` nor `text/html`.

#### Scenario: Unknown content type rejected

- **WHEN** a request is POSTed with `Content-Type: application/json`
- **THEN** the server returns 415

### Requirement: HTTPS enforces optional bearer token

When `apps.display_server.token` is set, the HTTPS listener SHALL require an
`Authorization: Bearer <token>` header on every request. Requests without the
header or with an incorrect token SHALL return HTTP 401. The HTTP listener SHALL
never check for a token.

#### Scenario: Correct token accepted on HTTPS

- **WHEN** a request arrives on the HTTPS listener with the correct
  `Authorization: Bearer` token
- **THEN** the request is processed normally

#### Scenario: Missing token rejected on HTTPS

- **WHEN** `apps.display_server.token` is set and a request arrives on the HTTPS
  listener without an `Authorization` header
- **THEN** the server returns 401

#### Scenario: HTTP listener ignores token config

- **WHEN** `apps.display_server.token` is set and a request arrives on the HTTP
  listener without an `Authorization` header
- **THEN** the request is processed normally (no 401)

### Requirement: Pending image is rendered on the main thread

The main loop SHALL consume the pending image slot between Launcher iterations
and call `compositor.set_content()` if an image is present. All Compositor and
Display calls remain on the main thread.

#### Scenario: Push renders between Launcher runs

- **WHEN** the pending slot holds an image at the start of a main loop iteration
- **THEN** `compositor.set_content()` is called with that image before the next
  Launcher run begins

### Requirement: POST /render returns 429 when slot is occupied

`POST /render` SHALL return HTTP 429 if the pending slot already holds an
unrendered image. The request body SHALL be discarded. This gives callers
immediate feedback to retry later.

#### Scenario: Second push rejected while first is unrendered

- **WHEN** a first push has been accepted but not yet rendered by the main
  thread
- **AND** a second `POST /render` request arrives
- **THEN** the server returns 429 and the first image remains in the pending
  slot

#### Scenario: Push accepted after slot is cleared

- **WHEN** the main thread has consumed the previous image from the pending slot
- **AND** a new `POST /render` request arrives
- **THEN** the server returns 200 and the new image occupies the pending slot
