"""Vertical stack layout component."""

from __future__ import annotations

from terminal.components.base import Renderable, frame
from terminal.measure import distribute


def vstack(
    *children: Renderable,
    spacing: int = 0,
    width: str | None = None,
    height: str | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    children_list = list(children)

    basis = max((c.flex_basis for c in children_list), default=0)
    grow_w = max(
        (c.flex_grow_width for c in children_list),
        default=0,
    )
    grow_h = max((c.flex_grow_height for c in children_list), default=0)

    def join(parts: list[list[str]]) -> list[str]:
        if not spacing:
            return [line for part in parts for line in part]
        lines: list[str] = []
        for i, part in enumerate(parts):
            if i > 0:
                lines.extend([""] * spacing)
            lines.extend(part)
        return lines

    def render_unconstrained(w: int) -> list[str]:
        return join([c.render(w) for c in children_list])

    def render_constrained(w: int, h: int) -> list[str]:
        if not children_list:
            return [""] * h

        weights = [
            (i, c.flex_grow_height)
            for i, c in enumerate(children_list)
            if c.flex_grow_height
        ]
        if not weights:
            return render_unconstrained(w)

        grower_set = {i for i, _ in weights}
        fixed = [
            None if i in grower_set else c.render(w)
            for i, c in enumerate(children_list)
        ]
        used = spacing * max(0, len(children_list) - 1)
        used += sum(len(r) for r in fixed if r is not None)
        remaining = max(0, h - used)
        shares = distribute(remaining, [wt for _, wt in weights])
        heights = {i: ht for (i, _), ht in zip(weights, shares)}

        return join(
            [
                f if (f := fixed[i]) is not None else child.render(w, heights[i])
                for i, child in enumerate(children_list)
            ]
        )

    def render(w: int, h: int | None = None) -> list[str]:
        if h is None:
            return render_unconstrained(w)
        return render_constrained(w, h)

    return frame(Renderable(render, basis, grow_w, grow_h), width, height, bg, overflow)
