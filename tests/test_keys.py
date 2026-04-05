"""Tests for key parsing — pure functions, no TTY needed."""

from terminal.keys import parse_csi, parse_sgr_mouse

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
