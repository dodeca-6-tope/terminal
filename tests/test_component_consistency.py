"""Cross-component consistency tests.

Verifies that components sharing the same concept (flex delegation, height
pass-through, private children, empty render) follow identical rules.
"""

from terminal import Renderable, cond, foreach, hstack, scroll, text, vstack, zstack
from terminal.components.scroll import ScrollState
from terminal.measure import display_width, strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


# ── grow delegation ───────────────────────────────────────────────────
# Every wrapper that delegates flex_basis must also delegate grow.


def test_cond_delegates_grow_true():
    assert cond(True, text("x", grow=1)).grow


def test_cond_delegates_grow_false():
    assert cond(False, text("x", grow=1)).grow == 0


def test_foreach_grow_not_propagated():
    fe = foreach(["a"], lambda item, i: text(str(item), grow=1))
    assert not fe.grow

    fe = foreach(["a"], lambda item, i: text(str(item)))
    assert fe.grow == 0

    fe = foreach([], lambda item, i: text(str(item)))
    assert fe.grow == 0

    s = ScrollState()
    fe = foreach(["a"], lambda item, i: scroll(text(item), state=s))
    assert not fe.grow


# ── Height pass-through: only growers receive height ──────────────────
# HStack, ZStack, and ForEach should all follow the same rule: pass height
# to children with grow, not to fixed children.


def _make_scroll(n: int = 20) -> tuple[ScrollState, list[Renderable]]:
    s = ScrollState()
    items: list[Renderable] = [text(str(i)) for i in range(n)]
    return s, items


def test_hstack_passes_height_only_to_growers():
    s, items = _make_scroll()
    h = hstack(scroll(*items, state=s), text("fixed"))
    h.render(40, 5)
    assert s.height == 5


def test_zstack_passes_height_only_to_growers():
    s, items = _make_scroll()
    z = zstack(scroll(*items, state=s), text("overlay"))
    z.render(40, 5)
    assert s.height == 5


def test_zstack_passes_height_to_children():
    """ZStack passes h to all children."""
    s = ScrollState()
    z = zstack(text("base"), scroll(text("a"), state=s))
    z.render(40, 5)
    assert s.height == 5


def test_foreach_passes_height_to_children():
    s = ScrollState()
    fe = foreach(["a"], lambda item, i: scroll(text(item), state=s))
    fe.render(40, 5)
    assert s.height == 5


# ── Weighted flex grow consistency ────────────────────────────────────
# Components wrapping children should propagate the max weight, not just 0/1.


def test_cond_propagates_flex_grow_weight():
    s1 = ScrollState()
    inner = scroll(text("a"), state=s1)
    c = cond(True, inner)
    assert c.grow == inner.grow


def test_foreach_no_propagation():
    s = ScrollState()
    fe = foreach(
        ["a", "b"],
        lambda item, i: scroll(text(item), state=s) if i == 0 else text(item),
    )
    assert not fe.grow


# ── All containers: flex methods match on empty ───────────────────────


def test_empty_flex_basis():
    assert hstack().flex_basis == 0
    assert vstack().flex_basis == 0
    assert zstack().flex_basis == 0
    assert foreach([], lambda item, i: text(str(item))).flex_basis == 0


def test_empty_grow():
    assert hstack().grow == 0
    assert vstack().grow == 0
    assert zstack().grow == 0
    assert foreach([], lambda item, i: text(str(item))).grow == 0


# ── Cond in HStack flex grow ──────────────────────────────────────────
# A fill-text wrapped in cond(True) should still grow in an hstack.


def test_cond_fill_text_grows_in_hstack():
    c = hstack(text("L"), cond(True, text("R", grow=1)))
    result = clean(c.render(20))
    # The fill text should expand to fill remaining space
    assert len(result[0]) == 20


def test_cond_false_fill_text_no_grow_in_hstack():
    c = hstack(text("L"), cond(False, text("R", grow=1)))
    result = clean(c.render(20))
    assert result[0].strip() == "L"


# ── Frame bg respects width constraint ───────────────────────────────


def test_bg_respects_fixed_width():
    """bg should only color the constrained width, not the full parent."""
    r = text("hi", width="10", bg=1)
    lines = r.render(40)
    assert display_width(strip_ansi(lines[0])) == 10


def test_bg_respects_percentage_width():
    r = vstack(text("hi"), width="50%", bg=1)
    lines = r.render(40)
    assert display_width(strip_ansi(lines[0])) == 20


def test_bg_without_width_uses_full_parent():
    r = vstack(text("hi"), bg=1)
    lines = r.render(40)
    assert display_width(strip_ansi(lines[0])) == 40
