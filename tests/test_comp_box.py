"""Tests for Box component."""

from terminal import box, scroll, text, vstack
from terminal.components.scroll import ScrollState
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_basic_rounded():
    b = box(text("hello"))
    lines = clean(b.render(20))
    assert lines[0].startswith("╭")
    assert lines[0].endswith("╮")
    assert lines[-1].startswith("╰")
    assert lines[-1].endswith("╯")
    assert "hello" in lines[1]


def test_basic_normal():
    lines = clean(box(text("hi"), style="normal").render(20))
    assert lines[0].startswith("┌")
    assert lines[-1].startswith("└")


def test_basic_double():
    lines = clean(box(text("hi"), style="double").render(20))
    assert lines[0].startswith("╔")
    assert "║" in lines[1]


def test_basic_heavy():
    lines = clean(box(text("hi"), style="heavy").render(20))
    assert lines[0].startswith("┏")
    assert "┃" in lines[1]


def test_title():
    lines = clean(box(text("body"), title="Title").render(20))
    assert "Title" in lines[0]
    assert lines[0].startswith("╭")
    assert lines[0].endswith("╮")


def test_title_truncated():
    lines = clean(box(text("x"), title="A Very Long Title That Overflows").render(15))
    assert "…" in lines[0]
    assert len(lines[0]) == 15


def test_multiline_child():
    child = vstack(text("one"), text("two"), text("three"))
    lines = clean(box(child).render(20))
    assert len(lines) == 5  # top + 3 content + bottom
    assert "one" in lines[1]
    assert "two" in lines[2]
    assert "three" in lines[3]


def test_content_padded_to_width():
    lines = clean(box(text("hi")).render(20))
    # all lines should be same width
    widths = {len(l) for l in lines}
    assert len(widths) == 1


def test_flex_basis():
    assert box(text("hello")).flex_basis() == 7  # 5 + 2 borders
    assert box(text("hello"), padding=1).flex_basis() == 9  # 5 + 2 borders + 2 padding


def test_flex_basis_accounts_for_title():
    """Box should be wide enough to fit the title without truncation."""
    b = box(text("x"), title="Long Title Here")
    # title needs: len("Long Title Here") + 2 (spaces) + 2 (borders) = 19
    assert b.flex_basis() >= len("Long Title Here") + 4


def test_flex_grow_passthrough():
    assert box(text("hi", max_width="fill")).flex_grow_width()
    assert not box(text("hi")).flex_grow_width()


def test_empty_child():
    lines = clean(box(text("")).render(10))
    assert len(lines) == 3  # top + 1 empty content + bottom


def test_narrow_width():
    """Box at minimum width (just borders) shouldn't crash."""
    lines = clean(box(text("hello")).render(2))
    assert len(lines) == 3


# ── Height pass-through ──────────────────────────────────────────────


def test_height_passed_to_child():
    s = ScrollState()
    b = box(scroll(text("a"), text("b"), text("c"), text("d"), state=s))
    lines = clean(b.render(20, 5))
    # Box uses 2 lines for borders, child gets 3
    assert len(lines) == 5
    assert "a" in lines[1]
    assert "b" in lines[2]
    assert "c" in lines[3]


def test_height_none_unconstrained():
    b = box(text("hi"))
    lines = clean(b.render(20))
    assert len(lines) == 3  # top + content + bottom


def test_flex_grow_height_delegates():
    s = ScrollState()
    assert box(scroll(text("a"), state=s)).flex_grow_height()
    assert not box(text("a")).flex_grow_height()


# ── Title position ──────────────────────────────────────────────────


def test_content_clipped_to_inner_width():
    """Child content wider than the box should be truncated, not overflow."""
    b = box(text("a long line of text"))
    lines = clean(b.render(10))
    widths = {len(l) for l in lines}
    assert len(widths) == 1, f"All lines should be same width, got {widths}"


def test_content_clip_preserves_ansi():
    """Clipping styled content should preserve ANSI codes, not strip them."""
    from terminal import bold

    b = box(text(bold("a long line")))
    lines = b.render(10)
    content_line = lines[1]  # first content line (between borders)
    assert "\033[1m" in content_line  # bold preserved


def test_title_starts_after_corner():
    """Title should start right after the corner: ╭ Title ─╮ (no leading dash)."""
    lines = clean(box(text("body"), title="T").render(20))
    top = lines[0]
    assert top[0] == "╭"
    assert top[1] == " "
    assert top[2] == "T"


# ── Validation ──────────────────────────────────────────────────────


def test_invalid_style_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown border style"):
        box(text("x"), style="fancy")
