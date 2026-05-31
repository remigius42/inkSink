# Launcher Button State Reference

Physical grid (portrait, bottom edge of device):

```text
[ btn_1 ][ btn_2 ][ btn_3 ][ btn_4 ]   ← top row
[ btn_5 ][ btn_6 ][ btn_7 ][ btn_8 ]   ← bottom row
```

## Labels per state

| Button | MENU | STATUS | SETTINGS | LOGS |
| --- | --- | --- | --- | --- |
| btn_1 | *(blank — inactive)* | Menu | Menu | Menu |
| btn_2 | Anki | | | |
| btn_3 | *(next App)* | | | |
| btn_4 | *(next App)* | | | |
| btn_5 | Status | | | |
| btn_6 | Settings | | ↓ | ↓ |
| btn_7 | Logs | | ↑ | ↑ |
| btn_8 | Sleep | | | |

Empty cells = inactive (blank label rendered, button press ignored).

`btn_1` = "Menu" is the universal return action across all states and all
Apps. In MENU state the button renders with a **blank label** (empty string
passed to the layout); no greyed "Menu" text is shown. "Empty cells = inactive"
convention applies — the button press is ignored.

## App slot assignment (MENU state)

Apps are assigned to btn_2–btn_4 in registration order:

```python
APPS = [
    ("Anki", run_anki),      # → btn_2
    # ("Ebooks", run_ebooks), # → btn_3  (future)
    # ("PDF",    run_pdf),    # → btn_4  (future)
]
```

If fewer than 3 Apps are registered, remaining btn_3/btn_4 slots are blank.

## btn_1 convention for content Apps

Every content App layout must reserve btn_1 for "Menu". The App's state
machine should handle `btn_1` press at any state by returning from `run()`.
The Launcher catches the return and re-renders MENU.
