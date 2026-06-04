<!-- spellchecker:ignore sniffable wttr -->

# ADR 0017 — Display Server: opt-in HTTP+HTTPS endpoint for push-rendered content

## Status

Accepted

## Context

Content Apps pull data from external services (AnkiWeb, wttr.in) on a
per-session or scheduled basis. A complementary pattern is push: an external
system sends content to the Device for immediate display, without requiring the
user to navigate to an App. This is the literal meaning of "Sink" in the project
name — a terminal node where information flows to rest.

Two approaches were considered:

**Per-App polling / scheduling.** Each App fetches its own data at configured
intervals. Already the pattern for Weather and Anki. Does not support ad-hoc
push from arbitrary external sources.

**Display Server: opt-in HTTP endpoint.** A background service running alongside
the main process accepts POST requests with a PNG image or HTML payload and
passes the content directly to the Compositor. Any device on the LAN (Home
Assistant, cron scripts, a laptop) can push content without user interaction —
the Device becomes a passive network display.

Security is a real concern: an open HTTP endpoint on the LAN can be abused to
display arbitrary content. A bearer token over plain HTTP is sniffable and
therefore security theater. HTTPS removes the sniffing risk; generating a
self-signed certificate is one Ansible task, and trust anchoring on the client
is the user's responsibility (`curl -k`, OS cert store, etc.) — not the
Device's. The service is therefore offered on both HTTP (open, LAN trust) and
HTTPS (with optional bearer token via `apps.display_server.token`). If no token
is configured, HTTPS still encrypts transport but requires no credential. HTTP
exists for LAN clients that prefer not to deal with a self-signed cert. It is
disabled by default and requires explicit opt-in via
`apps.display_server.enabled` in Config. The Device is not exposed to the
internet; LAN-only is the intended scope.

## Decision

Implement the Display Server as an optional App (`src/inksink/display_server/`)
that starts automatically alongside the main process when enabled. The endpoint
accepts POST `/render` with either a PNG body (`Content-Type: image/png`) or an
HTML body (`Content-Type: text/html`). PNG payloads are composited directly;
HTML payloads are rendered via the standard wkhtmltoimage pipeline. The
Compositor's existing `set_content()` / `display_partial()` API is reused
without modification.

The service is **disabled by default**. Enabling it is an explicit user action
(`apps.display_server.enabled: true` in Config). The Ansible `display_server`
role generates a self-signed certificate on first deploy. Both HTTP and HTTPS
listeners start on enable. Token auth on HTTPS is opt-in via
`apps.display_server.token`; unset means HTTPS with no credential check.

## Consequences

- The Device can function as a silent, always-on network display without user
  interaction (beyond powering on)
- External integrations (home automation, calendar pushes, custom scripts) are
  possible without building dedicated Apps for each data source
- The Display Server bypasses the Launcher; a pushed image will interrupt
  whatever the user is doing on-device. This is intentional — push semantics
  imply urgency or scheduled replacement
- HTTP is open (LAN trust); HTTPS supports an optional bearer token — not
  security theater because it is not sniffable
- Client trust of the self-signed cert is the user's responsibility; the Ansible
  role only generates and deploys the cert on the Device side
- The Display Server is a strong argument for why inkSink is distinct from a
  commercial e-ink device: no commercial device exposes this kind of open
  network rendering API
