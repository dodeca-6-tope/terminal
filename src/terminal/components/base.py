"""Renderable dataclass and layout helpers.

``Renderable`` is the core type — a render function plus flex properties.
``frame`` wraps a Renderable with size constraints and background.

Accepted size values:
    None       — no constraint (default)
    "50%"      — percentage of the parent dimension (falls back to
                 terminal size when no parent is available)
    "28"       — fixed number of columns / rows
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

RenderFn = Callable[..., list[str]]


@dataclass
class Renderable:
    render: RenderFn
    flex_basis: int = 0
    flex_grow_width: int = 0
    flex_grow_height: int = 0
    width: int | None = None
    height: int | None = None


_OVERFLOW = {"visible", "hidden", "ellipsis"}


def frame(
    child: Renderable,
    width: str | None = None,
    height: str | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    """Wrap *child* with size constraints and/or background."""
    if overflow not in _OVERFLOW:
        raise ValueError(f"unknown overflow {overflow!r}")
    if width is None and height is None and bg is None and overflow == "visible":
        return child

    fw = _fixed(width)
    fh = _fixed(height)
    basis = fw if fw is not None else child.flex_basis
    grow_w = 0 if fw is not None else (_pct(width) or child.flex_grow_width)
    grow_h = 0 if fh is not None else (_pct(height) or child.flex_grow_height)

    def render(w: int, h: int | None = None) -> list[str]:
        rw = _resolve(width, w, 0)
        rh = _resolve(height, h, 1)
        cw = min(rw, w) if rw is not None else w
        lines = child.render(
            cw,
            min(rh, h) if rh is not None and h is not None else (rh or h),
        )
        if rw is not None and overflow != "visible":
            from terminal.measure import display_width
            from terminal.screen import clip, clip_and_pad

            if overflow == "ellipsis":
                lines = [
                    clip(l, cw - 1) + "…" if display_width(l) > cw else l for l in lines
                ]
            lines = [clip_and_pad(l, cw) for l in lines]
        if rh is not None and len(lines) < rh:
            lines.extend([""] * (rh - len(lines)))
        if bg is not None:
            lines = _apply_bg(lines, bg, cw)
        return lines

    return Renderable(render, basis, grow_w, grow_h, width=fw, height=fh)


def _apply_bg(lines: list[str], color: int, width: int) -> list[str]:
    from terminal.screen import pad

    bg = f"\033[48;5;{color}m"
    reset = "\033[0m"
    return [
        f"{bg}{pad(line.replace(reset, reset + bg), width)}{reset}" for line in lines
    ]


def _resolve(value: str | None, parent: int | None, axis: int) -> int | None:
    if value is None:
        return None
    if value.endswith("%"):
        base = parent if parent is not None else os.get_terminal_size()[axis]
        return base * int(value[:-1]) // 100
    return int(value)


def _pct(value: str | None) -> int:
    if value is None or not value.endswith("%"):
        return 0
    return int(value[:-1])


def _fixed(value: str | None) -> int | None:
    if value is None or value.endswith("%"):
        return None
    return int(value)
