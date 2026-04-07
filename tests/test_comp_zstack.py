"""Tests for ZStack component."""

from terminal import box, text, vstack, zstack
from terminal.components.base import Renderable
from terminal.components.scroll import ScrollState
from terminal.measure import display_width, strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def _block(char: str, w: int, h: int) -> Renderable:
    def render(width: int, height: int | None = None) -> list[str]:
        return [char * w] * h

    return Renderable(render, flex_basis=w)


def _grower(char: str = "X") -> Renderable:
    def render(width: int, height: int | None = None) -> list[str]:
        return [char * width] * (height or 1)

    return Renderable(render, flex_grow_width=1, flex_grow_height=1)


# ── Canvas sizing ─────────────────────────────────────────────────


def test_canvas_height_from_first_child():
    """Canvas height comes from first child when h is not passed."""
    base = vstack(text("a"), text("b"), text("c"))  # 3 lines
    overlay = vstack(*[text(str(i)) for i in range(10)])  # 10 lines
    lines = zstack(base, overlay).render(20)
    assert len(lines) == 3


def test_canvas_height_uses_h():
    """When h is passed, canvas uses it."""
    z = zstack(_grower(), text("overlay"))
    lines = z.render(20, 10)
    assert len(lines) == 10


def test_canvas_height_uses_h_even_without_grower():
    """Canvas respects h even when no child grows."""
    base = _block(".", 10, 3)
    lines = zstack(base).render(10, 7)
    assert len(lines) == 7


def test_canvas_width_uses_w():
    """Canvas always uses the available width."""
    z = zstack(_block(".", 5, 2))
    lines = clean(z.render(20))
    assert all(display_width(l) == 20 for l in lines)


def test_default_alignment_is_top_left():
    """With default alignment, child renders at top-left."""
    lines = clean(zstack(_block("X", 3, 2)).render(10, 5))
    assert lines[0].startswith("XXX")
    assert lines[1].startswith("XXX")
    assert "X" not in lines[2]


def test_alignment_uses_declared_width():
    """A child with explicit width is positioned by declared width, not content."""
    # Text overflows width=8, but alignment uses 8
    child = vstack(text("very long content"), width="8", height="1")
    lines = clean(zstack(child, justify_content="center").render(30, 1))
    # Centered: (30-8)//2 = 11
    pos = lines[0].index("v")
    assert pos == 11


def test_alignment_uses_rendered_width_without_declared():
    """Without explicit width, alignment uses rendered content width."""
    child = text("hello")  # 5 chars, no width constraint
    lines = clean(zstack(child, justify_content="center").render(30, 1))
    # Centered: (30-5)//2 = 12
    pos = lines[0].index("h")
    assert pos == 12


def test_all_children_render_within_canvas():
    """All children are placed within the canvas dimensions."""
    base = _block(".", 10, 3)
    overlay = _block("X", 5, 1)
    lines = zstack(base, overlay).render(10, 5)
    assert len(lines) == 5
    assert all(display_width(l) <= 10 for l in clean(lines))


# ── Alignment ────────────────────────────────────────────────────


def test_all_9_alignments_distinct():
    """Every alignment produces a unique overlay position."""
    canvas_w, canvas_h = 20, 7
    overlay = _block("X", 3, 3)
    positions: set[tuple[int, int]] = set()
    combos = [
        ("start", "start"),
        ("center", "start"),
        ("end", "start"),
        ("start", "center"),
        ("center", "center"),
        ("end", "center"),
        ("start", "end"),
        ("center", "end"),
        ("end", "end"),
    ]
    for jc, ai in combos:
        lines = clean(
            zstack(overlay, justify_content=jc, align_items=ai).render(
                canvas_w, canvas_h
            )
        )
        row = next(r for r, l in enumerate(lines) if "X" in l)
        col = lines[row].index("X")
        positions.add((row, col))
    assert len(positions) == 9


def test_single_axis_centers_other():
    """'top' centers horizontally, 'left' centers vertically."""
    overlay = _block("X", 4, 2)

    # top: justify_content="center", align_items="start"
    top_lines = clean(
        zstack(overlay, justify_content="center", align_items="start").render(20, 10)
    )
    top_row = next(r for r, l in enumerate(top_lines) if "X" in l)
    top_col = top_lines[top_row].index("X")
    assert top_row == 0
    assert top_col == 8  # centered: (20-4)//2

    # top-left: defaults (start, start)
    tl_lines = clean(zstack(overlay).render(20, 10))
    tl_col = tl_lines[0].index("X")
    assert tl_col == 0

    # left: justify_content="start", align_items="center"
    left_lines = clean(zstack(overlay, align_items="center").render(20, 10))
    left_row = next(r for r, l in enumerate(left_lines) if "X" in l)
    left_col = left_lines[left_row].index("X")
    assert left_row == 4  # centered: (10-2)//2
    assert left_col == 0


