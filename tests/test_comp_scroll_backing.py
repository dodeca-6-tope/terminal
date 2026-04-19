"""Scroll accepts varargs Nodes, lists, tuples, and custom Sequences."""

from __future__ import annotations

from collections.abc import Sequence
from typing import overload

from conftest import render

import ttyz as t
from ttyz.components.base import Node


class LazySeq(Sequence[Node]):
    """Sequence that counts __getitem__ calls so we can assert laziness."""

    def __init__(self, n: int, counter: list[int]) -> None:
        self._n = n
        self._counter = counter

    def __len__(self) -> int:
        return self._n

    @overload
    def __getitem__(self, i: int) -> Node: ...
    @overload
    def __getitem__(self, i: slice) -> Sequence[Node]: ...
    def __getitem__(self, i: int | slice) -> Node | Sequence[Node]:
        if isinstance(i, slice):
            raise TypeError
        self._counter[0] += 1
        return t.text(f"row {i}")


def _state() -> t.ScrollState:
    return t.ScrollState()


def _render(node: Node, w: int, h: int) -> list[str]:
    return render(node, w, h)


def test_varargs_of_nodes_renders() -> None:
    """scroll(node1, node2, ...) — the existing pattern."""
    out = _render(
        t.scroll(t.text("a"), t.text("b"), t.text("c"), state=_state()),
        10,
        3,
    )
    assert out == ["a", "b", "c"]


def test_empty_scroll_renders() -> None:
    """scroll(state=...) with no children renders blank rows."""
    out = _render(t.scroll(state=_state()), 10, 3)
    assert out == ["", "", ""]


def test_list_as_positional_is_treated_as_backing() -> None:
    """A single list positional is the Sequence backing, not a single child."""
    nodes = [t.text("x"), t.text("y"), t.text("z")]
    node = t.scroll(nodes, state=_state())
    assert node.children is nodes
    assert _render(node, 10, 3) == ["x", "y", "z"]


def test_tuple_as_positional_is_treated_as_backing() -> None:
    """A single tuple positional is also the backing."""
    nodes = (t.text("p"), t.text("q"))
    node = t.scroll(nodes, state=_state())
    assert node.children is nodes
    assert _render(node, 10, 2) == ["p", "q"]


def test_custom_sequence_as_positional_is_lazy() -> None:
    """A custom Sequence renders lazily — only visible items are fetched."""
    counter = [0]
    out = _render(
        t.scroll(LazySeq(1_000_000, counter), state=_state(), height="5"),
        10,
        5,
    )
    assert out == [f"row {i}" for i in range(5)]
    assert counter[0] == 5


def test_mixing_varargs_and_sequence_argument_is_ambiguous() -> None:
    """A single Node positional is treated as varargs, not a Sequence."""
    # One Node positional → one child, not "this is a sequence of one Node".
    # Verified by the children slot being a tuple wrapping the single Node.
    node = t.scroll(t.text("solo"), state=_state())
    assert isinstance(node.children, tuple)
    assert len(node.children) == 1


def test_list_backing_renders_without_hash_error() -> None:
    """Regression: ccache used to tuple-key by (children, i), which fails
    for unhashable children like list.  Now keys by (id(children), i)."""
    nodes = [t.text(f"n{i}") for i in range(20)]
    out = _render(t.scroll(nodes, state=_state(), height="3"), 10, 3)
    assert out == ["n0", "n1", "n2"]


def test_sequence_backing_dedup_across_measure_and_render() -> None:
    """Custom sequence inside a flex parent: __getitem__ runs once per index."""
    counter = [0]
    tree = t.vstack(
        t.scroll(LazySeq(20, counter), state=_state(), grow=1),
        t.text("bottom"),
    )
    _render(tree, 10, 5)
    # Scroll's viewport is ~4 rows; flex measures the scroll, which doesn't
    # iterate its own children for measurement (render_scroll uses h directly).
    # So render_fn runs exactly once per visible row.
    assert counter[0] == 4
