"""Horizontal stack layout component."""

from __future__ import annotations

from terminal.components.base import Renderable, frame
from terminal.measure import display_width, distribute
from terminal.screen import pad


def _wrap_chunks(strs: list[str], width: int, gap: int) -> list[str]:
    sep = " " * gap
    lines: list[str] = []
    line: list[str] = []
    line_w = 0
    for s in strs:
        s_w = display_width(s)
        needed = line_w + gap + s_w if line else s_w
        if needed > width and line:
            lines.append(sep.join(line))
            line, line_w = [s], s_w
            continue
        line.append(s)
        line_w = needed
    if line:
        lines.append(sep.join(line))
    return lines


_JUSTIFY_CONTENT = {"start", "end", "center", "between"}
_ALIGN_ITEMS = {"start", "end", "center"}


def _aligned_cell(col: list[str], row: int, max_rows: int, align: str) -> str:
    if align == "end":
        offset = max_rows - len(col)
        return col[row - offset] if row >= offset else ""
    if align == "center":
        offset = (max_rows - len(col)) // 2
        return col[row - offset] if offset <= row < offset + len(col) else ""
    return col[row] if row < len(col) else ""


def _justify_row(cells: list[str], remaining: int, spacing: int, mode: str) -> str:
    gap = " " * spacing
    joined = gap.join(cells)
    if remaining <= 0 or mode == "start":
        return joined
    if mode == "end":
        return " " * remaining + joined
    if mode == "center":
        return " " * (remaining // 2) + joined
    if mode == "between" and len(cells) > 1:
        extras = distribute(remaining, [1] * (len(cells) - 1))
        sep = [" " * (spacing + e) for e in extras]
        return "".join(c + s for c, s in zip(cells, sep)) + cells[-1]
    return joined


def _resolve_col_widths(
    act: list[Renderable], w: int, spacing: int
) -> tuple[list[int], int]:
    """Resolve column widths and leftover space for flex-grow distribution."""
    col_widths = [c.resolve_width(w) or c.flex_basis for c in act]
    weights = [(i, c.grow) for i, c in enumerate(act) if c.grow and c.width is None]
    remaining = max(0, w - sum(col_widths) - spacing * max(0, len(act) - 1))
    if weights:
        for (i, _), extra in zip(
            weights, distribute(remaining, [wt for _, wt in weights])
        ):
            col_widths[i] += extra
        remaining = 0
    return col_widths, remaining


def _render_columns(
    act: list[Renderable], col_widths: list[int], w: int, h: int | None
) -> list[list[str]]:
    """Render each child at its resolved column width."""
    columns: list[list[str]] = []
    for i, c in enumerate(act):
        cw = w if c.width is not None else col_widths[i]
        columns.append(c.render(cw, h) if c.grow else c.render(cw))
    return columns


def hstack(
    *children: Renderable,
    spacing: int = 0,
    justify_content: str = "start",
    align_items: str = "start",
    wrap: bool = False,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    if justify_content not in _JUSTIFY_CONTENT:
        raise ValueError(f"unknown justify_content {justify_content!r}")
    if align_items not in _ALIGN_ITEMS:
        raise ValueError(f"unknown align_items {align_items!r}")
    children_list = list(children)

    act = [
        c for c in children_list if c.flex_basis > 0 or c.grow or c.width is not None
    ]
    gap_total = spacing * max(0, len(act) - 1)
    basis = sum(c.flex_basis for c in act) + gap_total

    def render_wrap(w: int) -> list[str]:
        if not children_list:
            return [""]
        strs = [" ".join(c.render(w)) for c in children_list]
        return _wrap_chunks(strs, w, spacing)

    def render_fixed(w: int, h: int | None = None) -> list[str]:
        if not act:
            return [""] * h if h else [""]

        col_widths, remaining = _resolve_col_widths(act, w, spacing)
        columns = _render_columns(act, col_widths, w, h)
        max_rows = max((len(col) for col in columns), default=0)

        lines: list[str] = []
        for row in range(max_rows):
            cells = [
                pad(_aligned_cell(col, row, max_rows, align_items), col_widths[i])
                for i, col in enumerate(columns)
            ]
            lines.append(_justify_row(cells, remaining, spacing, justify_content))
        return lines

    def render(w: int, h: int | None = None) -> list[str]:
        if wrap:
            return render_wrap(w)
        return render_fixed(w, h)

    return frame(Renderable(render, basis), width, height, grow, bg, overflow)
