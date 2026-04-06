"""Tests for Scroll component."""

from terminal import box, hstack, scroll, scrollbar, scrollbar_default, text, vstack
from terminal.components.scroll import ScrollState
from terminal.measure import display_width, strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def _state(offset: int = 0) -> ScrollState:
    s = ScrollState()
    s.offset = offset
    return s


# ── Basic rendering ──────────────────────────────────────────────────


def test_shows_slice_at_offset():
    s = _state(1)
    assert clean(
        scroll(
            text("a"), text("b"), text("c"), text("d"), text("e"), state=s, height=3
        ).render(80)
    ) == ["b", "c", "d"]


def test_offset_zero():
    s = _state()
    assert clean(
        scroll(text("a"), text("b"), text("c"), text("d"), state=s, height=2).render(80)
    ) == ["a", "b"]


def test_single_child():
    s = _state()
    assert clean(scroll(text("only"), state=s, height=1).render(80)) == ["only"]


def test_pads_when_content_shorter_than_height():
    s = _state()
    assert clean(scroll(text("a"), state=s, height=3).render(80)) == ["a", "", ""]


def test_exact_fit():
    s = _state()
    assert clean(
        scroll(text("a"), text("b"), text("c"), state=s, height=3).render(80)
    ) == ["a", "b", "c"]


def test_empty_no_children():
    s = _state()
    assert clean(scroll(state=s, height=3).render(80)) == ["", "", ""]


def test_height_one():
    s = _state(2)
    assert clean(
        scroll(text("a"), text("b"), text("c"), state=s, height=1).render(80)
    ) == ["c"]


# ── Offset clamping ─────────────────────────────────────────────────


def test_clamps_offset_over_max():
    s = _state(10)
    result = clean(
        scroll(text("a"), text("b"), text("c"), state=s, height=2).render(80)
    )
    assert result == ["b", "c"]
    assert s.offset == 1


def test_offset_negative_clamps_to_zero():
    s = _state(-5)
    assert clean(
        scroll(text("a"), text("b"), text("c"), state=s, height=2).render(80)
    ) == ["a", "b"]
    assert s.offset == 0


def test_offset_exactly_at_max():
    s = _state(2)
    result = clean(
        scroll(text("a"), text("b"), text("c"), text("d"), state=s, height=2).render(80)
    )
    assert result == ["c", "d"]
    assert s.offset == 2


def test_offset_clamps_when_content_fits():
    s = _state(5)
    result = clean(scroll(text("a"), text("b"), state=s, height=5).render(80))
    assert result == ["a", "b", "", "", ""]
    assert s.offset == 0  # max_offset is 0 since content fits


# ── Multiline children ──────────────────────────────────────────────


def test_multiline_child():
    s = _state()
    child = vstack(text("x"), text("y"))
    assert clean(scroll(child, text("z"), state=s, height=2).render(80)) == ["x", "y"]


def test_multiline_child_partial_clip():
    s = _state()
    child = vstack(text("x"), text("y"), text("z"))
    assert clean(scroll(child, text("after"), state=s, height=2).render(80)) == [
        "x",
        "y",
    ]


def test_multiline_child_at_offset():
    s = _state(1)
    child1 = vstack(text("a"), text("b"))
    child2 = vstack(text("c"), text("d"))
    child3 = vstack(text("e"), text("f"))
    # offset=1 skips child1, shows child2 (2 lines fills height)
    assert clean(scroll(child1, child2, child3, state=s, height=2).render(80)) == [
        "c",
        "d",
    ]


def test_mixed_single_and_multiline():
    s = _state()
    child = vstack(text("x"), text("y"))
    assert clean(
        scroll(text("header"), child, text("footer"), state=s, height=4).render(80)
    ) == ["header", "x", "y", "footer"]


# ── Flex delegation ─────────────────────────────────────────────────


def test_flex_basis_uses_max():
    s = _state()
    sc = scroll(text("hi"), text("hello"), state=s, height=5)
    assert sc.flex_basis() == 5


def test_flex_basis_empty():
    s = _state()
    sc = scroll(state=s, height=5)
    assert sc.flex_basis() == 0


