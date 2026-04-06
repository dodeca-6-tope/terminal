"""Tests for ZStack component."""

from terminal import box, text, vstack, zstack
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_single_child():
    lines = clean(zstack(text("hello")).render(20))
    assert "hello" in lines[0]


def test_top_layer_overwrites():
    lines = clean(zstack(text("aaaa"), text("bb")).render(10))
    assert lines[0].startswith("bb")


def test_center_alignment():
    base = vstack(text("." * 20), text("." * 20), text("." * 20))
    overlay = text("HI")
    lines = clean(zstack(base, overlay, align="center").render(20))
    # "HI" should be centered horizontally in the middle row
    mid = lines[1]
    hi_pos = mid.index("H")
    assert hi_pos == 9  # (20 - 2) // 2


def test_bottom_right_alignment():
    base = vstack(text(" " * 10), text(" " * 10), text(" " * 10))
    overlay = text("X")
    lines = clean(zstack(base, overlay, align="bottom-right").render(10))
    assert lines[2].rstrip().endswith("X")


def test_top_left_default():
    lines = clean(zstack(text("." * 10), text("AB")).render(10))
    assert lines[0].startswith("AB")


def test_empty():
    assert clean(zstack().render(10)) == [""]


def test_empty_overlay_preserves_base():
    from terminal import cond

    base = text("visible")
    overlay = cond(False, text("hidden"))
    lines = clean(zstack(base, overlay).render(20))
    assert "visible" in lines[0]


def test_box_overlay_centered():
    base = vstack(*[text("." * 30) for _ in range(5)])
    overlay = box(text("Alert!"), style="normal", padding=1)
    lines = clean(zstack(base, overlay, align="center").render(30))
    # Box should be centered, base dots visible around it
    assert any("Alert!" in l for l in lines)
    # Top and bottom rows should still have dots
    assert lines[0].startswith(".")
    assert lines[4].startswith(".")


def test_flex_basis_is_max():
    assert zstack(text("short"), text("longer text")).flex_basis() == 11


def test_flex_grow_if_any_child_grows():
    assert zstack(text("hi"), text("fill", max_width="fill")).flex_grow_width()
    assert not zstack(text("hi"), text("no")).flex_grow_width()


# ── Height pass-through ─────────────────────────────────────────────


def test_height_passed_to_children():
    """ZStack should pass height to children so fill-height components work."""
    from terminal import scroll
    from terminal.components.scroll import ScrollState

    s = ScrollState()
    items = [text(str(i)) for i in range(20)]
    base = scroll(*items, state=s)
    overlay = text("HI")
    lines = zstack(base, overlay).render(10, 5)
    # scroll should be constrained to 5 lines, not all 20
    assert len(lines) == 5


def test_flex_grow_height_propagates():
    from terminal import scroll
    from terminal.components.scroll import ScrollState

    s = ScrollState()
    z = zstack(scroll(text("a"), state=s))
    assert z.flex_grow_height()
    assert not zstack(text("a")).flex_grow_height()


# ── Overlay styling preservation ────────────────────────────────────


def test_overlay_preserves_base_styling():
    """Overlay should not strip ANSI styling from base text to its right."""
    from terminal import bold

    base = text(bold("hello world"))
    overlay = text("XX")
    lines = zstack(base, overlay).render(20)
    raw = lines[0]
    # After the overlay, the bold styling should be restored
    # Find content after "XX" — it should contain bold ANSI code
    after_overlay = raw.split("XX", 1)[1]
    assert "\033[1m" in after_overlay


def test_overlay_preserves_base_color():
    """Overlay should restore color on the base line after the overlay."""
    from terminal import color

    base = text(color(1, "aaabbbccc"))
    overlay = text("XX")
    lines = zstack(base, overlay, align="top-left").render(20)
    raw = lines[0]
    after_overlay = raw.split("XX", 1)[1]
    assert "\033[38;5;1m" in after_overlay


# ── Wide character handling ────────────────────────────────────────


def test_split_at_col_wide_chars():
    """_split_at_col must account for wide characters occupying 2 columns."""
    z = zstack(text("你好世界xxxx"), text("AB"), align="top-left")
    lines = clean(z.render(20))
    # AB overwrites columns 0-1, the rest of the wide chars should remain
    assert lines[0].startswith("AB")
    assert "好" in lines[0]


def test_overlay_on_wide_char_base():
    """Overlaying at a column offset over wide chars should align correctly."""
    # Base is 4 wide chars = 8 columns, overlay 2 ASCII chars centered
    base = text("你好世界")
    overlay = text("AB")
    lines = clean(zstack(base, overlay, align="center").render(8))
    assert "AB" in lines[0]


# ── Validation ─────────────────────────────────────────────────────


def test_invalid_align_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown align"):
        zstack(text("x"), align="middle")
