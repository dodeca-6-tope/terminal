"""Vertical stack layout component."""

from __future__ import annotations

from terminal.components.base import Renderable, frame
from terminal.measure import distribute


def vstack(
    *children: Renderable,
    spacing: int = 0,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    children_list = list(children)

    basis = max((c.flex_basis for c in children_list), default=0)
    r_grow = max((c.grow for c in children_list), default=0)

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

        # Separate explicit-height children from flex-grow children
        has_height = {i for i, c in enumerate(children_list) if c.height is not None}
        weights = [
            (i, c.grow)
            for i, c in enumerate(children_list)
            if c.grow and i not in has_height
        ]
        if not weights and not has_height:
            return render_unconstrained(w)

        deferred = {i for i, _ in weights} | has_height
        fixed = [
            None if i in deferred else c.render(w) for i, c in enumerate(children_list)
        ]
        used = spacing * max(0, len(children_list) - 1)
        used += sum(len(r) for r in fixed if r is not None)
        # Account for explicit-height children in space budget
        resolved_heights = {
            i: c.resolve_height(h)
            for i, c in enumerate(children_list)
            if i in has_height
        }
        used += sum(v for v in resolved_heights.values() if v is not None)
        remaining = max(0, h - used)
        shares = distribute(remaining, [wt for _, wt in weights])
        flex_heights = {i: ht for (i, _), ht in zip(weights, shares)}

        # Pass full h to explicit-height children (frame resolves their
        # spec once against h), allocated height to flex children.
        return join(
            [
                f
                if (f := fixed[i]) is not None
                else child.render(w, h)
                if i in has_height
                else child.render(w, flex_heights[i])
                for i, child in enumerate(children_list)
            ]
        )

    def render(w: int, h: int | None = None) -> list[str]:
        if h is None:
            return render_unconstrained(w)
        return render_constrained(w, h)

    return frame(Renderable(render, basis, r_grow), width, height, grow, bg, overflow)
