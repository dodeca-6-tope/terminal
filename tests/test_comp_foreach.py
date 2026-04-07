"""Tests for ForEach component."""

from terminal import foreach, text
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_renders_items():
    fe = foreach(["a", "b", "c"], lambda item, i: text(f"{i}:{item}"))
    assert clean(fe.render(80)) == ["0:a", "1:b", "2:c"]


def test_empty_list():
    items: list[str] = []
    assert clean(foreach(items, lambda item, i: text(item)).render(80)) == []


def test_flex_basis():
    assert foreach(["hi", "hello"], lambda item, i: text(item)).flex_basis == 5
