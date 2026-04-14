"""List — scrollable list with cursor selection."""

from __future__ import annotations

import builtins
from collections.abc import Callable, Hashable
from typing import Generic, TypeVar

from ttyz.components.base import Renderable
from ttyz.components.keyed import Keyed
from ttyz.components.scroll import ScrollState

T = TypeVar("T", bound=Keyed)


class ListState(Generic[T]):
    """Holds items and cursor position for a List component."""

    def __init__(self, items: builtins.list[T] | tuple[T, ...] = ()) -> None:
        self.items = builtins.list(items)
        self.cursor = 0
        self.scroll = ScrollState()

    @property
    def current(self) -> T | None:
        return self.items[self.cursor] if self.items else None

    def clamp(self, index: int) -> int:
        return max(0, min(index, self.total - 1)) if self.total else 0

    def move(self, delta: int) -> None:
        self.cursor = self.clamp(self.cursor + delta)

    def move_to(self, index: int) -> None:
        self.cursor = self.clamp(index)

    def set_items(self, items: builtins.list[T] | tuple[T, ...]) -> None:
        prev = self.current.key if self.current else None
        self.items = builtins.list(items)
        if prev is not None:
            idx = next(
                (i for i, x in enumerate(self.items) if x.key == prev),
                self.cursor,
            )
            self.move_to(idx)
        else:
            self.move_to(self.cursor)

    @property
    def offset(self) -> int:
        return self.scroll.offset

    @property
    def height(self) -> int:
        return self.scroll.height

    @property
    def total(self) -> int:
        return len(self.items)


def list(
    state: ListState[T],
    render_fn: Callable[[T, bool], Renderable],
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    cache: dict[Hashable, tuple[int, bool, int, builtins.list[str]]] = {}

    def render_item(i: int, w: int) -> builtins.list[str]:
        item = state.items[i]
        sel = i == state.cursor
        entry = cache.get(item.key)
        if (
            entry is not None
            and entry[0] == id(item)
            and entry[1] == sel
            and entry[2] == w
        ):
            return entry[3]
        rendered = render_fn(item, sel).render(w)
        cache[item.key] = (id(item), sel, w, rendered)
        return rendered

    def render(w: int, h: int | None = None) -> builtins.list[str]:
        state.cursor = state.clamp(state.cursor)
        state.scroll.scroll_to_visible(state.cursor)

        if not isinstance(h, int) or h <= 0:
            return []

        state.scroll.height = h
        state.scroll.total = state.total
        state.scroll.offset = max(0, min(state.scroll.offset, state.scroll.max_offset))

        lines: builtins.list[str] = []
        for i in range(state.scroll.offset, state.total):
            rendered = render_item(i, w)
            remaining = h - len(lines)
            if len(rendered) >= remaining:
                lines.extend(rendered[:remaining])
                break
            lines.extend(rendered)
        if len(lines) < h:
            lines.extend([""] * (h - len(lines)))
        return lines

    return Renderable(
        render,
        0,
        grow if grow is not None else 1,
        width=width,
        height=height,
        bg=bg,
        overflow=overflow,
    )
