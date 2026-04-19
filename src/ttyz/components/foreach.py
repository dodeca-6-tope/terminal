"""Foreach component — lazily render a list of items."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Generic, TypeVar

from ttyz.components.base import Node, Overflow

T = TypeVar("T")


class _ForeachChildren(Sequence[Node], Generic[T]):
    """Sequence of nodes produced on demand by calling ``render_fn(item, i)``."""

    __slots__ = ("_items", "_render_fn")

    def __init__(self, items: Sequence[T], render_fn: Callable[[T, int], Node]) -> None:
        self._items = items
        self._render_fn = render_fn

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, i: int | slice) -> Node:  # type: ignore[override]
        if isinstance(i, slice):
            raise TypeError("Foreach children do not support slicing")
        return self._render_fn(self._items[i], i)


class Foreach(Node):
    """Foreach node — children produced lazily from a sequence."""

    __slots__ = ()


def foreach(
    items: Sequence[T],
    render_fn: Callable[[T, int], Node],
    width: str | None = None,
    height: str | None = None,
    grow: int = 0,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Foreach:
    return Foreach(
        _ForeachChildren(items, render_fn), grow, width, height, bg, overflow
    )
