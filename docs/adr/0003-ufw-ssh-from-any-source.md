<!-- spellchecker:ignore hotspot -->

# ADR 0003 — UFW allows SSH from any source

## Status

Accepted

## Context

The Device moves between networks (home WiFi, phone hotspot, guest networks).
The conventional hardening approach — restricting SSH to a known LAN subnet —
would block access whenever the Device is on a different network than the
control machine.

## Decision

UFW allows SSH (port 22) from any source. fail2ban provides brute-force
protection with an SSH jail, compensating for the absence of network-level
restriction.

## Consequences

- SSH is reachable from any network the Device connects to
- fail2ban is a hard dependency of the `base` role, not optional
- A compromised or publicly reachable IP increases exposure compared to
  LAN-only; accepted given the personal-use threat model and fail2ban
  mitigation