def test_flex_grow_when_child_grows():
    s = _state()
    sc = scroll(text("x", max_width="fill"), state=s, height=5)
    assert sc.flex_grow_width()


def test_flex_grow_height_fill():
    s = _state()
    sc = scroll(text("a"), state=s)
    assert sc.flex_grow_height()


def test_no_flex_grow_height_fixed():
    s = _state()
    sc = scroll(text("a"), state=s, height=10)
    assert not sc.flex_grow_height()


# ── height="fill" ───────────────────────────────────────────────────


def test_fill_uses_parent_height():
    s = _state()
    sc = scroll(text("a"), text("b"), text("c"), text("d"), text("e"), state=s)
    assert clean(sc.render(80, 3)) == ["a", "b", "c"]


def test_fill_with_offset():
    s = _state(2)
    sc = scroll(text("a"), text("b"), text("c"), text("d"), state=s)
    assert clean(sc.render(80, 2)) == ["c", "d"]


def test_fill_in_vstack():
    s = _state()
    v = vstack(
        text("header"), scroll(text("a"), text("b"), text("c"), text("d"), state=s)
    )
    assert clean(v.render(80, 4)) == ["header", "a", "b", "c"]


def test_fill_in_vstack_with_multiple_fixed():
    s = _state()
    v = vstack(
        text("top"), scroll(text("a"), text("b"), text("c"), state=s), text("bottom")
    )
    # height=5: top=1, bottom=1, scroll gets 3
    assert clean(v.render(80, 5)) == ["top", "a", "b", "c", "bottom"]


def test_fill_in_vstack_with_spacing():
    s = _state()
    v = vstack(
        text("top"),
        scroll(text("a"), text("b"), text("c"), text("d"), state=s),
        spacing=1,
    )
    # height=5: top=1, spacing=1, scroll gets 3
    assert clean(v.render(80, 5)) == ["top", "", "a", "b", "c"]


def test_fill_returns_empty_without_parent_height():
    s = _state()
    sc = scroll(text("a"), state=s)
    assert clean(sc.render(80)) == []


def test_fill_clamps_offset():
    s = _state(100)
    sc = scroll(text("a"), text("b"), text("c"), state=s)
    result = clean(sc.render(80, 2))
    assert result == ["b", "c"]
    assert s.offset == 1


def test_fill_inside_box():
    s = _state()
    b = box(scroll(text("a"), text("b"), text("c"), text("d"), state=s))
    # box adds 2 lines (top+bottom border), so scroll gets height-2
    result = clean(b.render(80, 5))
    assert len(result) == 5
    # First and last are borders, middle 3 are scroll content
    assert result[1].strip("│ ") == "a"
    assert result[2].strip("│ ") == "b"
    assert result[3].strip("│ ") == "c"


# ── Render feeds back dimensions ────────────────────────────────────


def test_render_feeds_back_fixed_height():
    s = _state()
    scroll(text("a"), text("b"), text("c"), state=s, height=2).render(80)
    assert s.height == 2
    assert s.total == 3


def test_render_feeds_back_fill_height():
    s = _state()
    scroll(text("a"), text("b"), state=s).render(80, 10)
    assert s.height == 10
    assert s.total == 2


def test_dimensions_update_on_rerender():
    s = _state()
    sc1 = scroll(text("a"), text("b"), state=s, height=5)
    sc1.render(80)
    assert s.total == 2
    assert s.height == 5
    # Simulate rerender with different children
    sc2 = scroll(text("a"), text("b"), text("c"), text("d"), state=s, height=3)
    sc2.render(80)
    assert s.total == 4
    assert s.height == 3


# ── Shared state across renders ─────────────────────────────────────


def test_state_persists_offset_across_renders():
    s = _state()
    s.height = 3
    s.total = 10
    s.scroll_down(5)
    # New Scroll reads offset from state
    result = clean(
        scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    )
    assert result == ["5", "6", "7"]


def test_scroll_down_then_render():
    s = _state()
    # First render to set dimensions
    scroll(text("a"), text("b"), text("c"), text("d"), state=s, height=2).render(80)
    s.scroll_down()
    result = clean(
        scroll(text("a"), text("b"), text("c"), text("d"), state=s, height=2).render(80)
    )
    assert result == ["b", "c"]


