"""Renderer accepts any Sequence-shaped children, not just tuples."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import overload

from conftest import render

import ttyz as t
from ttyz.components.base import Node


class SeqView(Sequence[Node]):
    """Minimal Sequence — __len__ + __getitem__, explicitly not a tuple."""

    def __init__(self, items: Sequence[Node]) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    @overload
    def __getitem__(self, i: int) -> Node: ...
    @overload
    def __getitem__(self, i: slice) -> Sequence[Node]: ...
    def __getitem__(self, i: int | slice) -> Node | Sequence[Node]:
        return self._items[i]


def _swap(node: Node) -> Node:
    """Recursively replace tuple children with SeqView in place."""
    kids = node.children
    if isinstance(kids, tuple):
        for c in kids:
            _swap(c)
        if kids:
            node.children = SeqView(kids)
    return node


def _same(build: Callable[[], Node]) -> None:
    baseline = render(build(), 40, 12)
    sequenced = render(_swap(build()), 40, 12)
    assert sequenced == baseline


def test_hstack_accepts_sequence():
    _same(lambda: t.hstack(t.text("A"), t.text("B"), t.text("C"), spacing=1, grow=1))


def test_hstack_wrap_accepts_sequence():
    _same(
        lambda: t.hstack(
            t.text("alpha"),
            t.text("beta"),
            t.text("gamma"),
            spacing=1,
            wrap=True,
        )
    )


def test_vstack_non_flex_accepts_sequence():
    _same(lambda: t.vstack(t.text("A"), t.text("B"), t.text("C"), spacing=1))


def test_vstack_flex_accepts_sequence():
    _same(
        lambda: t.vstack(
            t.text("top"),
            t.text("grow", grow=1),
            t.text("bottom"),
            grow=1,
        )
    )


def test_zstack_accepts_sequence():
    _same(lambda: t.zstack(t.text("bottom"), t.text("TOP")))


def test_box_accepts_sequence():
    _same(lambda: t.box(t.text("inside"), title="Title"))


def test_scroll_accepts_sequence():
    _same(
        lambda: t.scroll(
            t.text("a"),
            t.text("b"),
            t.text("c"),
            t.text("d"),
            state=t.ScrollState(),
            height="3",
        )
    )


def test_foreach_accepts_sequence():
    _same(lambda: t.foreach(["one", "two", "three"], lambda s, i: t.text(f"{i}:{s}")))


def test_cond_accepts_sequence():
    # grow=1 (mismatching child.grow=0) forces cond() to build a Cond wrapper
    # rather than short-circuit to the child, so the Sequence-handling path
    # inside Cond is exercised.
    _same(lambda: t.cond(True, t.text("shown"), grow=1))


def test_nested_containers_accept_sequence():
    _same(
        lambda: t.vstack(
            t.hstack(t.text("L"), t.text("R"), spacing=1),
            t.box(t.vstack(t.text("a"), t.text("b"))),
            t.zstack(t.text("layer"), t.text("top")),
            spacing=1,
        )
    )
