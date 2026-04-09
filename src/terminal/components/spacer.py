"""Flexible space that expands along the major axis of its containing stack.

If not contained in a stack, it expands on both axes.
"""

from __future__ import annotations

from terminal.components.base import Renderable


def spacer(min_length: int = 0) -> Renderable:
    """Create a flexible spacer that pushes siblings apart in a stack."""

    def render(w: int, h: int | None = None) -> list[str]:
        return [""] * h if h is not None else [""]

    return Renderable(render, flex_basis=min_length, grow=1)
