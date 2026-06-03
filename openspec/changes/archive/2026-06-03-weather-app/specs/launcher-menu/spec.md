## MODIFIED Requirements

### Requirement: Launcher shows App menu on boot

`launcher/app.py` SHALL provide a `Launcher` class with a `run()` method that
renders the MENU state on startup. The menu SHALL display available Apps as
labeled buttons using the `default` layout. `btn_1` SHALL always be labeled
"Menu" (inactive / self-referential in MENU state). Each registered App SHALL
occupy a button slot with its display name as the label. The Weather App
(`weather/app.py`) SHALL be registered as a content App with the label "Weather"
(or equivalent locale label).

#### Scenario: Menu renders on startup

- **WHEN** `Launcher().run()` is called
- **THEN** the display shows the MENU screen with at least one App button
  labeled

#### Scenario: App is launched on button press

- **WHEN** the user presses a button mapped to a registered App in MENU state
- **THEN** the Launcher calls that App's `run()` function and blocks until it
  returns

#### Scenario: Control returns to menu after App exits

- **WHEN** a launched App's `run()` function returns (user pressed btn_1 "Menu")
- **THEN** the Launcher re-renders the MENU screen

#### Scenario: Weather App is accessible from menu

- **WHEN** the MENU screen is displayed
- **THEN** a button labeled "Weather" (or equivalent) is visible and launches the
  Weather App when pressed
