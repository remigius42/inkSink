"""Tests for core/ui/buttons.py — button rendering, slot resolution, bounding boxes."""

# cspell:ignore bboxes

import pytest
from PIL import Image, ImageDraw

from inksink.core.ui import BUTTON_BAR_SIZE, ButtonState
from inksink.core.ui.buttons import (
    _button_bar_edge,
    _compute_bounding_boxes,
    _draw_button,
    _resolve_slots,
)

_PW, _PH = 480, 800  # portrait framebuffer
_LW, _LH = 800, 480  # landscape framebuffer


# ---------------------------------------------------------------------------
# 3.1  _button_bar_edge
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_button_bar_edge_portrait_always_bottom(rotation):
    assert _button_bar_edge(rotation, "portrait") == "bottom"


@pytest.mark.parametrize(
    "rotation,expected",
    [
        (0, "bottom"),
        (90, "right"),
        (180, "top"),
        (270, "left"),
    ],
)
def test_button_bar_edge_landscape(rotation, expected):
    assert _button_bar_edge(rotation, "landscape") == expected


# ---------------------------------------------------------------------------
# 3.2  _resolve_slots
# ---------------------------------------------------------------------------


def test_resolve_slots_all_strings():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    assert len(groups) == 8
    for i, g in enumerate(groups):
        assert g.indices == [i]
        assert g.label == labels[i]
        assert g.state_index == i


def test_resolve_slots_none_slots():
    labels = [None, "A", None, "B", None, "C", None, "D"]
    groups = _resolve_slots(labels)
    assert len(groups) == 8
    assert groups[0].label is None
    assert groups[0].indices == [0]
    assert groups[1].label == "A"


def test_resolve_slots_single_merge():
    labels = ["Wide", "", "A", "B", "C", "D", "E", "F"]
    groups = _resolve_slots(labels)
    assert len(groups) == 7  # slot 0 absorbs slot 1
    assert groups[0].indices == [0, 1]
    assert groups[0].label == "Wide"
    assert groups[0].state_index == 0
    assert groups[1].label == "A"
    assert groups[1].indices == [2]


def test_resolve_slots_chain_merge():
    labels = [None, "foo", "", "", "bar", None, "baz", ""]
    groups = _resolve_slots(labels)
    assert len(groups) == 5
    # slot 0: None
    assert groups[0].label is None
    assert groups[0].indices == [0]
    # slots 1,2,3: "foo" triple
    assert groups[1].label == "foo"
    assert groups[1].indices == [1, 2, 3]
    assert groups[1].state_index == 1
    # slot 4: "bar"
    assert groups[2].label == "bar"
    assert groups[2].indices == [4]
    # slot 5: None
    assert groups[3].label is None
    assert groups[3].indices == [5]
    # slots 6,7: "baz" double
    assert groups[4].label == "baz"
    assert groups[4].indices == [6, 7]
    assert groups[4].state_index == 6


def test_resolve_slots_empty_first_raises():
    with pytest.raises(ValueError, match=r"slot 0: .* cannot start a row"):
        _resolve_slots(["", "foo", "A", "B", "C", "D", "E", "F"])


def test_resolve_slots_empty_first_of_second_row_raises():
    with pytest.raises(ValueError, match=r"slot 4: .* cannot start a row"):
        _resolve_slots(["A", "B", "C", "D", "", "F", "G", "H"])


def test_resolve_slots_run_crosses_row_boundary_raises():
    # "c" at slot 2, "" at slots 3 and 4 — slot 4 crosses row boundary
    with pytest.raises(ValueError, match=r"slot 4: .* crosses row boundary"):
        _resolve_slots(["a", "b", "c", "", "", "d", "e", "f"])


def test_resolve_slots_merged_state_uses_first_slot():
    labels = ["OK", "", "A", "B", "C", "D", "E", "F"]
    groups = _resolve_slots(labels)
    # The merged group uses state_index=0 (the first slot)
    assert groups[0].state_index == 0


