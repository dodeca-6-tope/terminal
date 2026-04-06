"""Tests for Spacer component."""

from terminal import spacer
from terminal.measure import strip_ansi


def test_fills_width():
    assert strip_ansi(spacer().render(10)[0]) == " " * 10


def test_flex_grow():
    assert spacer().flex_grow_width()


def test_flex_basis_zero():
    assert spacer().flex_basis() == 0
