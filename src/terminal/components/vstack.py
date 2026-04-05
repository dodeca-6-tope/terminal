"""Vertical stack layout component."""

from __future__ import annotations

from terminal.components.base import Component


class VStack(Component):
    def __init__(self, children: list[Component], *, spacing: int = 0) -> None:
        self.children = children
        self._spacing = spacing

    def flex_basis(self) -> int:
        return max((c.flex_basis() for c in self.children), default=0)

    def flex_grow(self) -> bool:
        return any(c.flex_grow() for c in self.children)

    def flex_grow_height(self) -> bool:
        return any(c.flex_grow_height() for c in self.children)

    def render(self, width: int, height: int | None = None) -> list[str]:
        if height is None:
            return self._render_unconstrained(width)
        return self._render_constrained(width, height)

    def _render_unconstrained(self, width: int) -> list[str]:
        return self._join([c.render(width) for c in self.children])

    def _render_constrained(self, width: int, height: int) -> list[str]:
        growers = [i for i, c in enumerate(self.children) if c.flex_grow_height()]
        if not growers:
            return self._render_unconstrained(width)

        fixed = [
            None if i in set(growers) else c.render(width)
            for i, c in enumerate(self.children)
        ]
        used = self._spacing * max(0, len(self.children) - 1)
        used += sum(len(r) for r in fixed if r is not None)
        per, extra = divmod(max(0, height - used), len(growers))
        heights = {g: per + (1 if j < extra else 0) for j, g in enumerate(growers)}

        return self._join(
            [
                f if (f := fixed[i]) is not None else child.render(width, heights[i])
                for i, child in enumerate(self.children)
            ]
        )

    def _join(self, parts: list[list[str]]) -> list[str]:
        if not self._spacing:
            return [line for part in parts for line in part]
        lines: list[str] = []
        for i, part in enumerate(parts):
            if i > 0:
                lines.extend([""] * self._spacing)
            lines.extend(part)
        return lines


def vstack(*children: Component, spacing: int = 0) -> VStack:
    return VStack(list(children), spacing=spacing)
