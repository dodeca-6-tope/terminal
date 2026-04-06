"""Tests for key parsing — pure functions, no TTY needed."""

from terminal.keys import Paste, parse_csi, parse_sgr_mouse

# ── CSI parsing ─────────────────────────────────────────────────────


def test_csi_arrows():
    assert parse_csi(b"A") == "up"
    assert parse_csi(b"B") == "down"
    assert parse_csi(b"C") == "right"
    assert parse_csi(b"D") == "left"


def test_csi_home_end():
    assert parse_csi(b"H") == "home"
    assert parse_csi(b"F") == "end"


def test_csi_special_keys():
    assert parse_csi(b"Z") == "shift-tab"
    assert parse_csi(b"3~") == "delete"
    assert parse_csi(b"5~") == "page-up"
    assert parse_csi(b"6~") == "page-down"


def test_csi_focus():
    assert parse_csi(b"I") == "focus"


def test_csi_focus_lost():
    assert parse_csi(b"O") is None


def test_csi_modifier_option_arrows():
    assert parse_csi(b"1;3C") == "word-right"
    assert parse_csi(b"1;3D") == "word-left"


def test_csi_modifier_cmd_arrows():
    assert parse_csi(b"1;9C") == "word-right"
    assert parse_csi(b"1;9D") == "word-left"


def test_csi_modifier_shift_arrows():
    assert parse_csi(b"1;2C") == "end"
    assert parse_csi(b"1;2D") == "home"


def test_csi_unknown_returns_none():
    assert parse_csi(b"99~") is None
    assert parse_csi(b"X") is None


# ── SGR mouse parsing ──────────────────────────────────────────────


def test_sgr_scroll_up():
    assert parse_sgr_mouse(b"64;10;20M") == "scroll-up"


def test_sgr_scroll_down():
    assert parse_sgr_mouse(b"65;10;20M") == "scroll-down"


def test_sgr_click_ignored():
    assert parse_sgr_mouse(b"0;10;20M") is None


def test_sgr_release_ignored():
    assert parse_sgr_mouse(b"0;10;20m") is None


def test_sgr_malformed_returns_none():
    assert parse_sgr_mouse(b"garbage") is None
    assert parse_sgr_mouse(b"") is None


# ── KeyReader — public contract: read() returns correct keys ───────

import os
from terminal.keys import KeyReader


def _pipe_reader(data: bytes) -> KeyReader:
    """Create a KeyReader backed by a pipe pre-loaded with data."""
    r, w = os.pipe()
    os.write(w, data)
    os.close(w)
    return KeyReader(r)


def test_reader_returns_none_on_empty():
    kr = _pipe_reader(b"")
    assert kr.read(0) is None


def test_reader_reads_printable_chars():
    kr = _pipe_reader(b"abc")
    assert kr.read(0) == "a"
    assert kr.read(0) == "b"
    assert kr.read(0) == "c"
    assert kr.read(0) is None


def test_reader_reads_special_keys():
    kr = _pipe_reader(b"\r\t\x7f")
    assert kr.read(0) == "enter"
    assert kr.read(0) == "tab"
    assert kr.read(0) == "backspace"


def test_reader_reads_arrow_keys():
    kr = _pipe_reader(b"\x1b[A\x1b[B\x1b[C\x1b[D")
    assert kr.read(0) == "up"
    assert kr.read(0) == "down"
    assert kr.read(0) == "right"
    assert kr.read(0) == "left"
    assert kr.read(0) is None


def test_reader_reads_mouse_scroll():
    kr = _pipe_reader(b"\x1b[<64;10;20M\x1b[<65;10;20M")
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) is None


def test_reader_consecutive_scroll_events_dont_merge():
    """Rapid scroll events should each be returned individually."""
    kr = _pipe_reader(b"\x1b[<64;5;10M\x1b[<64;5;10M\x1b[<64;5;10M")
    events = []
    while (k := kr.read(0)) is not None:
        events.append(k)
    assert events == ["scroll-up", "scroll-up", "scroll-up"]


def test_reader_interleaved_keys_and_escapes():
    kr = _pipe_reader(b"x\x1b[Ay\x1b[<65;1;1M")
    assert kr.read(0) == "x"
    assert kr.read(0) == "up"
    assert kr.read(0) == "y"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) is None


def test_reader_escape_does_not_consume_next_event():
    """Parsing one escape sequence must not eat bytes from the next."""
    kr = _pipe_reader(b"\x1b[Aa")
    assert kr.read(0) == "up"
    assert kr.read(0) == "a"


def test_reader_mouse_followed_by_keypress():
    """Mouse event bytes must not bleed into subsequent key."""
    kr = _pipe_reader(b"\x1b[<64;100;200Mx")
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "x"
    assert kr.read(0) is None


def test_reader_many_rapid_scroll_events():
    """Simulate rapid trackpad: many scroll events in one read buffer."""
    event = b"\x1b[<64;10;20M"
    count = 50
    kr = _pipe_reader(event * count)
    results = []
    while (k := kr.read(0)) is not None:
        results.append(k)
    assert results == ["scroll-up"] * count


