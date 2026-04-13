"""Text component — renders strings with optional truncation, wrap, padding."""

from __future__ import annotations

from ttyz.buffer import c_make_text, set_text_render_fallback
from ttyz.components.base import Renderable, frame
from ttyz.measure import char_width, display_width, slice_at_width, strip_ansi


def _wrap_line(line: str, width: int) -> list[str]:
    """Word-wrap a line, falling back to character-wrap for long words."""
    if width <= 0:
        return [line]
    if display_width(line) <= width:
        return [line]
    lines: list[str] = []
    current = ""
    for word in line.split(" "):
        joined = f"{current} {word}" if current else word
        if display_width(joined) <= width:
            current = joined
            continue
        if current:
            lines.append(current)
        current = ""
        while display_width(word) > width:
            chunk = slice_at_width(word, width)
            lines.append(chunk)
            word = word[len(chunk) :]
        current = word
    if current:
        lines.append(current)
    return lines or [""]


def _truncate_line(line: str, width: int, mode: str) -> str:
    """Truncate a line with ellipsis according to the given mode."""
    stripped = strip_ansi(line)
    if display_width(stripped) <= width:
        return line
    if width <= 0:
        return ""
    if mode == "head":
        budget, w, i = width - 1, 0, len(stripped)
        while i > 0:
            cw = char_width(stripped[i - 1])
            if w + cw > budget:
                break
            w += cw
            i -= 1
        return "…" + " " * (budget - w) + stripped[i:]
    if mode == "middle":
        left_w = (width - 1) // 2
        right_w = width - 1 - left_w
        return (
            slice_at_width(stripped, left_w)
            + "…"
            + slice_at_width(stripped[::-1], right_w)[::-1]
        )
    # tail (default)
    return slice_at_width(stripped, width - 1) + "…"


def _text_full_render(
    lines: list[str], w: int, pl: int, pr: int, truncation: str | None, wrap: bool
) -> list[str]:
    """Full render path for text with wrap/truncation — Python fallback for C."""
    inner = w - pl - pr
    chunks: list[str] = []
    for line in lines:
        if wrap and inner > 0:
            chunks.extend(_wrap_line(line, inner))
        elif truncation and inner > 0:
            chunks.append(_truncate_line(line, inner, truncation))
        else:
            chunks.append(line)
    if not pl and not pr:
        return chunks
    pad_l = " " * pl
    pad_r = " " * pr
    return [f"{pad_l}{c}{pad_r}" for c in chunks]


# Register the Python fallback so CTextRender can call it for wrap/non-ASCII.
set_text_render_fallback(_text_full_render)


def text(
    value: object = "",
    *,
    wrap: bool = False,
    truncation: str | None = None,
    padding: int = 0,
    padding_left: int | None = None,
    padding_right: int | None = None,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    pl = padding if padding_left is None else padding_left
    pr = padding if padding_right is None else padding_right

    # C: parse + display_width + TextRender creation in one call.
    render, _, visible_w = c_make_text(value, truncation, pl, pr, wrap)
    basis = visible_w + pl + pr

    # Skip frame() indirection when no constraints — avoids an extra Renderable.
    if width is None and height is None and bg is None and overflow == "visible":
        return Renderable(render, basis, grow or 0)
    return frame(Renderable(render, basis), width, height, grow, bg, overflow)
