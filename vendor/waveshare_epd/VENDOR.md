# Vendor: Waveshare e-Paper Library

| Field | Value |
| -- | -- |
| Source | <https://github.com/waveshare/e-Paper> |
| Path | `RaspberryPi_JetsonNano/python/lib/waveshare_epd/` |
| Commit | TBD — pin when files are copied from upstream |
| Date | TBD |
| Files | `epd7in5_V2.py`, `epdconfig.py` |

## Why vendored

The upstream repo has no stable release cadence and no PyPI package.
`git clone` at provision time requires network access and Git on the device
(both excluded by ADR 0001). Vendoring the two relevant files keeps deployment
self-contained and makes the exact version auditable.

## Update procedure

1. Copy `epd7in5_V2.py` and `epdconfig.py` from the upstream commit.
1. Update the commit SHA and date in this file.
1. Update the header comments in each file.
