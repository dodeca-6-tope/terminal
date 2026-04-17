"""Conditional rendering component."""

from __future__ import annotations

from ttyz.components.base import Node, Overflow


class Cond(Node):
    """Conditional node — renders child when present, empty otherwise."""

    __slots__ = ()


def cond(
    condition: object,
    child: Node,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: Overflow = "visible",
) -> Node:
    if not condition:
        return Node(
            grow=grow if grow is not None else 0,
            width=width,
            height=height,
            bg=bg,
            overflow=overflow,
        )

    if (
        width is None
        and height is None
        and bg is None
        and overflow == "visible"
        and (grow is None or grow == child.grow)
    ):
        return child

    return Cond(
        (child,),
        grow if grow is not None else child.grow,
        width,
        height,
        bg,
        overflow,
    )
