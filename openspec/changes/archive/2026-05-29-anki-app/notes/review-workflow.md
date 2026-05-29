<!-- spellchecker:ignore poweroff -->

# Daily Review Workflow (from build guide)

The intended user experience — use this as the acceptance test for the
session flow implementation.

## Normal session

1. Power on device (press PiSugar button) → Launcher menu appears
2. Press `btn_2` ("Anki") in Launcher to start a review session
3. Device shows "Syncing…" while downloading collection (or "Offline — using last
   sync" for 2 seconds if WiFi unavailable)
4. First card question appears automatically with progress indicator ("1 / 47")
5. View question, think about answer
6. Press `btn_2` ("Show Answer") to reveal answer
7. Rate recall using bottom row buttons
8. Next card appears automatically
9. Continue until all cards reviewed
10. Device shows session summary; press `btn_1` ("Menu") to sync and return
    to Launcher (sync happens before returning if WiFi available)

## Button mapping

| Physical button | Label (QUESTION) | Label (ANSWER) | Anki rating |
| --------------- | ---------------- | -------------- | ----------- |
| `btn_1` | Menu | Menu | — (return to Launcher) |
| `btn_2` | Show Answer | — | — |
| `btn_3` | — | — | — |
| `btn_4` | — | — | — |
| `btn_5` | — | Again | 1 — Failed, reset card |
| `btn_6` | — | Hard | 2 — Correct but difficult |
| `btn_7` | — | Good | 3 — Correct with effort |
| `btn_8` | — | Easy | 4 — Correct and easy |

## Charging

- Connect USB-C cable to PiSugar 3
- Can use device while charging
- Expected runtime: 5-7 hours active use
- Typical usage: 30-60 min/day = 5-10 days between charges
- Low battery warning at <10%; app calls `systemctl poweroff` for clean shutdown

## Maintenance access

- SSH over WiFi: `ssh pi@inksink.local`
- Check logs: `/var/log/inksink.log` (or systemd journal)
- Update software: run `deploy.yml` playbook
