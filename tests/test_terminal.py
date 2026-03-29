"""Tests for Terminal.readkey() with real pty input.

Writes raw byte sequences to a pty (simulating a real terminal emulator)
and asserts the key names that readkey() produces.
"""

import os
import pty
import sys

import pytest

from terminal import Terminal


@pytest.fixture
def term():
    master, slave = pty.openpty()
    old_stdin = sys.stdin
    sys.stdin = open(slave, closefd=False)
    t = Terminal()
    with t:
        yield t, master
    sys.stdin.close()
    sys.stdin = old_stdin
    os.close(master)
    os.close(slave)


def send(term_and_master, data: bytes):
    t, master = term_and_master
    os.write(master, data)
    return t.readkey()


# ── Cmd+arrow → home/end ────────────────────────────────────────────

def test_cmd_left(term):
    assert send(term, b"\x01") == "home"

def test_cmd_right(term):
    assert send(term, b"\x05") == "end"


# ── Option+arrow → word jump ────────────────────────────────────────

def test_option_left_double_escape(term):
    assert send(term, b"\x1b\x1b[D") == "word-left"

def test_option_right_double_escape(term):
    assert send(term, b"\x1b\x1b[C") == "word-right"

def test_option_left_modifier(term):
    assert send(term, b"\x1b[1;3D") == "word-left"

def test_option_right_modifier(term):
    assert send(term, b"\x1b[1;3C") == "word-right"

def test_option_left_esc_b(term):
    assert send(term, b"\x1bb") == "word-left"

def test_option_right_esc_f(term):
    assert send(term, b"\x1bf") == "word-right"
