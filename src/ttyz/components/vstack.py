"""Vertical stack layout component — data class and factory."""

from __future__ import annotations

from collections.abc import Sequence

from ttyz.components.base import Node, Overflow, is_eager_backing, resolve_children


class VStack(Node):
    """Vertical stack node."""

    __slots__ = ("spacing", "needs_measure_pass")
    spacing: int
    needs_measure_pass: bool


def vstack(
    *children: Node | Sequence[Node],
    spacing: int = 0,
    width: str | None = None,
    height: str | None = None,
    grow: int = 0,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> VStack:
    backing = resolve_children(children)
    needs_measure_pass = is_eager_backing(backing) and any(
        c.grow or c.height is not None for c in backing
    )

    node = VStack(backing, grow, width, height, bg, overflow)
    node.spacing = spacing
    node.needs_measure_pass = needs_measure_pass
    return node
