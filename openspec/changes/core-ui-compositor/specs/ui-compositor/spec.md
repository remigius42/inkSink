## Purpose

Stateful Compositor in `core/ui/` that owns the in-memory framebuffer,
orchestrates the two-layer rendering pipeline (wkhtmltoimage content zone +
Pillow chrome), drives partial refresh for chrome updates, and maintains a
background status bar refresh timer.

## ADDED Requirements

### Requirement: Compositor owns the framebuffer

`core/ui/compositor.py` SHALL provide a `Compositor` class that holds a PIL
Image as the authoritative framebuffer for the physical screen. The framebuffer
SHALL be a 1-bit PIL Image at the current orientation dimensions. One Compositor
instance SHALL exist for the process lifetime, instantiated in `core/startup.py`
alongside `Display`.

#### Scenario: Compositor initializes with empty framebuffer

- **WHEN** `Compositor` is instantiated
- **THEN** it holds a white 1-bit PIL Image at the correct orientation dimensions

### Requirement: set_content triggers full refresh and resets framebuffer

`Compositor.set_content(html: str)` SHALL render the HTML via `renderer.render()`,
composite it onto the framebuffer, redraw all chrome regions (status bar,
button bar if present), and call `display.display_full()` or
`display.display_4gray()` according to the App's display mode. This is the
natural App transition point; all previous framebuffer state is discarded.

#### Scenario: New content replaces previous framebuffer state

- **WHEN** `set_content(html)` is called after a prior screen state
- **THEN** the framebuffer is fully redrawn from the new HTML and current chrome state

#### Scenario: set_content with 4gray mode calls display_4gray

- **WHEN** the App's display mode is `"4gray"` and `set_content(html)` is called
- **THEN** `display.display_4gray()` is used for the full refresh

### Requirement: set_buttons redraws button bar via partial refresh

The Compositor SHALL provide `set_buttons(labels: list[str | None], states: list[ButtonState])`
accepting exactly 8 labels and 8 states (indexed `btn_1`–`btn_8`). It SHALL
redraw the button bar region on the framebuffer using Pillow, call
`display.display_partial()`, and derive the button bar edge and layout from
`display.portrait_rotation` and the current orientation.

Each label SHALL be interpreted as follows:

- A non-empty string — renders as a labeled button slot
- `None` — renders as invisible (no border, no fill, no label)
- `""` (empty string) — merges this slot into the previous slot, extending
  its width (portrait) or height (landscape); raises `ValueError` if the
  first slot in a row is `""`

#### Scenario: set_buttons updates button bar without full refresh

- **WHEN** `set_buttons(labels, states)` is called
- **THEN** only the button bar region of the framebuffer is redrawn and
  `display.display_partial()` is called (not `display_full`)

#### Scenario: Wrong list length raises ValueError

- **WHEN** `set_buttons` is called with a list of length ≠ 8 for labels or states
- **THEN** `ValueError` is raised

### Requirement: set_button_state updates a single button via partial refresh

`Compositor.set_button_state(idx: int, state: ButtonState)` SHALL update the
visual state of one button (0-indexed, 0 = `btn_1`) on the framebuffer and
call `display.display_partial()`. No full redraw of the button bar occurs.

#### Scenario: Single button highlight on press

- **WHEN** `set_button_state(1, ButtonState.ACTIVE)` is called
- **THEN** only `btn_2`'s region on the framebuffer is redrawn as inverted
  and `display.display_partial()` is called

### Requirement: Button tristate rendering in 1-bit

The Compositor SHALL render buttons in three visual states using only 1-bit
Pillow primitives (no gray):

- **default**: white fill, 2px black outline, black text
- **active**: black fill, 2px black outline, white text (fully inverted)
- **disabled**: white fill, dashed black outline, black text

#### Scenario: Active button is visually inverted

- **WHEN** a button is rendered with `ButtonState.ACTIVE`
- **THEN** its PIL region has a black background and white text

#### Scenario: Disabled button uses dashed outline

- **WHEN** a button is rendered with `ButtonState.DISABLED`
- **THEN** its PIL region has a white background, dashed outline, and black text

### Requirement: Button bar edge is orientation-aware

In portrait, the button bar SHALL be rendered at the bottom of the framebuffer.
In landscape, the button bar edge SHALL be derived from `display.portrait_rotation`:
the edge that corresponds to the physical bottom (where the buttons are) SHALL
host the button bar. Button text SHALL be rotated 90° to read correctly from
that edge.

#### Scenario: Portrait button bar is at bottom

- **WHEN** orientation is `PORTRAIT`
- **THEN** button bar occupies the bottom `BUTTON_BAR_SIZE` rows of the framebuffer

