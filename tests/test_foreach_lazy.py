"""foreach is lazy — render_fn runs only for items that actually render."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import pytest
from conftest import render

import ttyz as t
from ttyz.components.base import Node


def _empty_int_list() -> list[int]:
    return []


@dataclass
class _Counter:
    calls: int = 0
    indices: list[int] = field(default_factory=_empty_int_list)


def _counting_fn() -> tuple[Callable[[object, int], Node], _Counter]:
    """Return (render_fn, counter) — counter.calls increments per invocation."""
    counter = _Counter()

    def render_fn(item: object, i: int) -> Node:
        counter.calls += 1
        counter.indices.append(i)
        return t.text(f"{i}:{item}")

    return render_fn, counter


def test_construction_does_not_call_render_fn() -> None:
    """Building foreach(range(N), fn) does no work up front."""
    fn, counter = _counting_fn()
    t.foreach(range(10_000_000), fn)
    assert counter.calls == 0


def test_scroll_renders_only_the_visible_window() -> None:
    """Inside scroll, render_fn runs only for items in the viewport."""
    fn, counter = _counting_fn()
    tree = t.scroll(t.foreach(range(10_000_000), fn), state=t.ScrollState(), height="5")
    render(tree, 20, 5)
    assert counter.calls == 5
    assert counter.indices == [0, 1, 2, 3, 4]


def test_foreach_at_root_respects_buffer_height() -> None:
    """A foreach rendered at the root with h=3 runs render_fn exactly 3 times."""
    fn, counter = _counting_fn()
    render(t.foreach(range(1_000_000), fn), 20, 3)
    assert counter.calls == 3
    assert counter.indices == [0, 1, 2]


def test_flex_parent_runs_render_fn_once_per_index() -> None:
    """A flex parent measures then renders; render_fn runs once per index,
    not twice — the two passes agree on which node an index maps to.

    N is small because a lazy foreach inside a flex parent iterates every
    item during the measure pass (flex needs intrinsic size).  The test
    is about per-index parity, not iteration scale.
    """
    fn, counter = _counting_fn()
    tree = t.vstack(
        t.foreach(range(50), fn),
        t.text("bottom", grow=1),
        grow=1,
    )
    render(tree, 20, 10)
    assert counter.calls == len(set(counter.indices)), (
        f"render_fn called {counter.calls} times for "
        f"{len(set(counter.indices))} unique indices"
    )


def test_each_render_call_reinvokes_render_fn() -> None:
    """render_fn runs fresh on every render_to_buffer — no caching persists."""
    fn, counter = _counting_fn()
    tree = t.foreach(range(5), fn)
    render(tree, 20, 5)
    first = counter.calls
    render(tree, 20, 5)
    assert counter.calls == first * 2


def test_output_matches_eager_vstack() -> None:
    """Lazy foreach and an eager vstack of the same items render identically."""
    items = ["alpha", "beta", "gamma"]
    lazy_out = render(t.foreach(items, lambda s, i: t.text(f"{i}:{s}")), 20, 5)
    eager_out = render(
        t.vstack(*[t.text(f"{i}:{s}") for i, s in enumerate(items)]), 20, 5
    )
    assert lazy_out == eager_out


def test_render_fn_exception_propagates() -> None:
    """An exception raised by render_fn surfaces through render_to_buffer."""

    class Boom(Exception):
        pass

    def boom(item: object, i: int) -> Node:
        raise Boom("no")

    tree = t.foreach([1, 2, 3], boom)
    buf = t.Buffer(20, 5)
    with pytest.raises(Boom):
        t.render_to_buffer(tree, buf, 5)


def test_slicing_children_raises() -> None:
    """Slicing foreach.children is rejected with TypeError (unlike a tuple)."""
    tree = t.foreach(range(10), lambda v, i: t.text(str(v)))
    with pytest.raises(TypeError):
        tree.children[1:3]


def test_items_mutation_reflected_on_next_render() -> None:
    """items is held by reference; later mutations show up on the next render."""
    items = ["a", "b"]
    tree = t.foreach(items, lambda s, i: t.text(f"{i}:{s}"))
    first = render(tree, 20, 5)
    items.append("c")
    second = render(tree, 20, 5)
    assert len(second) == len(first) + 1
    assert any("2:c" in line for line in second)