# ---------------------------------------------------------------------------
# 3.3  _compute_bounding_boxes
# ---------------------------------------------------------------------------


def test_bboxes_portrait_normal_slots():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "portrait", False)
    # Bar at bottom of 480x800 framebuffer
    y_start = _PH - BUTTON_BAR_SIZE  # 720
    col_w = _PW // 4  # 120
    row_h = BUTTON_BAR_SIZE // 2  # 40
    # slot 0: row=0, col=0
    assert bboxes[0] == (0, y_start, col_w, row_h)
    # slot 3: row=0, col=3
    assert bboxes[3] == (3 * col_w, y_start, col_w, row_h)
    # slot 4: row=1, col=0
    assert bboxes[4] == (0, y_start + row_h, col_w, row_h)
    # slot 7: row=1, col=3
    assert bboxes[7] == (3 * col_w, y_start + row_h, col_w, row_h)


def test_bboxes_portrait_none_slot():
    labels = [None, "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "portrait", False)
    # None slot still occupies its grid position
    assert bboxes[0] == (0, _PH - BUTTON_BAR_SIZE, _PW // 4, BUTTON_BAR_SIZE // 2)


def test_bboxes_portrait_merged_slot():
    labels = ["Wide", "", "A", "B", "C", "D", "E", "F"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "portrait", False)
    y_start = _PH - BUTTON_BAR_SIZE
    col_w = _PW // 4
    row_h = BUTTON_BAR_SIZE // 2
    # Merged group [0,1]: double-wide
    assert bboxes[0] == (0, y_start, 2 * col_w, row_h)
    # Next group "A" at slot 2
    assert bboxes[1] == (2 * col_w, y_start, col_w, row_h)


def test_bboxes_landscape_narrow():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "landscape", False, portrait_rotation=90)
    # Bar at right of 800x480 framebuffer
    x_start = _LW - BUTTON_BAR_SIZE  # 720
    col_w = BUTTON_BAR_SIZE // 2  # 40
    row_h = _LH // 4  # 120
    # slot 0: col=0, row=0 → x=720, y=0
    assert bboxes[0] == (x_start, 0, col_w, row_h)
    # slot 3: col=0, row=3 → x=720, y=360
    assert bboxes[3] == (x_start, 3 * row_h, col_w, row_h)
    # slot 4: col=1, row=0 → x=760, y=0
    assert bboxes[4] == (x_start + col_w, 0, col_w, row_h)
    # slot 7: col=1, row=3 → x=760, y=360
    assert bboxes[7] == (x_start + col_w, 3 * row_h, col_w, row_h)


def test_bboxes_landscape_horizontal_bottom():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "landscape", False, portrait_rotation=0)
    # edge="bottom": bar at bottom of 800x480 framebuffer
    y_start = _LH - BUTTON_BAR_SIZE  # 400
    col_w = _LW // 4  # 200
    row_h = BUTTON_BAR_SIZE // 2  # 40
    assert bboxes[0] == (0, y_start, col_w, row_h)
    assert bboxes[3] == (3 * col_w, y_start, col_w, row_h)
    assert bboxes[4] == (0, y_start + row_h, col_w, row_h)
    assert bboxes[7] == (3 * col_w, y_start + row_h, col_w, row_h)


def test_bboxes_landscape_horizontal_top():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "landscape", False, portrait_rotation=180)
    # edge="top": bar at top of 800x480 framebuffer
    col_w = _LW // 4  # 200
    row_h = BUTTON_BAR_SIZE // 2  # 40
    assert bboxes[0] == (0, 0, col_w, row_h)
    assert bboxes[3] == (3 * col_w, 0, col_w, row_h)
    assert bboxes[4] == (0, row_h, col_w, row_h)
    assert bboxes[7] == (3 * col_w, row_h, col_w, row_h)


