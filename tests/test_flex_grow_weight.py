"""Tests for weighted flex_grow distribution."""

from terminal import hstack, text, vstack
from terminal.components.base import Component
from terminal.components.table import table, table_row
from terminal.measure import display_width, strip_ansi


class Weighted(Component):
    """Test component with configurable grow weight."""

    def __init__(self, label: str, grow: int = 0, grow_height: int = 0) -> None:
        self._label = label
        self._grow = grow
        self._grow_height = grow_height

    def flex_grow_width(self) -> int:
        return self._grow

    def flex_grow_height(self) -> int:
        return self._grow_height

    def render(self, width: int, height: int | None = None) -> list[str]:
        lines = [self._label[:width].ljust(width)]
        if height is not None:
            while len(lines) < height:
                lines.append(" " * width)
        return lines


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


# ── HStack weighted ────────────────────────────────────────────────


def test_hstack_equal_weights():
    """Two children with weight=1 split evenly (same as old behavior)."""
    a = Weighted("A", grow=1)
    b = Weighted("B", grow=1)
    lines = clean(hstack(a, b).render(20))
    assert len(lines) == 1
    assert display_width(lines[0]) == 20
    # Each gets 10 cols
    assert lines[0][:10].strip() == "A"
    assert lines[0][10:].strip() == "B"


def test_hstack_2_to_1_weight():
    """Weight 2 gets twice the space of weight 1."""
    a = Weighted("A", grow=2)
    b = Weighted("B", grow=1)
    lines = clean(hstack(a, b).render(30))
    # A gets 20, B gets 10
    assert lines[0][:20].strip() == "A"
    assert lines[0][20:].strip() == "B"


def test_hstack_3_to_1_weight():
    a = Weighted("A", grow=3)
    b = Weighted("B", grow=1)
    lines = clean(hstack(a, b).render(40))
    # A gets 30, B gets 10
    assert display_width(lines[0][:30].rstrip()) <= 30
    assert lines[0][:30].strip() == "A"
    assert lines[0][30:].strip() == "B"


def test_hstack_uneven_remainder():
    """Remainder pixels distributed via cumulative rounding."""
    a = Weighted("A", grow=1)
    b = Weighted("B", grow=1)
    c = Weighted("C", grow=1)
    lines = clean(hstack(a, b, c).render(20))
    # 20*1//3=6, 20*2//3=13, 20*3//3=20 → A=6, B=7, C=7
    widths = [6, 7, 7]
    pos = 0
    for i, w in enumerate(widths):
        cell = lines[0][pos : pos + w]
        assert cell.strip() == chr(ord("A") + i)
        pos += w


def test_hstack_mixed_fixed_and_weighted():
    """Fixed-basis child + two weighted growers."""
    fixed = text("XX")  # basis=2, no grow
    a = Weighted("A", grow=1)
    b = Weighted("B", grow=2)
    lines = clean(hstack(fixed, a, b).render(32))
    # fixed=2, remaining=30, A=10, B=20
    assert lines[0][:2] == "XX"
    assert lines[0][2:12].strip() == "A"
    assert lines[0][12:].strip() == "B"


def test_hstack_weight_with_spacing():
    a = Weighted("A", grow=1)
    b = Weighted("B", grow=1)
    lines = clean(hstack(a, b, spacing=2).render(22))
    # 22 - 2 spacing = 20, split 10/10
    assert lines[0][:10].strip() == "A"
    assert lines[0][10:12] == "  "
    assert lines[0][12:].strip() == "B"


# ── VStack weighted ────────────────────────────────────────────────


def test_vstack_equal_height_weights():
    a = Weighted("A", grow_height=1)
    b = Weighted("B", grow_height=1)
    lines = vstack(a, b).render(10, 20)
    assert len(lines) == 20
    # Each gets 10 rows
    assert lines[0].strip() == "A"
    assert lines[10].strip() == "B"


def test_vstack_2_to_1_height():
    a = Weighted("A", grow_height=2)
    b = Weighted("B", grow_height=1)
    lines = vstack(a, b).render(10, 30)
    assert len(lines) == 30
    # A gets 20, B gets 10
    assert lines[0].strip() == "A"
    assert lines[20].strip() == "B"


def test_vstack_mixed_fixed_and_weighted():
    header = text("HEAD")  # 1 line, no grow_height
    a = Weighted("A", grow_height=1)
    b = Weighted("B", grow_height=2)
    lines = vstack(header, a, b).render(10, 31)
    assert len(lines) == 31
    # header=1, remaining=30 → A=10, B=20
    assert lines[0].strip() == "HEAD"
    assert lines[1].strip() == "A"
    assert lines[11].strip() == "B"


def test_vstack_uneven_height_remainder():
    a = Weighted("A", grow_height=1)
    b = Weighted("B", grow_height=1)
    c = Weighted("C", grow_height=1)
    lines = vstack(a, b, c).render(5, 20)
    # 20*1//3=6, 20*2//3=13, 20*3//3=20 → A=6, B=7, C=7
    assert len(lines) == 20
    assert lines[0].strip() == "A"
    assert lines[6].strip() == "B"
    assert lines[13].strip() == "C"


# ── Table weighted ─────────────────────────────────────────────────


def test_table_weighted_columns():
    a = Weighted("A", grow=2)
    b = Weighted("B", grow=1)
    tbl = table(table_row(a, b), spacing=0)
    lines = clean(tbl.render(30))
    # A gets 20, B gets 10
    assert lines[0][:20].strip() == "A"
    assert lines[0][20:].strip() == "B"


def test_table_weighted_with_fixed():
    fixed = text("XX")  # basis=2
    a = Weighted("A", grow=1)
    b = Weighted("B", grow=3)
    tbl = table(table_row(fixed, a, b), spacing=0)
    lines = clean(tbl.render(30))
    # fixed=2, remaining=28, A=7, B=21
    assert lines[0][:2] == "XX"
    assert lines[0][2:9].strip() == "A"
    assert lines[0][9:].strip() == "B"


# ── Protocol ───────────────────────────────────────────────────────


def test_default_flex_grow_is_zero():
    c = Component()
    assert c.flex_grow_width() == 0
    assert c.flex_grow_height() == 0


def test_weighted_component_returns_weight():
    w = Weighted("x", grow=3, grow_height=5)
    assert w.flex_grow_width() == 3
    assert w.flex_grow_height() == 5