def test_page_down_then_render():
    s = _state()
    scroll(*[text(str(i)) for i in range(20)], state=s, height=5).render(80)
    s.page_down()
    result = clean(
        scroll(*[text(str(i)) for i in range(20)], state=s, height=5).render(80)
    )
    assert result == ["5", "6", "7", "8", "9"]


def test_page_up_from_middle():
    s = _state()
    scroll(*[text(str(i)) for i in range(20)], state=s, height=5).render(80)
    s.scroll_down(10)
    s.page_up()
    result = clean(
        scroll(*[text(str(i)) for i in range(20)], state=s, height=5).render(80)
    )
    assert result == ["5", "6", "7", "8", "9"]


def test_scroll_to_bottom_then_render():
    s = _state()
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    s.scroll_to_bottom()
    result = clean(
        scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    )
    assert result == ["7", "8", "9"]


def test_scroll_to_top_then_render():
    s = _state(5)
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    s.scroll_to_top()
    result = clean(
        scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    )
    assert result == ["0", "1", "2"]


# ── ScrollState edge cases ──────────────────────────────────────────


def test_scroll_state_initial():
    s = ScrollState()
    assert s.offset == 0
    assert s.height == 0
    assert s.total == 0
    assert s.max_offset == 0


def test_scroll_state_scroll_down():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.scroll_down(3)
    assert s.offset == 3


def test_scroll_state_scroll_down_clamps():
    s = ScrollState()
    s.height = 5
    s.total = 10
    s.scroll_down(100)
    assert s.offset == 5


def test_scroll_state_scroll_up():
    s = ScrollState()
    s.offset = 5
    s.scroll_up(3)
    assert s.offset == 2


def test_scroll_state_scroll_up_clamps():
    s = ScrollState()
    s.offset = 2
    s.scroll_up(10)
    assert s.offset == 0


def test_scroll_state_scroll_up_from_zero():
    s = ScrollState()
    s.scroll_up()
    assert s.offset == 0


def test_scroll_state_scroll_down_when_content_fits():
    s = ScrollState()
    s.height = 10
    s.total = 5
    s.scroll_down()
    assert s.offset == 0  # max_offset is 0


def test_scroll_state_page_down():
    s = ScrollState()
    s.height = 10
    s.total = 50
    s.page_down()
    assert s.offset == 10


def test_scroll_state_page_down_clamps():
    s = ScrollState()
    s.height = 10
    s.total = 15
    s.page_down()
    assert s.offset == 5  # max_offset


def test_scroll_state_page_up():
    s = ScrollState()
    s.height = 10
    s.total = 50
    s.offset = 20
    s.page_up()
    assert s.offset == 10


def test_scroll_state_page_up_clamps():
    s = ScrollState()
    s.height = 10
    s.total = 50
    s.offset = 5
    s.page_up()
    assert s.offset == 0


def test_scroll_state_page_down_then_up_roundtrip():
    s = ScrollState()
    s.height = 10
    s.total = 100
    s.page_down()
    s.page_down()
    s.page_up()
    assert s.offset == 10


def test_scroll_state_to_top():
    s = ScrollState()
    s.offset = 15
    s.scroll_to_top()
    assert s.offset == 0


def test_scroll_state_to_bottom():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.scroll_to_bottom()
    assert s.offset == 15


def test_scroll_state_to_bottom_when_content_fits():
    s = ScrollState()
    s.height = 10
    s.total = 3
    s.scroll_to_bottom()
    assert s.offset == 0


def test_scroll_state_max_offset():
    s = ScrollState()
    s.height = 5
    s.total = 20
    assert s.max_offset == 15


def test_scroll_state_max_offset_content_fits():
    s = ScrollState()
    s.height = 10
    s.total = 3
    assert s.max_offset == 0


def test_scroll_state_max_offset_exact():
    s = ScrollState()
    s.height = 5
    s.total = 5
    assert s.max_offset == 0


