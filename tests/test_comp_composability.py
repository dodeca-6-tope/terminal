"""Tests for component composability — any nesting should work."""

from terminal import (
    bold,
    color,
    cond,
    foreach,
    hstack,
    table,
    table_row,
    text,
    vstack,
)
from terminal.measure import strip_ansi


def clean(lines: list[str]) -> list[str]:
    return [strip_ansi(l) for l in lines]


def test_vstack_in_hstack():
    lines = clean(hstack(vstack(text("a"), text("b")), text("c"), spacing=1).render(20))
    assert len(lines) == 2


def test_hstack_in_vstack():
    lines = clean(vstack(hstack(text("a"), text("b"), spacing=1), text("c")).render(20))
    assert lines[0] == "a b"
    assert lines[1] == "c"


def test_table_in_vstack():
    lines = clean(
        vstack(text(bold("header")), table(table_row(text("x"), text("y")))).render(80)
    )
    assert len(lines) == 2


def test_foreach_in_hstack():
    fe = foreach(["a", "b"], lambda x, i: text(x))
    lines = clean(hstack(fe, text("side"), spacing=2).render(30))
    assert "a" in lines[0]
    assert "side" in lines[0]


def test_cond_in_hstack_between():
    result = clean(
        hstack(cond(False, text("L")), text("R"), justify_content="between").render(20)
    )[0]
    assert result.rstrip().endswith("R")


def test_deeply_nested():
    tree = vstack(
        hstack(text("title"), text("v1.0"), justify_content="between"),
        table(table_row(text(">"), text("item"), text(color(2, "ok")))),
        hstack(text("[q] quit"), text("[h] help"), wrap=True, spacing=2),
    )
    assert len(tree.render(60)) >= 3
