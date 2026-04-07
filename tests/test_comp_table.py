"""Tests for Table component."""

from terminal import table, table_row, text
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_aligns_columns():
    tbl = table(
        table_row(text("a"), text("bb")),
        table_row(text("ccc"), text("d")),
    )
    lines = clean(tbl.render(80))
    assert len(lines) == 2
    assert lines[0].index("bb") == lines[1].index("d")


def test_single_row():
    line = clean(table(table_row(text("x"), text("y"))).render(80))[0]
    assert "x" in line
    assert "y" in line


def test_empty():
    assert clean(table().render(80)) == [""]


def test_fill_column():
    tbl = table(table_row(text("id"), text("long title here", width="100%")))
    lines = clean(tbl.render(30))
    assert len(lines[0]) <= 30


def test_spacing():
    line = clean(table(table_row(text("a"), text("b")), spacing=3).render(80))[0]
    a_end = line.index("a") + 1
    b_start = line.index("b")
    assert b_start - a_end == 3


def test_jagged_rows():
    """Rows with fewer cells than the widest row get padded."""
    tbl = table(
        table_row(text("a"), text("b"), text("c")),
        table_row(text("x")),
    )
    lines = clean(tbl.render(80))
    assert len(lines) == 2
    # second row should still have spacing for 3 columns
    assert len(lines[1]) == len(lines[0])


def test_multiple_fill_columns():
    """Two fill columns share remaining space."""
    tbl = table(
        table_row(
            text("id"),
            text("name", width="100%"),
            text("desc", width="100%"),
        )
    )
    lines = clean(tbl.render(42))
    # id=2 + spacing(2) + two fill cols should sum to 42
    assert len(lines[0]) == 42


# ── flex_grow propagation ───────────────────────────────────────────


def test_flex_grow_with_fill_column():
    tbl = table(table_row(text("id"), text("name", width="100%")))
    assert tbl.flex_grow_width


def test_flex_grow_false_without_fill():
    tbl = table(table_row(text("a"), text("b")))
    assert not tbl.flex_grow_width