def test_scroll_state_scroll_n_steps():
    s = ScrollState()
    s.height = 5
    s.total = 100
    s.scroll_down(50)
    assert s.offset == 50
    s.scroll_up(20)
    assert s.offset == 30


def test_scroll_state_before_first_render():
    """scroll_down before any render (height/total still 0) should not crash."""
    s = ScrollState()
    s.scroll_down()
    assert s.offset == 0
    s.page_down()
    assert s.offset == 0
    s.scroll_to_bottom()
    assert s.offset == 0


def test_scroll_to_visible_above():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 10
    s.scroll_to_visible(7)
    assert s.offset == 7


def test_scroll_to_visible_below():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 0
    s.scroll_to_visible(8)
    assert s.offset == 4


def test_scroll_to_visible_already_visible():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 5
    s.scroll_to_visible(7)
    assert s.offset == 5  # unchanged


def test_scroll_to_visible_at_top_edge():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 5
    s.scroll_to_visible(5)
    assert s.offset == 5  # exactly at top edge, still visible


def test_scroll_to_visible_at_bottom_edge():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 5
    s.scroll_to_visible(9)
    assert s.offset == 5  # exactly at bottom edge, still visible


# ── Follow mode ────────────────────────────────────────────────────


def test_follow_disabled_by_default():
    s = ScrollState()
    assert s.follow is False


def test_follow_sticks_to_bottom():
    s = ScrollState(follow=True)
    items = [text(str(i)) for i in range(10)]
    scroll(*items, state=s, height=3).render(80)
    assert s.offset == 7  # max_offset = 10 - 3

    # Add more items — follow should track
    items.extend(text(str(i)) for i in range(10, 20))
    scroll(*items, state=s, height=3).render(80)
    assert s.offset == 17  # max_offset = 20 - 3


def test_scroll_up_disables_follow():
    s = ScrollState(follow=True)
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    s.scroll_up(2)
    assert s.follow is False
    assert s.offset == 5

    # Re-render — should NOT jump to bottom
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    assert s.offset == 5


def test_follow_reengages_at_bottom():
    s = ScrollState(follow=True)
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    s.scroll_up(2)
    assert s.follow is False

    # Scroll back down to bottom
    s.scroll_down(2)
    scroll(*[text(str(i)) for i in range(10)], state=s, height=3).render(80)
    assert s.follow is True


def test_follow_with_growing_content():
    s = ScrollState(follow=True)
    items = [text(str(i)) for i in range(5)]
    scroll(*items, state=s, height=3).render(80)
    assert s.offset == 2  # following bottom

    # User scrolls up
    s.scroll_up(1)
    assert s.follow is False

    # Content grows — should stay at user's position
    items.extend([text(str(i)) for i in range(5, 10)])
    scroll(*items, state=s, height=3).render(80)
    assert s.offset == 1  # didn't jump


def test_page_up_disables_follow():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.offset = 15
    s.page_up()
    assert s.follow is False


def test_scroll_down_does_not_disable_follow():
    s = ScrollState()
    s.follow = True
    s.height = 5
    s.total = 20
    s.scroll_down(3)
    assert s.follow is True  # scroll_down should not set follow=False


# ── Scrollbar component ────────────────────────────────────────────


def test_scrollbar_returns_one_char_wide():
    s = _state()
    scroll(*[text(str(i)) for i in range(20)], state=s, height=5).render(80)
    lines = scrollbar(state=s).render(1, 5)
    assert len(lines) == 5
    for line in lines:
        assert display_width(line) == 1


def test_scrollbar_empty_when_content_fits():
    s = _state()
    scroll(text("a"), text("b"), state=s, height=5).render(80)
    lines = scrollbar(state=s).render(1, 5)
    assert all(line == "" for line in lines)


def test_scrollbar_thumb_moves_with_offset():
    items = [text(str(i)) for i in range(100)]

    s1 = _state(0)
    scroll(*items, state=s1, height=10).render(80)
    bar_top = [strip_ansi(l) for l in scrollbar(state=s1).render(1, 10)]

    s2 = _state(90)
    scroll(*items, state=s2, height=10).render(80)
    bar_bot = [strip_ansi(l) for l in scrollbar(state=s2).render(1, 10)]

    assert bar_top != bar_bot


