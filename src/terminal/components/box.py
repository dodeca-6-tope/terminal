"""Box component — draws a border around a child."""

from __future__ import annotations

from terminal.components.base import Renderable, frame
from terminal.components.text import Text, truncate
from terminal.measure import display_width
from terminal.screen import clip

BORDERS: dict[str, tuple[str, str, str, str, str, str]] = {
    # (top_left, top_right, bottom_left, bottom_right, horizontal, vertical)
    "rounded": ("╭", "╮", "╰", "╯", "─", "│"),
    "normal": ("┌", "┐", "└", "┘", "─", "│"),
    "double": ("╔", "╗", "╚", "╝", "═", "║"),
    "heavy": ("┏", "┓", "┗", "┛", "━", "┃"),
}


def box(
    child: Renderable,
    *,
    style: str = "rounded",
    title: str = "",
    padding: int = 0,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    if style not in BORDERS:
        raise ValueError(f"unknown border style {style!r}")

    def inner_width(w: int) -> int:
        if child.grow:
            return max(0, w - 2)
        content_w = child.flex_basis + padding * 2
        title_w = display_width(title) + 2 if title else 0
        return max(0, min(max(content_w, title_w), w - 2))

    def top_border(inner: int) -> str:
        tl, tr, _, _, hz, _ = BORDERS[style]
        if not title:
            return f"{tl}{hz * inner}{tr}"
        label = Text(truncate(title, inner - 2, ellipsis=True))
        return f"{tl} {label} {hz * (inner - len(label) - 2)}{tr}"

    content_w = child.flex_basis + padding * 2
    title_w = display_width(title) + 2 if title else 0
    basis = max(content_w, title_w) + 2
    r_grow = child.grow

    def render(w: int, h: int | None = None) -> list[str]:
        _, _, bl, br, hz, v = BORDERS[style]
        inner = inner_width(w)
        child_h = max(0, h - 2) if h is not None else None
        child_lines = child.render(max(0, inner - padding * 2), child_h)

        top = top_border(inner)
        pad_str = " " * padding
        lines = [top]
        cw = inner - padding * 2
        for line in child_lines:
            lw = display_width(line)
            if lw > cw:
                line = clip(line, cw)
                lw = cw
            gap = inner - lw - padding * 2
            lines.append(f"{v}{pad_str}{line}{' ' * gap}{pad_str}{v}")
        lines.append(f"{bl}{hz * inner}{br}")
        return lines

    return frame(Renderable(render, basis, r_grow), width, height, grow, bg, overflow)
