"""Tests for VStack component."""

from terminal import scroll, text, vstack
from terminal.components.scroll import ScrollState
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_stacks_children():
    assert clean(vstack(text("a"), text("b")).render(80)) == ["a", "b"]


def test_spacing():
    assert clean(vstack(text("a"), text("b"), spacing=1).render(80)) == ["a", "", "b"]


def test_empty():
    assert clean(vstack().render(80)) == []


def test_flex_basis():
    assert vstack(text("hello"), text("hi")).flex_basis == 5


# ── Height-constrained rendering ─────────────────────────────────────


def test_unconstrained_when_no_height():
    """Without height, render produces as many lines as content needs."""
    v = vstack(text("a"), text("b"), text("c"))
    assert clean(v.render(80)) == ["a", "b", "c"]
    assert clean(v.render(80, None)) == ["a", "b", "c"]


def test_constrained_no_growers_ignores_height():
    """With height but no growers, renders unconstrained."""
    v = vstack(text("a"), text("b"))
    assert clean(v.render(80, 10)) == ["a", "b"]


def test_constrained_distributes_to_grower():
    s = ScrollState()
    v = vstack(text("header"), scroll(text("a"), text("b"), text("c"), state=s))
    # height=4: header=1, scroll gets 3
    result = clean(v.render(80, 4))
    assert result == ["header", "a", "b", "c"]


def test_constrained_multiple_fixed_children():
    s = ScrollState()
    v = vstack(
        text("top"), scroll(text("a"), text("b"), text("c"), state=s), text("bottom")
    )
    # height=5: top=1, bottom=1, scroll gets 3
    result = clean(v.render(80, 5))
    assert result == ["top", "a", "b", "c", "bottom"]


def test_constrained_with_spacing():
    s = ScrollState()
    v = vstack(
        text("top"),
        scroll(text("a"), text("b"), text("c"), text("d"), state=s),
        spacing=1,
    )
    # height=5: top=1, spacing=1, scroll gets 3
    result = clean(v.render(80, 5))
    assert result == ["top", "", "a", "b", "c"]


def test_constrained_two_growers():
    from terminal.components.scroll import ScrollState

    s1 = ScrollState()
    s2 = ScrollState()
    v = vstack(
        scroll(*[text(str(i)) for i in range(10)], state=s1),
        scroll(*[text(str(i + 10)) for i in range(10)], state=s2),
    )
    # height=6: each grower gets 3
    result = clean(v.render(80, 6))
    assert result == ["0", "1", "2", "10", "11", "12"]


def test_constrained_grower_gets_zero_when_fixed_fills():
    s = ScrollState()
    v = vstack(
        text("a"),
        text("b"),
        text("c"),
        scroll(text("x"), text("y"), state=s),
    )
    # height=3: fixed children take 3, scroll gets 0
    result = clean(v.render(80, 3))
    assert result == ["a", "b", "c"]


# ── flex_grow propagation ───────────────────────────────────────────


def test_flex_grow_propagates_from_children():
    assert vstack(text("a"), text("b", width="100%")).flex_grow_width


def test_flex_grow_false_without_growers():
    assert not vstack(text("a"), text("b")).flex_grow_width
