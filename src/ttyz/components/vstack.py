"""Vertical stack layout component — data class and factory."""

from __future__ import annotations

from ttyz.components.base import Node, Overflow


class VStack(Node):
    """Vertical stack node."""

    __slots__ = ("spacing", "has_flex")
    spacing: int
    has_flex: bool


def vstack(
    *children: Node,
    spacing: int = 0,
    width: str | None = None,
    height: str | None = None,
    grow: int = 0,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> VStack:
    has_flex = any(c.grow or c.height is not None for c in children)

    node = VStack(children, grow, width, height, bg, overflow)
    node.spacing = spacing
    node.has_flex = has_flex
    return node
