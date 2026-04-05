"""Tests for ANSI style helpers."""

from terminal import bold, color, dim, italic, reverse
from terminal.measure import strip_ansi


def test_bold():
    assert bold("hi") == "\033[1mhi\033[0m"
    assert strip_ansi(bold("hi")) == "hi"


def test_dim():
    assert dim("hi") == "\033[2mhi\033[0m"


def test_italic():
    assert italic("hi") == "\033[3mhi\033[0m"


def test_reverse():
    assert reverse("hi") == "\033[7mhi\033[0m"


def test_color():
    assert color(1, "hi") == "\033[38;5;1mhi\033[0m"
    assert color(39, "hi") == "\033[38;5;39mhi\033[0m"


def test_composable():
    result = bold(color(1, "hi"))
    assert "\033[1m" in result
    assert "\033[38;5;1m" in result
    assert strip_ansi(result) == "hi"