# ── Overlay alignment ────────────────────────────────────────────


def test_overlay_aligns_within_canvas():
    """Overlay centers within the canvas (w, h), not the first child."""
    overlay = _block("X", 4, 1)
    lines = clean(
        zstack(overlay, justify_content="center", align_items="center").render(20, 7)
    )
    mid = lines[3]
    x_pos = mid.index("XXXX")
    assert x_pos == 8  # (20-4)//2


def test_center_alignment():
    base = vstack(text("." * 20), text("." * 20), text("." * 20))
    overlay = text("HI")
    lines = clean(
        zstack(base, overlay, justify_content="center", align_items="center").render(20)
    )
    mid = lines[1]
    hi_pos = mid.index("H")
    assert hi_pos == 9  # (20 - 2) // 2


def test_bottom_right_alignment():
    base = _block(".", 10, 3)
    overlay = text("X")
    lines = clean(
        zstack(base, overlay, justify_content="end", align_items="end").render(10)
    )
    assert lines[2].rstrip().endswith("X")


def test_top_left_default():
    lines = clean(zstack(text("." * 10), text("AB")).render(10))
    assert lines[0].startswith("AB")


# ── Overlay clipping ─────────────────────────────────────────────


def test_overlay_clips_vertically():
    """Overlay taller than canvas is clipped to canvas height."""
    overlay = _block("X", 10, 10)
    lines = zstack(overlay).render(10, 3)
    assert len(lines) == 3


def test_overlay_clips_when_offset():
    """Overlay at bottom that would exceed canvas is clipped."""
    base = _block(".", 10, 5)
    overlay = _block("X", 3, 4)
    lines = clean(
        zstack(base, overlay, justify_content="center", align_items="end").render(10)
    )
    assert len(lines) == 5
    # Overlay should appear on the bottom rows, partially clipped
    assert "X" in lines[4]


def test_overlay_clips_width():
    """Overlay wider than canvas is clipped to canvas width."""
    overlay = _block("X", 15, 1)
    lines = clean(zstack(overlay).render(7, 3))
    assert all(display_width(l) == 7 for l in lines)
    assert lines[0] == "X" * 7


def test_overlay_clips_width_when_offset():
    """Overlay at right edge that would exceed canvas is clipped."""
    base = _block(".", 10, 3)
    overlay = _block("X", 6, 1)
    lines = clean(zstack(base, overlay, justify_content="end").render(10))
    # Overlay at col 4, width 6 — should clip to 6 (fits: 4+6=10)
    assert display_width(lines[0]) == 10
    assert lines[0].count("X") == 6


def test_overlay_larger_than_base_clips_both_axes():
    """Overlay larger than canvas in both dimensions clips to canvas bounds."""
    overlay = _block("X", 12, 10)
    lines = clean(
        zstack(overlay, justify_content="center", align_items="center").render(7, 5)
    )
    assert len(lines) == 5
    assert all(display_width(l) == 7 for l in lines)


# ── Height pass-through ──────────────────────────────────────────


def test_height_passed_to_growers():
    from terminal import scroll

    s = ScrollState()
    items = [text(str(i)) for i in range(20)]
    base = scroll(*items, state=s)
    overlay = text("HI")
    lines = zstack(base, overlay).render(10, 5)
    assert len(lines) == 5
    assert s.height == 5


# ── Nested ZStacks ───────────────────────────────────────────────


def test_nested_zstack_preserves_inner_width():
    """Inner ZStack uses canvas width (w), not first child width."""
    inner_overlay = _block("X", 4, 1)
    inner = zstack(inner_overlay, justify_content="center", align_items="center")

    # Inner gets w=40, so canvas is 40 wide
    inner_lines = inner.render(40, 3)
    for line in inner_lines:
        assert display_width(line) == 40


def test_nested_zstack_positions_correctly():
    """Inner ZStack can be positioned within an outer ZStack."""
    inner = zstack(
        _block("B", 10, 3),
        _block("X", 2, 1),
        justify_content="center",
        align_items="center",
    )
    lines = clean(
        zstack(inner, justify_content="center", align_items="center").render(30, 9)
    )

    # Inner renders at w=30, canvas=30. B block (10 wide) centered -> col 10
    # Inner (3 tall from tallest child) centered in outer 9 -> row 3
    assert "B" in lines[3]
    b_pos = lines[3].index("B")
    assert b_pos == 10