def test_scrollbar_composes_with_hstack():
    s = _state()
    view = vstack(
        hstack(
            scroll(*[text(str(i)) for i in range(20)], state=s),
            scrollbar(state=s),
        ),
    )
    lines = view.render(20, 5)
    assert len(lines) == 5


def test_scrollbar_custom_render_fn():
    def my_bar(h: int, total: int, offset: int) -> list[str]:
        return ["X"] * h

    s = _state()
    scroll(*[text(str(i)) for i in range(20)], state=s, height=3).render(80)
    lines = scrollbar(state=s, render_fn=my_bar).render(1, 3)
    assert lines == ["X", "X", "X"]


def test_scrollbar_default_fn_directly():
    col = scrollbar_default(10, 100, 0)
    assert len(col) == 10
    # Thumb should be near the top
    assert any(strip_ansi(c) == "┃" for c in col[:3])


def test_scrollbar_default_at_bottom():
    col = scrollbar_default(10, 100, 90)
    assert len(col) == 10
    # Thumb should be near the bottom
    assert any(strip_ansi(c) == "┃" for c in col[-3:])


def test_scrollbar_default_content_fits():
    col = scrollbar_default(10, 5, 0)
    # No scrollbar needed — all empty
    assert all(c == "" for c in col)


def test_scrollbar_default_single_row():
    col = scrollbar_default(1, 100, 0)
    assert len(col) == 1
    assert strip_ansi(col[0]) == "┃"


def test_scrollbar_default_monotonic():
    """Thumb position should only move forward as offset increases."""

    def thumb_top(offset: int) -> int:
        col = scrollbar_default(20, 200, offset)
        for i, c in enumerate(col):
            if strip_ansi(c) == "┃":
                return i
        return 20

    positions = [thumb_top(o) for o in range(0, 181, 10)]
    # Should be monotonically non-decreasing
    for i in range(1, len(positions)):
        assert positions[i] >= positions[i - 1]


# ── scroll_to_top / scroll_to_bottom follow interaction ───────────


def test_scroll_to_top_disables_follow():
    s = ScrollState(follow=True)
    s.height = 5
    s.total = 20
    s.offset = 15
    s.scroll_to_top()
    assert s.offset == 0
    assert s.follow is False


def test_scroll_to_bottom_enables_follow():
    s = ScrollState()
    s.height = 5
    s.total = 20
    s.scroll_to_bottom()
    assert s.offset == 15
    assert s.follow is True


def test_scroll_always_grows_horizontally():
    s = ScrollState()
    sc = scroll(text("short"), state=s, height=5)
    assert sc.flex_grow_width()


# ── Scroll + Scrollbar end-to-end ─────────────────────────────────


def test_scroll_and_scrollbar_share_state():
    """Scrollbar reads from same state that Scroll writes to."""
    s = ScrollState()
    items = [text(str(i)) for i in range(50)]
    # Scroll writes height/total/offset
    scroll(*items, state=s, height=10).render(80)
    assert s.height == 10
    assert s.total == 50
    # Scrollbar reads them
    bar = scrollbar(state=s).render(1, 10)
    assert len(bar) == 10
    assert any(strip_ansi(c) == "┃" for c in bar)


def test_follow_tracks_growing_content_end_to_end():
    """Simulates streaming content: follow keeps viewport at bottom."""
    s = ScrollState(follow=True)
    items = [text(str(i)) for i in range(5)]
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["2", "3", "4"]

    # Add more content
    items.extend(text(str(i)) for i in range(5, 15))
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["12", "13", "14"]

    # User scrolls up — follow disengages
    s.scroll_up(5)
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["7", "8", "9"]

    # Content grows — viewport stays
    items.extend(text(str(i)) for i in range(15, 25))
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["7", "8", "9"]

    # User hits End — follow re-engages
    s.scroll_to_bottom()
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["22", "23", "24"]

    # Content grows — follows again
    items.extend(text(str(i)) for i in range(25, 30))
    result = clean(scroll(*items, state=s, height=3).render(80))
    assert result == ["27", "28", "29"]