#### Scenario: Landscape button bar edge matches physical buttons

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=90`
- **THEN** button bar occupies the right `BUTTON_BAR_SIZE` columns of the framebuffer
  and button text is rendered vertically

### Requirement: Landscape double-column button layout

The Compositor SHALL support two landscape button bar layouts controlled by
`apps.<name>.display.double_vertical_button_size`. When `False` (default), the
bar SHALL be `BUTTON_BAR_SIZE` wide with a 4×2 layout (4 rows, 2 columns).
When `True`, the bar SHALL be `2 × BUTTON_BAR_SIZE` wide with a 4×4 layout
(4 rows, 4 columns), and a filled dot marker (●) SHALL indicate each button's
y-position to disambiguate which on-screen slot maps to which physical button.

#### Scenario: Landscape narrow layout (4×2, default)

- **WHEN** orientation is `LANDSCAPE` and `double_vertical_button_size=False`
- **THEN** button bar width equals `BUTTON_BAR_SIZE` and shows a 4×2 grid
  (4 rows, 2 columns)

#### Scenario: Landscape wide layout (4×4, doubled)

- **WHEN** orientation is `LANDSCAPE` and `double_vertical_button_size=True`
- **THEN** button bar width equals `2 × BUTTON_BAR_SIZE`, shows a 4×4 grid
  (4 rows, 4 columns), and each button slot contains a ● marker

### Requirement: None label renders as invisible button slot

A label of `None` SHALL cause the Compositor to leave that slot completely
empty — no border, no fill, no label. The slot still occupies its grid
position (spacing is preserved) but is visually indistinguishable from the
background. `ButtonState` for a `None` slot SHALL be ignored.

#### Scenario: None slot is invisible

- **WHEN** a slot's label is `None`
- **THEN** no border, fill, or text is drawn in that slot's grid region

#### Scenario: None slot preserves grid spacing

- **WHEN** a slot's label is `None` and adjacent slots have labels
- **THEN** adjacent slots remain in their correct grid positions

### Requirement: Empty string label extends the current button run

A run of consecutive `""` labels following a non-`None`, non-`""` label SHALL
extend the width (portrait) or height (landscape) of that label's button by
one slot unit per `""` in the run. The entire run forms one merged button.
The label and ● marker of the merged group SHALL be left-aligned (portrait)
or top-aligned (landscape), anchored at the first slot's edge. `ButtonState`
for `""` slots SHALL be ignored; the merged group uses the state of the first
slot in the run.

`""` as the first slot in a row (portrait) or column (landscape) SHALL raise
`ValueError`. A `""` run starting in one row and crossing into the next
(e.g. portrait slot 3 is a label and slot 4 is `""`) SHALL raise `ValueError`.

#### Scenario: Two adjacent slots produce a double-wide button

- **WHEN** labels are `["Wide", "", "A", "B", "C", "D", "E", "F"]`
- **THEN** slots 0–1 render as one double-wide button labeled "Wide"
  left-aligned, and slots 2–7 render normally

#### Scenario: Multiple consecutive empty strings extend the same run

- **WHEN** labels are `[None, "foo", "", "", "bar", None, "baz", ""]`
- **THEN** "foo" spans slots 1–3 (triple-wide) with ● at slot 1's position;
  "bar" occupies slot 4; slot 5 is invisible; "baz" spans slots 6–7
  (double-wide) with ● at slot 6's position; slots 0 and 5 are invisible

#### Scenario: Merged slot uses first slot's state

- **WHEN** labels are `["OK", "", "A", "B", "C", "D", "E", "F"]` and states
  are `[ButtonState.ACTIVE, ButtonState.DEFAULT, ...]`
- **THEN** the merged "OK" button spanning slots 0–1 is rendered as ACTIVE

#### Scenario: Empty string as first slot raises ValueError

- **WHEN** `set_buttons(["", ...], states)` is called with `""` as the first label
- **THEN** `ValueError` is raised

#### Scenario: Empty string as first slot of any row raises descriptive ValueError

- **WHEN** `set_buttons(["", ...], states)` is called with `""` at index 0
- **THEN** `ValueError` is raised with a message identifying the offending slot
  index and the rule, e.g. `"slot 0: '' cannot start a row"`

#### Scenario: Run crossing row boundary raises descriptive ValueError

- **WHEN** portrait labels are `["a", "b", "c", "", "", "d", "e", "f"]`
  (run on "c" reaches slot 3, then `""` at slot 4 tries to cross into row 2)
- **THEN** `ValueError` is raised with a message identifying the offending slot
  index and the boundary crossed, e.g.
  `"slot 4: '' run crosses row boundary from row 1 into row 2"`

### Requirement: Status bar refreshes on a configurable timer

The Compositor SHALL run a daemon thread that redraws the status bar region
(time, WiFi, battery) via Pillow and calls `display.display_partial()` every
`display.status_refresh_interval` seconds (default: 20). The timer SHALL start
on `compositor.start()` and stop on `compositor.stop()`.

#### Scenario: Status bar updates without App involvement

- **WHEN** 20 seconds elapse with no App interaction
- **THEN** the status bar region is redrawn with current time and
  `display.display_partial()` is called automatically

#### Scenario: Timer stops on compositor.stop()

- **WHEN** `compositor.stop()` is called (e.g. in SIGTERM handler)
- **THEN** no further status bar refreshes occur

### Requirement: Chrome region dimensions are constants

`core/ui/` SHALL export `BUTTON_BAR_SIZE: int` and `STATUS_BAR_HEIGHT: int`
as module-level constants. These SHALL be the single source of truth used by
both the Compositor (for drawing) and `core/layout.py` (for template variable
injection). They SHALL NOT be Config keys.

#### Scenario: Template and Compositor agree on chrome dimensions

- **WHEN** `fill_content` injects `BUTTON_BAR_SIZE` into the Jinja2 template
- **THEN** the blank region reserved in the HTML exactly matches the region
  the Compositor draws into