def test_block_positioned_at_all_9_spots():
    """A small block placed at each alignment lands at the expected offset."""
    outer_w, outer_h = 30, 9
    block_w, block_h = 6, 3
    block = _block("B", block_w, block_h)

    expected = {
        ("start", "start"): (0, 0),
        ("center", "start"): (0, 12),
        ("end", "start"): (0, 24),
        ("start", "center"): (3, 0),
        ("center", "center"): (3, 12),
        ("end", "center"): (3, 24),
        ("start", "end"): (6, 0),
        ("center", "end"): (6, 12),
        ("end", "end"): (6, 24),
    }
    for (jc, ai), (exp_row, exp_col) in expected.items():
        lines = clean(
            zstack(block, justify_content=jc, align_items=ai).render(outer_w, outer_h)
        )
        b_pos = lines[exp_row].index("B")
        assert b_pos == exp_col, f"jc={jc},ai={ai}: expected col {exp_col}, got {b_pos}"
        assert "B" not in lines[exp_row - 1] if exp_row > 0 else True


def test_nested_zstack_at_all_9_spots():
    """Nested ZStack (block + overlay) positioned at all 9 spots."""
    outer_w, outer_h = 30, 9
    inner_base = _block("B", 6, 3)
    inner_overlay = _block("X", 2, 1)

    combos = [
        ("start", "start"),
        ("center", "start"),
        ("end", "start"),
        ("start", "center"),
        ("center", "center"),
        ("end", "center"),
        ("start", "end"),
        ("center", "end"),
        ("end", "end"),
    ]

    for jc, ai in combos:
        combo = zstack(
            inner_base,
            inner_overlay,
            justify_content="center",
            align_items="center",
        )
        lines = clean(
            zstack(combo, justify_content=jc, align_items=ai).render(outer_w, outer_h)
        )
        assert len(lines) == outer_h
        has_b = any("B" in l for l in lines)
        has_x = any("X" in l for l in lines)
        assert has_b, f"jc={jc},ai={ai}: inner base not visible"
        assert has_x, f"jc={jc},ai={ai}: inner overlay not visible"


# ── Flex properties ──────────────────────────────────────────────


def test_flex_basis_is_max():
    assert zstack(text("short"), text("longer text")).flex_basis == 11


def test_flex_grow_width_if_any_child_grows():
    assert zstack(text("hi"), text("fill", width="100%")).flex_grow_width
    assert not zstack(text("hi"), text("no")).flex_grow_width


def test_flex_grow_height_propagates():
    from terminal import scroll

    s = ScrollState()
    z = zstack(scroll(text("a"), state=s))
    assert z.flex_grow_height
    assert not zstack(text("a")).flex_grow_height


# ── Edge cases ───────────────────────────────────────────────────


def test_empty():
    assert clean(zstack().render(10)) == [""]


def test_single_child():
    lines = clean(zstack(text("hello")).render(20))
    assert "hello" in lines[0]


def test_top_layer_overwrites():
    lines = clean(zstack(text("aaaa"), text("bb")).render(10))
    assert lines[0].startswith("bb")


def test_empty_overlay_preserves_base():
    from terminal import cond

    base = text("visible")
    overlay = cond(False, text("hidden"))
    lines = clean(zstack(base, overlay).render(20))
    assert "visible" in lines[0]


def test_box_overlay_centered():
    base = vstack(*[text("." * 30) for _ in range(5)])
    overlay = box(text("Alert!"), style="normal", padding=1)
    lines = clean(
        zstack(base, overlay, justify_content="center", align_items="center").render(30)
    )
    assert any("Alert!" in l for l in lines)
    assert lines[0].startswith(".")
    assert lines[4].startswith(".")


# ── ANSI / styling preservation ──────────────────────────────────


def test_overlay_preserves_base_styling():
    from terminal import bold

    base = text(bold("hello world"))
    overlay = text("XX")
    lines = zstack(base, overlay).render(20)
    raw = lines[0]
    after_overlay = raw.split("XX", 1)[1]
    assert "\033[1m" in after_overlay


def test_overlay_preserves_base_color():
    from terminal import color

    base = text(color(1, "aaabbbccc"))
    overlay = text("XX")
    lines = zstack(base, overlay).render(20)
    raw = lines[0]
    after_overlay = raw.split("XX", 1)[1]
    assert "\033[38;5;1m" in after_overlay


# ── Wide character handling ──────────────────────────────────────


def test_split_at_col_wide_chars():
    z = zstack(text("你好世界xxxx"), text("AB"))
    lines = clean(z.render(20))
    assert lines[0].startswith("AB")
    assert "好" in lines[0]


def test_overlay_on_wide_char_base():
    base = text("你好世界")
    overlay = text("AB")
    lines = clean(
        zstack(base, overlay, justify_content="center", align_items="center").render(8)
    )
    assert "AB" in lines[0]


# ── Validation ───────────────────────────────────────────────────


def test_invalid_justify_content_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown justify_content"):
        zstack(text("x"), justify_content="middle")


def test_invalid_align_items_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown align_items"):
        zstack(text("x"), align_items="middle")
