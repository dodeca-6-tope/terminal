"""Tests for Terminal.readkey() with real pty input.

Writes raw byte sequences to a pty (simulating a real terminal emulator)
and asserts the key names that readkey() produces.
"""

from __future__ import annotations

import os
import pty
import sys
from collections.abc import Generator

import pytest

from terminal import TTY as Terminal
from terminal.term import Paste


@pytest.fixture
def term() -> Generator[tuple[Terminal, int], None, None]:
    master, slave = pty.openpty()
    old_stdin = sys.stdin
    with open(slave, closefd=False) as f:
        sys.stdin = f
        t = Terminal()
        with t:
            yield t, master
    sys.stdin = old_stdin
    os.close(master)
    os.close(slave)


def send(term_and_master: tuple[Terminal, int], data: bytes) -> str | Paste | None:
    t, master = term_and_master
    os.write(master, data)
    return t.readkey()


# ── Cmd+arrow → home/end ────────────────────────────────────────────


def test_cmd_left(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x01") == "home"


def test_cmd_right(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x05") == "end"


# ── Option+arrow → word jump ────────────────────────────────────────


def test_option_left_double_escape(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b\x1b[D") == "word-left"


def test_option_right_double_escape(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b\x1b[C") == "word-right"


def test_option_left_modifier(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[1;3D") == "word-left"


def test_option_right_modifier(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[1;3C") == "word-right"


def test_option_left_esc_b(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1bb") == "word-left"


def test_option_right_esc_f(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1bf") == "word-right"


# ── Mouse scroll (SGR mode) ─────────────────────────────────────────


def test_scroll_up_mouse(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[<64;10;20M") == "scroll-up"


def test_scroll_down_mouse(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[<65;10;20M") == "scroll-down"


def test_mouse_click_ignored(term: tuple[Terminal, int]) -> None:
    """Regular mouse click (button 0) should return None."""
    assert send(term, b"\x1b[<0;10;20M") is None


def test_mouse_release_ignored(term: tuple[Terminal, int]) -> None:
    """Mouse release (lowercase m) should return None for non-scroll."""
    assert send(term, b"\x1b[<0;10;20m") is None


# ── Basic keys ───────────────────────────────────────────────────────


def test_arrow_up(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[A") == "up"


def test_arrow_down(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[B") == "down"


def test_arrow_right(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[C") == "right"


def test_arrow_left(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[D") == "left"


def test_enter(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\r") == "enter"


def test_tab(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\t") == "tab"


def test_shift_tab(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[Z") == "shift-tab"


def test_backspace(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x7f") == "backspace"


def test_delete(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[3~") == "delete"


def test_page_up(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[5~") == "page-up"


def test_page_down(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[6~") == "page-down"


def test_home(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[H") == "home"


def test_end(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[F") == "end"


def test_printable_char(term: tuple[Terminal, int]) -> None:
    assert send(term, b"a") == "a"


def test_space(term: tuple[Terminal, int]) -> None:
    assert send(term, b" ") == "space"


def test_ctrl_q(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x11") == "ctrl-q"


def test_delete_word(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x17") == "delete-word"


def test_clear_line(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x15") == "clear-line"


def test_esc(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b") == "esc"


def test_focus(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[I") == "focus"


def test_focus_lost(term: tuple[Terminal, int]) -> None:
    assert send(term, b"\x1b[O") is None
