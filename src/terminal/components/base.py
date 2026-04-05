"""Component protocol.

Every component implements:

    render(width, height=None) -> list[str]
        Render into lines that fit within `width` columns.
        When `height` is given, the component should produce exactly that
        many lines (used by height-aware containers like VStack).
        When `height` is None, produce as many lines as the content needs.

    flex_basis() -> int
        Preferred width in columns. Used by HStack and Table to allocate
        space before distributing remaining width to growers. Default: 0.

    flex_grow() -> bool
        Whether to expand horizontally to fill remaining width in an
        HStack or Table. Default: False.

    flex_grow_height() -> bool
        Whether to expand vertically to fill remaining height in a
        VStack. Default: False.
"""

from __future__ import annotations


class Component:
    def render(self, width: int, height: int | None = None) -> list[str]:
        return []

    def flex_basis(self) -> int:
        return 0

    def flex_grow(self) -> bool:
        return False

    def flex_grow_height(self) -> bool:
        return False
