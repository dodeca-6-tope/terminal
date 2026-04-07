"""Cross-component consistency tests.

Verifies that components sharing the same concept (flex delegation, height
pass-through, private children, empty render) follow identical rules.
"""

from terminal import Renderable, cond, foreach, hstack, scroll, text, vstack, zstack
from terminal.components.scroll import ScrollState
from terminal.measure import display_width, strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


# ── flex_grow_width delegation ────────────────────────────────────────
# Every wrapper that delegates flex_basis must also delegate flex_grow_width.


def test_cond_delegates_flex_grow_width_true():
    assert cond(True, text("x", width="100%")).flex_grow_width


def test_cond_delegates_flex_grow_width_false():
    assert cond(False, text("x", width="100%")).flex_grow_width == 0


def test_foreach_delegates_flex_grow_width():
    fe = foreach(["a"], lambda item, i: text(str(item), width="100%"))
    assert fe.flex_grow_width


def test_foreach_flex_grow_width_no_growers():
    fe = foreach(["a"], lambda item, i: text(str(item)))
    assert fe.flex_grow_width == 0


def test_foreach_flex_grow_width_empty():
    fe = foreach([], lambda item, i: text(str(item)))
    assert fe.flex_grow_width == 0


# ── flex_grow_height delegation ───────────────────────────────────────


def test_foreach_delegates_flex_grow_height():
    s = ScrollState()
    fe = foreach(["a"], lambda item, i: scroll(text(item), state=s))
    assert fe.flex_grow_height == 1


def test_foreach_flex_grow_height_no_growers():
    fe = foreach(["a"], lambda item, i: text(str(item)))
    assert fe.flex_grow_height == 0


def test_foreach_flex_grow_height_empty():
    fe = foreach([], lambda item, i: text(str(item)))
    assert fe.flex_grow_height == 0


# ── Height pass-through: only growers receive height ──────────────────
# HStack, ZStack, and ForEach should all follow the same rule: pass height
# to children with flex_grow_height, not to fixed children.


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
    # scroll has flex_grow_height=1, but we can test that it propagates exactly
    inner = scroll(text("a"), state=s1)
    c = cond(True, inner)
    assert c.flex_grow_width == inner.flex_grow_width
    assert c.flex_grow_height == inner.flex_grow_height


def test_foreach_propagates_max_flex_grow():
    s = ScrollState()
    fe = foreach(
        ["a", "b"],
        lambda item, i: scroll(text(item), state=s) if i == 0 else text(item),
    )
    assert fe.flex_grow_width == 1  # scroll has grow_width=1
    assert fe.flex_grow_height == 1  # scroll has grow_height=1


# ── All containers: flex methods match on empty ───────────────────────


def test_empty_flex_basis():
    assert hstack().flex_basis == 0
    assert vstack().flex_basis == 0
    assert zstack().flex_basis == 0
    assert foreach([], lambda item, i: text(str(item))).flex_basis == 0


def test_empty_flex_grow_width():
    assert hstack().flex_grow_width == 0
    assert vstack().flex_grow_width == 0
    assert zstack().flex_grow_width == 0
    assert foreach([], lambda item, i: text(str(item))).flex_grow_width == 0


def test_empty_flex_grow_height():
    assert hstack().flex_grow_height == 0
    assert vstack().flex_grow_height == 0
    assert zstack().flex_grow_height == 0
    assert foreach([], lambda item, i: text(str(item))).flex_grow_height == 0


# ── Cond in HStack flex grow ──────────────────────────────────────────
# A fill-text wrapped in cond(True) should still grow in an hstack.


def test_cond_fill_text_grows_in_hstack():
    c = hstack(text("L"), cond(True, text("R", width="100%")))
    result = clean(c.render(20))
    # The fill text should expand to fill remaining space
    assert len(result[0]) == 20


def test_cond_false_fill_text_no_grow_in_hstack():
    c = hstack(text("L"), cond(False, text("R", width="100%")))
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
