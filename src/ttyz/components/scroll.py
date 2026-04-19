"""Scrollable viewport — ScrollState and factory."""

from __future__ import annotations

from collections.abc import Sequence
from typing import overload

from ttyz.components.base import Node, Overflow


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
        diff = self.total - self.height
        return diff if diff > 0 else 0


class Scroll(Node):
    """Scrollable viewport node."""

    __slots__ = ("state",)
    state: ScrollState


@overload
def scroll(
    children: Sequence[Node],
    /,
    *,
    state: ScrollState,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Scroll: ...
@overload
def scroll(
    *children: Node,
    state: ScrollState,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Scroll: ...
def scroll(
    *children: Node | Sequence[Node],
    state: ScrollState,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Scroll:
    # Single non-Node positional → treat as the Sequence backing (lazy-friendly).
    # Otherwise varargs of Nodes → bundle into a tuple.
    if len(children) == 1 and not isinstance(children[0], Node):
        backing: Sequence[Node] = children[0]
    else:
        backing = children  # type: ignore[assignment]
    node = Scroll(backing, grow if grow is not None else 1, width, height, bg, overflow)
    node.state = state
    return node
