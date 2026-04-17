"""Scrollable viewport — ScrollState and factory.

``scroll`` is always lazy: items are data, only visible ones render.
The ``scroll(*children)`` form is sugar for pre-built nodes.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar, cast, overload

from ttyz.components.base import Node, Overflow

T = TypeVar("T")


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

    __slots__ = ("state", "items", "render_fn", "cache")
    state: ScrollState
    items: list[Any]
    render_fn: Callable[[Any, int], Node]
    cache: dict[Any, Node]


def _identity(node: Node, _: int) -> Node:
    return node


@overload
def scroll(
    items: Sequence[T],
    render_fn: Callable[[T, int], Node],
    /,
    *,
    state: ScrollState,
    width: str | None = ...,
    height: str | None = ...,
    grow: int | None = ...,
    bg: int | None = ...,
    overflow: Overflow = ...,
) -> Scroll: ...


@overload
def scroll(
    *children: Node,
    state: ScrollState,
    width: str | None = ...,
    height: str | None = ...,
    grow: int | None = ...,
    bg: int | None = ...,
    overflow: Overflow = ...,
) -> Scroll: ...


def scroll(
    *args: Any,
    state: ScrollState,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Scroll:
    """Scrollable viewport.

    Two call shapes:
        scroll(items, render_fn, *, state=...)   # data + render
        scroll(*children, *, state=...)          # pre-built nodes
    """
    items: list[Any]
    render_fn: Callable[[Any, int], Node]
    eager: tuple[Node, ...]
    if len(args) == 2 and callable(args[1]):
        raw = cast("Sequence[Any]", args[0])
        items = raw if isinstance(raw, list) else list(raw)
        render_fn = cast("Callable[[Any, int], Node]", args[1])
        eager = ()
    else:
        items = list(args)
        render_fn = _identity
        eager = args

    node = Scroll(eager, grow if grow is not None else 1, width, height, bg, overflow)
    node.state = state
    node.items = items
    node.render_fn = render_fn
    node.cache = {}
    return node
