"""Tests for HStack component."""

from terminal import cond, hstack, scroll, text, vstack
from terminal.components.scroll import ScrollState
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


# ── Fixed layout ─────────────────────────────────────────────────────


def test_side_by_side():
    assert clean(hstack(text("a"), text("b"), spacing=1).render(20)) == ["a b"]


def test_spacing():
    assert clean(hstack(text("a"), text("b"), spacing=3).render(20)) == ["a   b"]


def test_between_fills():
    result = clean(hstack(text("L"), text("R"), justify_content="between").render(20))[
        0
    ]
    assert result.startswith("L")
    assert result.endswith("R")
    assert len(result) == 20


def test_cond_false_invisible():
    result = clean(hstack(cond(False, text("gone")), text("here")).render(80))[0]
    assert "gone" not in result
    assert result.strip() == "here"


def test_empty():
    assert clean(hstack().render(80)) == [""]


def test_multiline_children():
    lines = clean(hstack(vstack(text("a"), text("b")), text("c"), spacing=1).render(20))
    assert len(lines) == 2
    assert "a" in lines[0] and "c" in lines[0]
    assert "b" in lines[1]


# ── Justify ──────────────────────────────────────────────────────────


def test_justify_between():
    result = clean(hstack(text("L"), text("R"), justify_content="between").render(20))[
        0
    ]
    assert result.startswith("L")
    assert result.rstrip().endswith("R")


def test_justify_end():
    result = clean(hstack(text("hi"), justify_content="end").render(20))[0]
    assert result.endswith("hi")
    assert result.startswith(" ")


def test_justify_center():
    result = clean(hstack(text("hi"), justify_content="center").render(20))[0]
    assert "hi" in result
    assert result.index("h") > 0


def test_justify_between_single_child():
    """justify_content=between with one child should behave like start."""
    result = clean(hstack(text("only"), justify_content="between").render(20))[0]
    assert result.startswith("only")


# ── Wrap ─────────────────────────────────────────────────────────────


def test_wrap_basic():
    assert clean(hstack(text("hello"), wrap=True, spacing=1).render(80)) == ["hello"]
    assert clean(
        hstack(text("[⏎] select"), text("[esc] back"), wrap=True, spacing=1).render(40)
    ) == ["[⏎] select [esc] back"]
    assert clean(
        hstack(text("[⏎] select"), text("[esc] back"), wrap=True, spacing=1).render(15)
    ) == ["[⏎] select", "[esc] back"]
    assert clean(hstack(wrap=True, spacing=1).render(80)) == [""]
    assert clean(hstack(text("very long chunk"), wrap=True, spacing=1).render(5)) == [
        "very long chunk"
    ]


def test_wrap_many_chunks():
    chunks = [text("[a] one"), text("[b] two"), text("[c] three"), text("[d] four")]
    assert clean(hstack(*chunks, wrap=True, spacing=1).render(24)) == [
        "[a] one [b] two",
        "[c] three [d] four",
    ]


def test_wrap_boundary():
    assert clean(hstack(text("aaa"), text("bbb"), wrap=True, spacing=1).render(7)) == [
        "aaa bbb"
    ]
    assert clean(hstack(text("aaa"), text("bbb"), wrap=True, spacing=1).render(6)) == [
        "aaa",
        "bbb",
    ]


def test_wrap_with_spacing():
    assert clean(
        hstack(text("a"), text("b"), text("c"), wrap=True, spacing=2).render(20)
    ) == ["a  b  c"]
    assert clean(hstack(text("aaa"), text("bbb"), wrap=True, spacing=3).render(8)) == [
        "aaa",
        "bbb",
    ]
    assert clean(hstack(text("aaa"), text("bbb"), wrap=True, spacing=3).render(9)) == [
        "aaa   bbb"
    ]


def test_wrap_with_text_objects():
    assert clean(
        hstack(text("hello"), text("world"), wrap=True, spacing=1).render(40)
    ) == ["hello world"]


def test_wrap_ansi_text():
    green, rst = "\033[32m", "\033[0m"
    chunks = [text(f"{green}[⏎]{rst} select"), text("[esc] back")]
    result = clean(hstack(*chunks, wrap=True, spacing=1).render(25))
    assert len(result) == 1
    assert len(clean(hstack(*chunks, wrap=True, spacing=1).render(15))) == 2


# ── flex_grow propagation ───────────────────────────────────────────


def test_flex_grow_from_child():
    assert hstack(text("a"), text("b", width="100%")).flex_grow_width


def test_flex_grow_false_without_growers():
    assert not hstack(text("a"), text("b")).flex_grow_width


def test_justify_implies_flex_grow():
    """Non-start justify modes need extra space, so they imply flex_grow."""
    assert hstack(text("a"), justify_content="center").flex_grow_width
    assert hstack(text("a"), justify_content="end").flex_grow_width
    assert hstack(text("a"), justify_content="between").flex_grow_width
    assert not hstack(text("a"), justify_content="start").flex_grow_width


def test_justify_gets_space_in_hstack():
    """A justify_content=between hstack inside an outer hstack should spread items."""
    inner = hstack(text("L"), text("R"), justify_content="between")
    outer = hstack(inner)
    result = clean(outer.render(20))[0]
    assert result.startswith("L")
    assert result.rstrip().endswith("R")
    assert len(result) == 20


# ── Validation ──────────────────────────────────────────────────────


def test_invalid_justify_content_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown justify_content"):
        hstack(text("x"), justify_content="spread")


# ── Height propagation ─────────────────────────────────────────────


def test_height_passed_to_scroll_child():
    """HStack should forward height to children with flex_grow_height."""
    s = ScrollState()
    view = vstack(
        hstack(
            scroll(*[text(str(i)) for i in range(20)], state=s),
            text("R"),
        ),
    )
    lines = view.render(20, 10)
    assert len(lines) == 10
    # Scroll should have received the height and rendered its content
    assert s.height == 10


def test_height_not_passed_to_fixed_child():
    """Children without flex_grow_height should not receive height."""
    s = ScrollState()
    view = vstack(
        hstack(
            scroll(*[text(str(i)) for i in range(20)], state=s),
            text("side"),
        ),
    )
    lines = view.render(40, 8)
    # Scroll fills 8 rows, text("side") is 1 row — HStack pads shorter columns
    assert len(lines) == 8
    assert s.height == 8


def test_flex_grow_height_true_with_scroll():
    """HStack with a scroll child should claim flex_grow_height."""
    s = ScrollState()
    h = hstack(scroll(text("a"), state=s), text("b"))
    assert h.flex_grow_height


def test_hstack_in_vstack_scroll_gets_remaining_height():
    """Scroll inside HStack inside VStack should get the remaining height."""
    s = ScrollState()
    view = vstack(
        text("header"),
        hstack(
            scroll(*[text(str(i)) for i in range(50)], state=s),
        ),
        text("footer"),
    )
    lines = view.render(20, 12)
    assert len(lines) == 12
    # header=1, footer=1, scroll gets 10
    assert s.height == 10
    assert clean(lines)[0] == "header"
    assert clean(lines)[11] == "footer"
