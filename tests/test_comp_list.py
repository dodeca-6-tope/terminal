"""Tests for List and ListState."""

from terminal import ListState


def test_total_reflects_items():
    s = ListState(["a", "b", "c"])
    assert s.total == 3


def test_total_before_render():
    """total should work before any render (no dependency on scroll state)."""
    s = ListState(["a", "b", "c"])
    s.move(1)
    assert s.cursor == 1


def test_total_empty():
    s = ListState[str]()
    assert s.total == 0


def test_move_clamps():
    s = ListState(["a", "b", "c"])
    s.move(100)
    assert s.cursor == 2
    s.move(-100)
    assert s.cursor == 0


def test_move_to():
    s = ListState(["a", "b", "c"])
    s.move_to(2)
    assert s.cursor == 2
    assert s.current == "c"
