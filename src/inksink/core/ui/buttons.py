"""Pillow-based button bar rendering for the e-ink compositor."""

# cspell:ignore bboxes getbbox

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from PIL import Image, ImageDraw, ImageFont

from inksink.core.display import _PANEL_H, _PANEL_W
from inksink.core.ui import BUTTON_BAR_SIZE, ButtonState

if TYPE_CHECKING:
    pass

_DASH = 4  # dash-on length in pixels


@dataclass
class _SlotGroup:
    indices: list[int]
    label: str | None
    state_index: int


def _extend_group(
    groups: list[_SlotGroup], i: int, cols: int, prev_lbl: str | None
) -> None:
    row = i // cols
    col_in_row = i % cols
    if col_in_row == 0:
        if i > 0 and prev_lbl == "":
            prev_row = (i - 1) // cols
            raise ValueError(
                f"slot {i}: '' run crosses row boundary "
                f"from row {prev_row + 1} into row {row + 1}"
            )
        raise ValueError(f"slot {i}: '' cannot start a row")
    if not groups:
        raise ValueError(f"slot {i}: '' cannot start a row")
    prev = groups[-1]
    prev_row = prev.indices[-1] // cols
    if prev_row != row:
        raise ValueError(
            f"slot {i}: '' run crosses row boundary "
            f"from row {prev_row + 1} into row {row + 1}"
        )
    prev.indices.append(i)


def _resolve_slots(labels: Sequence[str | None], cols: int = 4) -> list[_SlotGroup]:
    """Resolve 8 raw labels into slot groups, handling None and '' merging."""
    groups: list[_SlotGroup] = []
    for i, lbl in enumerate(labels):
        if lbl == "":
            _extend_group(groups, i, cols, labels[i - 1] if i > 0 else None)
        else:
            groups.append(_SlotGroup(indices=[i], label=lbl, state_index=i))
    return groups


def _button_bar_edge(portrait_rotation: int, orientation: str) -> str:
    """Derive which screen edge hosts the button bar."""
    if orientation == "portrait":
        return "bottom"
    _map = {0: "bottom", 90: "right", 180: "top", 270: "left"}
    return _map[portrait_rotation]


def _horizontal_bboxes(
    slot_groups: list[_SlotGroup],
    y_start: int,
    cols: int,
    col_w: int,
    row_h: int,
) -> list[tuple[int, int, int, int]]:
    return [
        (
            g.indices[0] % cols * col_w,
            y_start + g.indices[0] // cols * row_h,
            len(g.indices) * col_w,
            row_h,
        )
        for g in slot_groups
    ]


def _vertical_bboxes(
    slot_groups: list[_SlotGroup],
    x_start: int,
    col_w: int,
    row_h: int,
) -> list[tuple[int, int, int, int]]:
    return [
        (
            x_start + g.indices[0] // 4 * col_w,
            g.indices[0] % 4 * row_h,
            col_w,
            len(g.indices) * row_h,
        )
        for g in slot_groups
    ]


def _compute_bounding_boxes(
    slot_groups: list[_SlotGroup],
    orientation: str,
    double_vertical: bool,
    portrait_rotation: int = 90,
) -> list[tuple[int, int, int, int]]:
    """Return (x, y, w, h) in framebuffer coords for each slot group."""
    edge = _button_bar_edge(portrait_rotation, orientation)

    if orientation == "portrait":
        fw, fh = _PANEL_H, _PANEL_W
        col_w = fw // 4
        row_h = BUTTON_BAR_SIZE // 2
        return _horizontal_bboxes(slot_groups, fh - BUTTON_BAR_SIZE, 4, col_w, row_h)

    fw, fh = _PANEL_W, _PANEL_H
    row_h = fh // 4

    if edge in ("right", "left"):
        x_start = (
            fw - (2 * BUTTON_BAR_SIZE if double_vertical else BUTTON_BAR_SIZE)
            if edge == "right"
            else 0
        )
        col_w = BUTTON_BAR_SIZE if double_vertical else BUTTON_BAR_SIZE // 2
        return _vertical_bboxes(slot_groups, x_start, col_w, row_h)

    col_w = fw // 4
    row_h_h = BUTTON_BAR_SIZE // 2
    y_start = fh - BUTTON_BAR_SIZE if edge == "bottom" else 0
    return _horizontal_bboxes(slot_groups, y_start, 4, col_w, row_h_h)


def _dashed_rectangle(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    dash: int = _DASH,
) -> None:
    """Draw a dashed rectangle outline (1-bit: 0=black) on draw."""

    def _dash_line(pts: list[tuple[int, int]]) -> None:
        on = True
        count = 0
        for pt in pts:
            if count == dash:
                on = not on
                count = 0
            if on:
                draw.point(pt, fill=0)
            count += 1

    top = [(x, y0) for x in range(x0, x1 + 1)]
    bottom = [(x, y1) for x in range(x0, x1 + 1)]
    left = [(x0, y) for y in range(y0, y1 + 1)]
    right = [(x1, y) for y in range(y0, y1 + 1)]
    _dash_line(top)
    _dash_line(bottom)
    _dash_line(left)
    _dash_line(right)


def _draw_label(
    draw: ImageDraw.ImageDraw,
    slot: tuple[int, int, int, int],
    label: str,
    text_fill: int,
    text_vertical: bool,
) -> None:
    x, y, w, h = slot
    font = ImageFont.load_default()
    if text_vertical:
        tmp = Image.new("1", (h, w), color=0)
        tmp_draw = ImageDraw.Draw(tmp)
        bbox = font.getbbox(label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tmp_draw.text(((h - tw) // 2, (w - th) // 2), label, fill=1, font=font)
        draw.bitmap((x, y), tmp.rotate(90, expand=True), fill=text_fill)
    else:
        bbox = font.getbbox(label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (x + (w - tw) // 2, y + (h - th) // 2), label, fill=text_fill, font=font
        )


def _draw_button(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    label: str | None,
    state: ButtonState,
    text_vertical: bool = False,
) -> None:
    """Draw a single button slot onto draw at (x, y, w, h)."""
    if label is None:
        return

    fill, text_fill = (0, 1) if state == ButtonState.ACTIVE else (1, 0)
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill)

    if state == ButtonState.DISABLED:
        _dashed_rectangle(draw, x, y, x + w - 1, y + h - 1)
    else:
        for i in range(2):
            draw.rectangle([x + i, y + i, x + w - 1 - i, y + h - 1 - i], outline=0)

    if label:
        _draw_label(draw, (x, y, w, h), label, text_fill, text_vertical)