def test_reader_alt_keys():
    kr = _pipe_reader(b"\x1b\x7f\x1bb\x1bf")
    assert kr.read(0) == "delete-word"
    assert kr.read(0) == "word-left"
    assert kr.read(0) == "word-right"
    assert kr.read(0) is None


def test_reader_page_keys():
    kr = _pipe_reader(b"\x1b[5~\x1b[6~")
    assert kr.read(0) == "page-up"
    assert kr.read(0) == "page-down"
    assert kr.read(0) is None


def test_reader_modifier_arrows():
    kr = _pipe_reader(b"\x1b[1;3C\x1b[1;3D")
    assert kr.read(0) == "word-right"
    assert kr.read(0) == "word-left"
    assert kr.read(0) is None


def test_reader_bracketed_paste():
    kr = _pipe_reader(b"\x1b[200~hello world\x1b[201~x")
    result = kr.read(0)
    assert isinstance(result, Paste)
    assert result.text == "hello world"
    assert kr.read(0) == "x"


def test_reader_scroll_interleaved_with_arrows():
    """Realistic fast input: scroll events mixed with arrow keys."""
    kr = _pipe_reader(
        b"\x1b[<64;5;5M\x1b[A\x1b[<65;5;5M\x1b[B"
    )
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "up"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) == "down"
    assert kr.read(0) is None


# ── CSI boundary parsing (the core smooth-scroll fix) ─────────────


def test_csi_boundary_arrow_then_arrow():
    """Two CSI arrows in one buffer: each terminates at its letter byte."""
    kr = _pipe_reader(b"\x1b[A\x1b[B")
    assert kr.read(0) == "up"
    assert kr.read(0) == "down"
    assert kr.read(0) is None


def test_csi_boundary_page_then_arrow():
    """Page-up (multi-byte CSI) followed by arrow (single-byte CSI)."""
    kr = _pipe_reader(b"\x1b[5~\x1b[C")
    assert kr.read(0) == "page-up"
    assert kr.read(0) == "right"
    assert kr.read(0) is None


def test_csi_boundary_mouse_then_page():
    """SGR mouse (variable-length CSI) followed by page-down."""
    kr = _pipe_reader(b"\x1b[<64;999;999M\x1b[6~")
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "page-down"
    assert kr.read(0) is None


def test_csi_boundary_modifier_then_mouse():
    """Modifier arrow followed by mouse scroll."""
    kr = _pipe_reader(b"\x1b[1;3C\x1b[<65;1;1M")
    assert kr.read(0) == "word-right"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) is None


def test_csi_boundary_many_mixed_sequences():
    """Stress test: many different CSI types back-to-back."""
    data = (
        b"\x1b[A"          # up
        b"\x1b[<64;1;1M"   # scroll-up
        b"\x1b[5~"         # page-up
        b"\x1b[1;3D"       # word-left
        b"\x1b[B"          # down
        b"\x1b[<65;1;1M"   # scroll-down
        b"\x1b[3~"         # delete
        b"\x1b[H"          # home
    )
    kr = _pipe_reader(data)
    assert kr.read(0) == "up"
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "page-up"
    assert kr.read(0) == "word-left"
    assert kr.read(0) == "down"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) == "delete"
    assert kr.read(0) == "home"
    assert kr.read(0) is None


def test_csi_boundary_mouse_large_coordinates():
    """Mouse events with large coordinates still parse correctly."""
    kr = _pipe_reader(b"\x1b[<64;1234;5678M\x1b[<65;9999;9999M")
    assert kr.read(0) == "scroll-up"
    assert kr.read(0) == "scroll-down"
    assert kr.read(0) is None


# ── Double-escape sequences ────────────────────────────────────────


def test_double_escape_option_arrows():
    """Double-escape Option+arrow on some terminals."""
    kr = _pipe_reader(b"\x1b\x1b[C\x1b\x1b[D")
    assert kr.read(0) == "word-right"
    assert kr.read(0) == "word-left"
    assert kr.read(0) is None


def test_double_escape_followed_by_normal():
    """Double-escape followed by a regular key."""
    kr = _pipe_reader(b"\x1b\x1b[Cx")
    assert kr.read(0) == "word-right"
    assert kr.read(0) == "x"
    assert kr.read(0) is None


# ── Bare escape ────────────────────────────────────────────────────


def test_bare_escape():
    """Lone escape byte with nothing following should return 'esc'."""
    kr = _pipe_reader(b"\x1b")
    assert kr.read(0) == "esc"


# ── Paste followed by more input ──────────────────────────────────


def test_paste_with_newlines():
    kr = _pipe_reader(b"\x1b[200~line1\rline2\x1b[201~")
    result = kr.read(0)
    assert isinstance(result, Paste)
    assert result.text == "line1\nline2"


def test_paste_then_csi_then_char():
    """Paste, arrow key, and char in one buffer."""
    kr = _pipe_reader(b"\x1b[200~hi\x1b[201~\x1b[Az")
    result = kr.read(0)
    assert isinstance(result, Paste)
    assert result.text == "hi"
    assert kr.read(0) == "up"
    assert kr.read(0) == "z"
    assert kr.read(0) is None