def test_bboxes_landscape_wide():
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = _resolve_slots(labels)
    bboxes = _compute_bounding_boxes(groups, "landscape", True, portrait_rotation=90)
    x_start = _LW - 2 * BUTTON_BAR_SIZE  # 640
    row_h = _LH // 4  # 120
    pair_w = BUTTON_BAR_SIZE  # 80
    # slot 0: pair=0, row=0 → x=640, y=0, w=80, h=120
    assert bboxes[0] == (x_start, 0, pair_w, row_h)
    # slot 3: pair=0, row=3 → x=640, y=360
    assert bboxes[3] == (x_start, 3 * row_h, pair_w, row_h)
    # slot 4: pair=1, row=0 → x=720, y=0
    assert bboxes[4] == (x_start + pair_w, 0, pair_w, row_h)


# ---------------------------------------------------------------------------
# 3.4-3.6  Button drawing — pixel assertions
# ---------------------------------------------------------------------------


def _btn_image(w=120, h=40):
    """Create a white 1-bit image with an ImageDraw."""
    img = Image.new("1", (w, h), color=1)
    draw = ImageDraw.Draw(img)
    return img, draw


def test_active_button_corner_pixel_is_black():
    img, draw = _btn_image()
    _draw_button(draw, 0, 0, 120, 40, "OK", ButtonState.ACTIVE)
    px = img.load()
    assert px is not None
    assert px[2, 2] == 0


def test_default_button_corner_pixel_is_white():
    img, draw = _btn_image()
    _draw_button(draw, 0, 0, 120, 40, "OK", ButtonState.DEFAULT)
    px = img.load()
    assert px is not None
    assert px[2, 2] == 1


def test_disabled_button_border_dashes():
    img, draw = _btn_image()
    _draw_button(draw, 0, 0, 120, 40, "X", ButtonState.DISABLED)
    px = img.load()
    assert px is not None
    assert px[0, 0] == 0
    assert px[4, 0] == 1


# ---------------------------------------------------------------------------
# 3.7  None slot drawing
# ---------------------------------------------------------------------------


def test_none_slot_region_is_unchanged():
    img = Image.new("1", (120, 40), color=1)
    draw = ImageDraw.Draw(img)
    _draw_button(draw, 0, 0, 120, 40, None, ButtonState.ACTIVE)
    px = img.load()
    assert px is not None
    assert px[0, 0] == 1
    assert px[60, 20] == 1


# ---------------------------------------------------------------------------
# 3.8  Merged slot drawing
# ---------------------------------------------------------------------------


def test_merged_slot_no_internal_border():
    """A double-wide merged slot should have no vertical border at the midpoint."""
    img = Image.new("1", (240, 40), color=1)
    draw = ImageDraw.Draw(img)
    _draw_button(draw, 0, 0, 240, 40, "Wide", ButtonState.DEFAULT)
    px = img.load()
    assert px is not None
    assert px[120, 20] == 1  # fill is white, no internal divider


# ---------------------------------------------------------------------------
# Vertical text rendering (landscape mode)
# ---------------------------------------------------------------------------


def test_vertical_text_default_button_background_is_white():
    """
    Vertical-text DEFAULT button keeps background white.

    Background pixels must not be painted black by the bitmap mask.
    """
    img = Image.new("1", (40, 120), color=1)
    draw = ImageDraw.Draw(img)
    _draw_button(draw, 0, 0, 40, 120, "OK", ButtonState.DEFAULT, text_vertical=True)
    px = img.load()
    assert px is not None
    # (2, 2) is inside the 2px border, far from the text center — must stay white
    assert px[2, 2] == 1


def test_vertical_text_active_button_background_is_black():
    """
    Vertical-text ACTIVE button keeps background black.

    Background pixels must not be painted white by the bitmap mask.
    """
    img = Image.new("1", (40, 120), color=1)
    draw = ImageDraw.Draw(img)
    _draw_button(draw, 0, 0, 40, 120, "OK", ButtonState.ACTIVE, text_vertical=True)
    px = img.load()
    assert px is not None
    # (2, 2) is inside the 2px border, far from the text center — must be black (0)
    assert px[2, 2] == 0
