"""Node base class.

``Node`` is a plain data node in the component tree.  Each component
type is a ``Node`` subclass that adds component-specific slots but
no render/measure logic — all rendering lives in ``render.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, TypeAlias

RenderFn: TypeAlias = Callable[..., list[str]]
Overflow: TypeAlias = Literal["visible", "hidden"]
Align: TypeAlias = Literal["start", "end", "center"]
Justify: TypeAlias = Literal["start", "end", "center", "between"]


class Node:
    """Base data node in the component tree."""

    __slots__ = ("children", "grow", "width", "height", "bg", "overflow")
    children: tuple[Node, ...]
    grow: int
    width: str | None
    height: str | None
    bg: int | None
    overflow: Overflow

    def __init__(
        self,
        children: tuple[Node, ...] = (),
        grow: int = 0,
        width: str | None = None,
        height: str | None = None,
        bg: int | None = None,
        overflow: Overflow = "visible",
    ) -> None:
        self.children = children
        self.grow = grow
        self.width = width
        self.height = height
        self.bg = bg
        self.overflow = overflow


class Custom(Node):
    """Node wrapping a raw render function — escape hatch for custom components."""

    __slots__ = ("render_fn",)
    render_fn: RenderFn

    def __init__(
        self,
        render_fn: RenderFn,
        grow: int = 0,
        width: str | None = None,
        height: str | None = None,
        bg: int | None = None,
        overflow: Overflow = "visible",
    ) -> None:
        super().__init__((), grow, width, height, bg, overflow)
        self.render_fn = render_fn
