"""Tests for display_width and strip_ansi."""

from terminal import display_width, strip_ansi


def test_plain_ascii():
    assert display_width("hello") == 5

def test_ansi_codes_ignored():
    assert display_width("\033[1mhello\033[0m") == 5

def test_wide_chars():
    assert display_width("你好") == 4

def test_mixed_ansi_and_wide():
    assert display_width("\033[31m你好\033[0m world") == 10

def test_strip_ansi():
    assert strip_ansi("\033[1;31mhello\033[0m") == "hello"

def test_strip_ansi_no_codes():
    assert strip_ansi("hello") == "hello"

def test_empty():
    assert display_width("") == 0
    assert strip_ansi("") == ""
