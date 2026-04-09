"""Vertical stack layout component."""

from __future__ import annotations

from terminal.components.base import Renderable, frame
from terminal.measure import distribute


def _resolve_flex_heights(
    children: list[Renderable],
    w: int,
    h: int,
    spacing: int,
) -> tuple[list[list[str] | None], dict[int, int], set[int]]:
    """Pre-render non-flex children and compute flex-grow row allocations.

    Returns (rendered, flex_heights, has_height) where rendered[i] is None
    for deferred children and flex_heights maps grow-child indices to heights.
    """
    has_height = {i for i, c in enumerate(children) if c.height is not None}
    weights = [
        (i, c.grow) for i, c in enumerate(children) if c.grow and i not in has_height
    ]
    deferred = {i for i, _ in weights} | has_height
    rendered: list[list[str] | None] = [
        None if i in deferred else c.render(w) for i, c in enumerate(children)
    ]
    used = spacing * max(0, len(children) - 1)
    used += sum(len(r) for r in rendered if r is not None)
    resolved_heights = {
        i: c.resolve_height(h) for i, c in enumerate(children) if i in has_height
    }
    used += sum(v for v in resolved_heights.values() if v is not None)
    shares = distribute(max(0, h - used), [wt for _, wt in weights])
    flex_heights = {i: ht for (i, _), ht in zip(weights, shares)}
    return rendered, flex_heights, has_height


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

        has_flex = any(c.grow or c.height is not None for c in children_list)
        if not has_flex:
            return render_unconstrained(w)

        rendered, flex_heights, has_height = _resolve_flex_heights(
            children_list, w, h, spacing
        )
        return join(
            [
                f
                if (f := rendered[i]) is not None
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

    return frame(Renderable(render, basis), width, height, grow, bg, overflow)
