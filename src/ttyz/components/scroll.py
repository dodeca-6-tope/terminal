"""Scrollable viewport — renders only the visible children."""

from __future__ import annotations

from collections.abc import Iterator

from ttyz.components.base import Renderable, frame


def fill_viewport(items: Iterator[Renderable], w: int, h: int) -> list[str]:
    """Render items into a viewport of h rows, stopping when full."""
    lines: list[str] = []
    for child in items:
        rendered = child.render(w)
        remaining = h - len(lines)
        if len(rendered) >= remaining:
            lines.extend(rendered[:remaining])
            break
        lines.extend(rendered)
    if len(lines) < h:
        lines.extend([""] * (h - len(lines)))
    return lines


class ScrollState:
    """Tracks scroll offset. Scroll writes resolved height/total during render."""

    def __init__(self, follow: bool = False) -> None:
        self.offset = 0
        self.height = 0
        self.total = 0
        self.follow = follow

    def scroll_up(self, n: int = 1) -> None:
        self.offset = max(0, self.offset - n)
        self.follow = False

    def scroll_down(self, n: int = 1) -> None:
        self.offset = min(self.max_offset, self.offset + n)

    def page_up(self) -> None:
        self.scroll_up(self.height)

    def page_down(self) -> None:
        self.scroll_down(self.height)

    def scroll_to_top(self) -> None:
        self.offset = 0
        self.follow = False

    def scroll_to_bottom(self) -> None:
        self.offset = self.max_offset
        self.follow = True

    def scroll_to_visible(self, index: int) -> None:
        if index < self.offset:
            self.offset = index
        elif index >= self.offset + self.height:
            self.offset = index - self.height + 1

    @property
    def max_offset(self) -> int:
        return max(0, self.total - self.height)


def scroll(
    *children: Renderable,
    state: ScrollState,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    children_list = list(children)

    basis = max((c.flex_basis for c in children_list), default=0)

    def render(w: int, h: int | None = None) -> list[str]:
        if not isinstance(h, int) or h <= 0:
            return []

        state.height = h
        state.total = len(children_list)
        if state.follow:
            state.offset = state.max_offset
        state.offset = max(0, min(state.offset, state.max_offset))
        if state.total > state.height and state.offset >= state.max_offset:
            state.follow = True

        return fill_viewport(iter(children_list[state.offset :]), w, h)

    return frame(Renderable(render, basis, 1), width, height, grow, bg, overflow)
