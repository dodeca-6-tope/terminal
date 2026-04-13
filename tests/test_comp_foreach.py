"""Tests for ForEach component."""

from helpers import clean, vis

from ttyz import foreach, text


def test_renders_items():
    assert vis(
        foreach(["a", "b", "c"], lambda item, i: text(f"{i}:{item}")).render(80)
    ) == [
        "0:a",
        "1:b",
        "2:c",
    ]


def test_empty_list():
    items: list[str] = []
    assert foreach(items, lambda item, i: text(item)).render(80) == []


def test_flex_basis():
    assert foreach(["hi", "hello"], lambda item, i: text(item)).flex_basis == 5


def test_children_get_outer_height():
    """text() children ignore h, so render is the same with or without height."""
    items = ["a", "b", "c"]
    f = foreach(items, lambda item, i: text(item))
    assert clean(f.render(80)) == clean(f.render(80, 10)) == ["a", "b", "c"]
