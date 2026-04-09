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

    def active() -> list[Renderable]:
        return [
            c
            for c in children_list
            if c.flex_basis > 0 or c.grow or c.width is not None
        ]

    act = active()
    gap_total = spacing * max(0, len(act) - 1)
    basis = sum(c.flex_basis for c in act) + gap_total

    grow_w = max((c.grow for c in children_list), default=0)

    def justify_between(cells: list[str], remaining: int) -> str:
        gaps = len(cells) - 1
        per_gap = remaining // gaps
        extra = remaining % gaps
        parts: list[str] = []
        for i, cell in enumerate(cells):
            parts.append(cell)
            if i < gaps:
                parts.append(" " * (spacing + per_gap + (1 if i < extra else 0)))
        return "".join(parts)

    def justify_row(cells: list[str], remaining: int) -> str:
        gap = " " * spacing
        joined = gap.join(cells)

        if remaining <= 0 or justify_content == "start":
            return joined
        if justify_content == "end":
            return " " * remaining + joined
        if justify_content == "center":
            return " " * (remaining // 2) + joined
        if justify_content == "between" and len(cells) > 1:
            return justify_between(cells, remaining)
        return joined

    def render_wrap(w: int) -> list[str]:
        if not children_list:
            return [""]
        strs = [" ".join(c.render(w)) for c in children_list]
        return _wrap_chunks(strs, w, spacing)

    def render_fixed(w: int, h: int | None = None) -> list[str]:
        act = active()
        if not act:
            return [""] * h if h else [""]

        # Resolve explicit-width children for layout; flex children use basis
        col_widths = [c.resolve_width(w) or c.flex_basis for c in act]
        # Flex-grow distribution (only children without explicit width)
        weights = [(i, c.grow) for i, c in enumerate(act) if c.grow and c.width is None]
        gt = spacing * max(0, len(act) - 1)
        remaining = max(0, w - sum(col_widths) - gt)

        if weights:
            for (i, _), extra in zip(
                weights, distribute(remaining, [wt for _, wt in weights])
            ):
                col_widths[i] += extra
            remaining = 0

        # Render: pass full w to explicit-width children (frame resolves
        # their spec once against w), allocated width to flex children.
        columns = [
            c.render(w if c.width is not None else col_widths[i], h)
            if c.grow
            else c.render(w if c.width is not None else col_widths[i])
            for i, c in enumerate(act)
        ]
        max_rows = max((len(col) for col in columns), default=0)

        lines: list[str] = []
        for row in range(max_rows):
            cells: list[str] = []
            for i, col in enumerate(columns):
                cell = col[row] if row < len(col) else ""
                if align_items == "end":
                    cell = (
                        col[row - max_rows + len(col)]
                        if row >= max_rows - len(col)
                        else ""
                    )
                elif align_items == "center":
                    offset = (max_rows - len(col)) // 2
                    cell = (
                        col[row - offset] if offset <= row < offset + len(col) else ""
                    )
                cells.append(pad(cell, col_widths[i]))
            lines.append(justify_row(cells, remaining))
        return lines

    def render(w: int, h: int | None = None) -> list[str]:
        if wrap:
            return render_wrap(w)
        return render_fixed(w, h)

    return frame(Renderable(render, basis, grow_w), width, height, grow, bg, overflow)
