<!-- spellchecker:ignore minkowski polyround -->

# Vendor: Round-Anything (OpenSCAD)

| Field | Value |
| -- | -- |
| Source | <https://github.com/Irev-Dev/Round-Anything> |
| Commit | `061fef7c429628808e847696bb345a9b0ec6e279` |
| Date | 2026-05-28 |
| Files | `polyround.scad` |

## Why vendored

Provides `polyRoundExtrude` and `polyRound` for 3D fillets on rectangular
profiles — faster and more composable than `minkowski()`. Used in case
geometry (`hardware/case/`) for outer-edge rounding.

## Update procedure

1. Copy `polyround.scad` from the upstream commit.
1. Update the commit SHA and date in this file.
