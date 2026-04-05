"""Tests for HStack component."""

from terminal import Text, cond, hstack, spacer, text, vstack
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


# ── Fixed layout ─────────────────────────────────────────────────────


def test_side_by_side():
    assert clean(hstack(text("a"), text("b"), spacing=1).render(20)) == ["a b"]


def test_spacing():
    assert clean(hstack(text("a"), text("b"), spacing=3).render(20)) == ["a   b"]


def test_spacer_fills():
    result = clean(hstack(text("L"), spacer(), text("R")).render(20))[0]
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
    result = clean(hstack(text("L"), text("R"), justify="between").render(20))[0]
    assert result.startswith("L")
    assert result.rstrip().endswith("R")


def test_justify_end():
    result = clean(hstack(text("hi"), justify="end").render(20))[0]
    assert result.endswith("hi")
    assert result.startswith(" ")


def test_justify_center():
    result = clean(hstack(text("hi"), justify="center").render(20))[0]
    assert "hi" in result
    assert result.index("h") > 0


def test_justify_between_single_child():
    """justify=between with one child should behave like start."""
    result = clean(hstack(text("only"), justify="between").render(20))[0]
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
        hstack(Text("hello"), Text("world"), wrap=True, spacing=1).render(40)
    ) == ["hello world"]


def test_wrap_ansi_text():
    green, rst = "\033[32m", "\033[0m"
    chunks = [text(f"{green}[⏎]{rst} select"), text("[esc] back")]
    result = clean(hstack(*chunks, wrap=True, spacing=1).render(25))
    assert len(result) == 1
    assert len(clean(hstack(*chunks, wrap=True, spacing=1).render(15))) == 2


# ── flex_grow propagation ───────────────────────────────────────────


def test_flex_grow_from_child():
    assert hstack(text("a"), text("b", max_width="fill")).flex_grow() is True


def test_flex_grow_false_without_growers():
    assert hstack(text("a"), text("b")).flex_grow() is False


def test_justify_implies_flex_grow():
    """Non-start justify modes need extra space, so they imply flex_grow."""
    assert hstack(text("a"), justify="center").flex_grow() is True
    assert hstack(text("a"), justify="end").flex_grow() is True
    assert hstack(text("a"), justify="between").flex_grow() is True
    assert hstack(text("a"), justify="start").flex_grow() is False


def test_justify_gets_space_in_hstack():
    """A justify=between hstack inside an outer hstack should spread items."""
    inner = hstack(text("L"), text("R"), justify="between")
    outer = hstack(inner)
    result = clean(outer.render(20))[0]
    assert result.startswith("L")
    assert result.rstrip().endswith("R")
    assert len(result) == 20


# ── Validation ──────────────────────────────────────────────────────


def test_invalid_justify_raises():
    import pytest

    with pytest.raises(ValueError, match="unknown justify"):
        hstack(text("x"), justify="spread")
