"""Spacer — flexible empty space that expands along the parent's main axis."""

from __future__ import annotations

from terminal.components.base import Component


class Spacer(Component):
    def render(self, width: int, height: int | None = None) -> list[str]:
        if height is not None:
            return [""] * height
        return [" " * width]

    def flex_grow(self) -> bool:
        return True

    def flex_grow_height(self) -> bool:
        return True


def spacer() -> Spacer:
    return Spacer()
