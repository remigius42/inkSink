<!-- spellchecker:ignore sched -->

## ADDED Requirements

### Requirement: Session state is in-memory only

`anki/app.py` SHALL define a `SessionState` dataclass holding `current_card_index`,
`review_count`, and `last_sync`. `SessionState` SHALL NOT be persisted to disk —
a reboot or crash resets it.

#### Scenario: Fresh session starts at zero

- **WHEN** a new `SessionState()` is instantiated
- **THEN** `review_count` is 0 and `current_card_index` is `None`

### Requirement: Anki Session opens with a sync screen

When the app starts, the display SHALL show a "Syncing…" screen while the
collection is downloaded. If WiFi is unavailable, the display SHALL show
"Offline — using last sync" and proceed with the local collection.

#### Scenario: Online sync shows syncing screen

- **WHEN** the app launches and WiFi is available
- **THEN** "Syncing…" is displayed while `sync_down()` runs

#### Scenario: Offline start shows offline notice

- **WHEN** the app launches and WiFi is unavailable
- **THEN** "Offline — using last sync" is displayed for 2 seconds before
  the first card appears

### Requirement: Card question is displayed and waits for btn_2

After sync, the first due card's question HTML SHALL be rendered and
displayed using the Anki layout template with a progress indicator ("N / M").
The session SHALL block until `btn_2` (labeled "Show Answer") is pressed.
`btn_1` (labeled "Menu") SHALL cause `run()` to return immediately.

#### Scenario: Question is shown with progress indicator

- **WHEN** the session enters the QUESTION state for card N of M
- **THEN** the card front HTML and "N / M" are rendered and displayed

#### Scenario: Only btn_2 advances from QUESTION state

- **WHEN** any button other than `btn_2` or `btn_1` is pressed in QUESTION state
- **THEN** the session remains in QUESTION state (button is ignored)

#### Scenario: btn_1 in QUESTION returns to Launcher

- **WHEN** `btn_1` is pressed in QUESTION state
- **THEN** `ReviewSession.run()` returns without completing the session

### Requirement: Card answer is displayed and waits for a rating button

After `btn_2` is pressed, the card answer HTML SHALL be rendered and
displayed. The session SHALL block until one of `btn_5` (Again), `btn_6`
(Hard), `btn_7` (Good), or `btn_8` (Easy) is pressed. `btn_1` (Menu) SHALL
cause `run()` to return immediately.

#### Scenario: Answer is shown after btn_2

- **WHEN** `btn_2` is pressed in QUESTION state
- **THEN** the card back HTML is rendered and the display updates to ANSWER state

#### Scenario: Rating button submits review and advances

- **WHEN** `btn_7` (Good) or any valid rating button is pressed in ANSWER state
- **THEN** the review is recorded via `col.sched.answer_card(card, rating)`
  (1=Again, 2=Hard, 3=Good, 4=Easy) and the session advances to the next due
  card

#### Scenario: btn_1 in ANSWER returns to Launcher

- **WHEN** `btn_1` is pressed in ANSWER state
- **THEN** `ReviewSession.run()` returns without recording the current card's review

### Requirement: Anki Session ends when no due cards remain

When all due cards have been reviewed, the display SHALL show a summary
screen with the count of cards reviewed and total session time. The session
SHALL wait for `btn_1` (labeled "Menu"). If WiFi is available, `sync_up()`
SHALL be called before `run()` returns to the Launcher.

#### Scenario: Summary shown after last card

- **WHEN** the last due card is rated
- **THEN** the display shows "Done! X cards reviewed in Y minutes"

#### Scenario: Collection uploaded before returning to Launcher

- **WHEN** `btn_1` is pressed on the summary screen and WiFi is available
- **THEN** `sync_up()` is called and completes before `run()` returns

### Requirement: Cards are rendered in portrait orientation

The session SHALL render all card states (QUESTION, ANSWER, SYNCING, DONE)
in portrait orientation (`480×800 px`) by passing `orientation="portrait"`
to the renderer. The orientation value is driven by the `apps.anki.orientation`
config key (default `"portrait"`, per ADR 0008).

#### Scenario: Card renders at portrait dimensions

- **WHEN** the session renders a card in QUESTION or ANSWER state
- **THEN** the image passed to the display driver is portrait-sized
  (height > width), and `Display` rotates it to the 800×480 panel buffer

### Requirement: Card progress is shown via the Anki layout template

The display SHALL show the current card position and total due count
(e.g. "12 / 47") as a named slot in `anki/layouts/review.html.j2`, filled
alongside the card content HTML. It SHALL NOT be a PIL overlay.

#### Scenario: Progress indicator updates each card

- **WHEN** the session advances to card N of M
- **THEN** the display shows "N / M" in the reserved progress region of the
  layout alongside the card content
