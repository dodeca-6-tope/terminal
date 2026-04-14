"""Sole Python gateway to the C extension (terminal.cbuf).

All other modules import C functions through here, keeping a single
point of coupling to the native layer.
"""

from ttyz.cbuf import (
    Buffer,
    Renderable,
    char_width,
    distribute,
    flex_distribute,
    make_text_render,
    pad_columns,
    parse_line,
    place_at_offsets,
    render_diff,
    render_full,
    set_text_render_fallback,
    slice_at_width,
    strip_ansi,
    truncate,
)
from ttyz.cbuf import (
    display_width as c_display_width,
)

__all__ = [
    "Buffer",
    "Renderable",
    "c_display_width",
    "make_text_render",
    "char_width",
    "distribute",
    "pad_columns",
    "parse_line",
    "render_diff",
    "place_at_offsets",
    "render_full",
    "flex_distribute",
    "set_text_render_fallback",
    "slice_at_width",
    "strip_ansi",
    "truncate",
]
