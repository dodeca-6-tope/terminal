"""Tests for Spacer component."""

from terminal import hstack, spacer, text, vstack, zstack
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def vis(lines: list[str]) -> list[str]:
    """Replace spaces with dots so layouts are visible in assertions."""
    return [l.replace(" ", "·") for l in clean(lines)]


# ── HStack: expands horizontally, not vertically ───────────────────


def test_hstack_spacer_right():
    #                        ├── spacer ──┤├end┤
    assert vis(hstack(spacer(), text("end")).render(15)) == [
        "············end",
    ]


def test_hstack_spacer_left():
    #                        ├str─┤├── spacer ──┤
    assert vis(hstack(text("start"), spacer()).render(15)) == [
        "start··········",
    ]


def test_hstack_spacer_both_sides():
    #                        ├spacer┤├mid┤├spacer┤
    assert vis(hstack(spacer(), text("mid"), spacer()).render(15)) == [
        "······mid······",
    ]


def test_hstack_spacer_does_not_add_rows():
    assert vis(hstack(text("a"), spacer(), text("b")).render(10)) == [
        "a········b",
    ]


# ── VStack: expands vertically, not horizontally ───────────────────


def test_vstack_spacer_pushes_down():
    assert vis(vstack(spacer(), text("bot")).render(3, 4)) == [
        "",
        "",
        "",
        "bot",
    ]


def test_vstack_spacer_pushes_up():
    assert vis(vstack(text("top"), spacer()).render(3, 4)) == [
        "top",
        "",
        "",
        "",
    ]


def test_vstack_spacer_between():
    assert vis(vstack(text("hi"), spacer(), text("lo")).render(2, 5)) == [
        "hi",
        "",
        "",
        "",
        "lo",
    ]


def test_vstack_spacer_no_height_constraint():
    """Without height, no flex context — spacer is just one empty line."""
    assert vis(vstack(text("a"), spacer(), text("b")).render(1)) == [
        "a",
        "",
        "b",
    ]


# ── ZStack: expands on both axes ───────────────────────────────────


def test_zstack_spacer_fills_canvas():
    assert vis(zstack(spacer()).render(4, 3)) == [
        "····",
        "····",
        "····",
    ]


def test_zstack_spacer_behind_content():
    assert vis(zstack(spacer(), text("hi")).render(4, 2)) == [
        "hi··",
        "····",
    ]


# ── Flex properties ─────────────────────────────────────────────────


def test_grow_is_one():
    assert spacer().grow == 1


def test_flex_basis_default():
    assert spacer().flex_basis == 0


def test_min_length():
    assert spacer(min_length=5).flex_basis == 5


def test_does_not_propagate_grow():
    assert not hstack(text("a"), spacer()).grow
    assert not vstack(text("a"), spacer()).grow


# ── No cross-axis leak ─────────────────────────────────────────────


def test_hstack_with_spacer_does_not_steal_height():
    header = hstack(text("L"), spacer(), text("R"))
    lines = vis(vstack(header, text("scene")).render(5, 4))
    assert lines == [
        "L···R",
        "scene",
    ]


def test_vstack_with_spacer_does_not_steal_width():
    sidebar = vstack(text("T"), spacer(), text("B"))
    lines = vis(hstack(sidebar, text("scene")).render(6, 3))
    assert lines == [
        "Tscene",
        "······",
        "B·····",
    ]
