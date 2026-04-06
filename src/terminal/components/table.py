"""Table component — columnar layout with auto-sized columns."""

from __future__ import annotations

from terminal.components.base import Component
from terminal.screen import pad


class TableRow:
    """A row of components for use inside a Table."""

    def __init__(self, cells: list[Component]) -> None:
        self.cells = cells


class Table(Component):
    def __init__(self, rows: list[TableRow], *, spacing: int = 1) -> None:
        self._rows = rows
        self._spacing = spacing
        if rows:
            self._col_widths, self._grow_cols = self._measure_columns()
        else:
            self._col_widths, self._grow_cols = [], set[int]()

    def _measure_columns(self) -> tuple[list[int], set[int]]:
        """Return (col_widths, grow_cols) from natural sizes."""
        num_cols = max(len(r.cells) for r in self._rows)
        cells = [(ci, cell) for row in self._rows for ci, cell in enumerate(row.cells)]
        col_widths = [0] * num_cols
        grow_cols: set[int] = set()
        for ci, cell in cells:
            col_widths[ci] = max(col_widths[ci], cell.flex_basis())
            if cell.flex_grow():
                grow_cols.add(ci)
        return col_widths, grow_cols

    def _resolve_widths(self, width: int) -> list[int]:
        """Return col_widths with grow columns distributed."""
        col_widths, grow_cols = list(self._col_widths), self._grow_cols
        if grow_cols:
            gap_total = self._spacing * max(0, len(col_widths) - 1)
            fixed = (
                sum(w for ci, w in enumerate(col_widths) if ci not in grow_cols)
                + gap_total
            )
            remaining = max(0, width - fixed)
            per = remaining // len(grow_cols)
            extra = remaining % len(grow_cols)
            for j, ci in enumerate(sorted(grow_cols)):
                col_widths[ci] = per + (1 if j < extra else 0)
        return col_widths

    def render(self, width: int, height: int | None = None) -> list[str]:
        if not self._rows:
            return [""]
        col_widths = self._resolve_widths(width)
        if not col_widths:
            return [""]
        sep = " " * self._spacing
        return [_render_row(row, col_widths, sep) for row in self._rows]

    def flex_basis(self) -> int:
        if not self._rows:
            return 0
        gap_total = self._spacing * max(0, len(self._col_widths) - 1)
        return sum(self._col_widths) + gap_total

    def flex_grow(self) -> bool:
        return len(self._grow_cols) > 0


_empty = Component()


def _render_row(row: TableRow, col_widths: list[int], sep: str) -> str:
    parts: list[str] = []
    for ci, w in enumerate(col_widths):
        cell = row.cells[ci] if ci < len(row.cells) else _empty
        rendered = cell.render(w)
        content = rendered[0] if rendered else ""
        parts.append(pad(content, w))
    return sep.join(parts)


def table_row(*cells: Component) -> TableRow:
    return TableRow(list(cells))


def table(*rows: TableRow, spacing: int = 1) -> Table:
    return Table(list(rows), spacing=spacing)
