<!-- markdownlint-disable MD013 -->

## ADDED Requirements

### Requirement: Launcher shows App menu on boot

`launcher/app.py` SHALL provide a `Launcher` class with a `run()` method that
renders the MENU state on startup. The menu SHALL display available Apps as
labeled buttons using the `default` layout. `btn_1` SHALL always be labeled
"Menu" (inactive / self-referential in MENU state). Each registered App SHALL
occupy a button slot with its display name as the label.

#### Scenario: Menu renders on startup

- **WHEN** `Launcher().run()` is called
- **THEN** the display shows the MENU screen with at least one App button labeled

#### Scenario: App is launched on button press

- **WHEN** the user presses a button mapped to a registered App in MENU state
- **THEN** the Launcher calls that App's `run()` function and blocks until it returns

#### Scenario: Control returns to menu after App exits

- **WHEN** a launched App's `run()` function returns (user pressed btn_1 "Menu")
- **THEN** the Launcher re-renders the MENU screen

### Requirement: App crashes are caught and surfaced at the menu

If a content App's `run()` raises an unhandled exception, `__main__.py` SHALL catch it, log it, and display an error screen (via `fill_error()` in `core/layout.py`) showing the exception message and "Press any button to continue…". It SHALL block until any button is pressed, then restart Launcher.

#### Scenario: Crashed App returns to menu

- **WHEN** a launched App raises an exception
- **THEN** an error screen is shown with "Press any button to continue…" and
  MENU is restored after the user presses any button

### Requirement: btn_8 in MENU sleeps the display

In MENU state, `btn_8` SHALL be labeled "Sleep" and SHALL call
`display.sleep()`, then return immediately. The next Launcher cycle's
`display_full()` call triggers `_wake_if_sleeping()` automatically — no
explicit `display.init()` or button-wait inside Launcher.

#### Scenario: Sleep and wake cycle

- **WHEN** `btn_8` is pressed in MENU state
- **THEN** `display.sleep()` is called; pressing any button wakes the display
  and returns to MENU
