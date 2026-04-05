"""Tests for Cond component."""

from terminal import cond, text
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_true_renders_child():
    assert clean(cond(True, text("yes")).render(80)) == ["yes"]


def test_false_renders_empty():
    assert cond(False, text("no")).render(80) == []


def test_truthy_values():
    assert clean(cond(1, text("yes")).render(80)) == ["yes"]
    assert cond(0, text("no")).render(80) == []
    assert cond("", text("no")).render(80) == []
    assert clean(cond("x", text("yes")).render(80)) == ["yes"]


def test_flex_basis():
    assert cond(True, text("hello")).flex_basis() == 5
    assert cond(False, text("hello")).flex_basis() == 0


def test_flex_grow_height_true():
    from terminal.components.scroll import ScrollState

    s = ScrollState()
    from terminal import scroll

    assert cond(True, scroll(text("a"), state=s)).flex_grow_height() is True


def test_flex_grow_height_false_condition():
    from terminal.components.scroll import ScrollState

    s = ScrollState()
    from terminal import scroll

    assert cond(False, scroll(text("a"), state=s)).flex_grow_height() is False


def test_flex_grow_height_non_grower():
    assert cond(True, text("a")).flex_grow_height() is False


def test_height_passed_to_child():
    from terminal.components.scroll import ScrollState

    s = ScrollState()
    from terminal import scroll

    c = cond(True, scroll(text("a"), text("b"), text("c"), state=s))
    result = clean(c.render(80, 2))
    assert result == ["a", "b"]
