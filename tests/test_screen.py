"""Tests for Screen rendering — clip, diff, full render."""

from terminal.screen import clip, render_diff, render_full

# ── clip ────────────────────────────────────────────────────────────


def test_clip_leaves_short_text():
    assert clip("hello", 10) == "hello"


def test_clip_truncates_at_width():
    result = clip("hello world", 5)
    # Should contain exactly 5 visible chars + ANSI reset
    assert "hello" in result
    assert "world" not in result


def test_clip_preserves_ansi_before_cutoff():
    result = clip("\033[1mhello world\033[0m", 5)
    assert "\033[1m" in result
    assert "hello" in result
    assert "world" not in result


def test_clip_ansi_codes_dont_consume_width():
    """A line with ANSI codes that fits visually should not be clipped."""
    line = "\033[31mhi\033[0m"  # 2 visible chars
    assert clip(line, 2) == line
    assert clip(line, 10) == line


def test_clip_wide_chars():
    result = clip("你好世界", 4)
    assert "你好" in result
    assert "世界" not in result


def test_pad_wide_chars():
    from terminal.screen import pad

    assert pad("你好", 6) == "你好  "  # 4 cols + 2 spaces


# ── render_full ────────────────────────────────────────────────────


def test_full_render_starts_at_home():
    result = render_full(["a", "b"])
    assert result.startswith("\033[H")


def test_full_render_joins_lines():
    result = render_full(["a", "b", "c"])
    assert "a\nb\nc" in result


def test_full_render_contains_all_content():
    result = render_full(["hello", "world"])
    assert "hello" in result
    assert "world" in result


# ── render_diff ────────────────────────────────────────────────────


def test_diff_skips_unchanged_lines():
    result = render_diff(["same", "same"], ["same", "same"])
    assert result == ""


def test_diff_updates_only_changed_lines():
    result = render_diff(["same", "new"], ["same", "old"])
    assert "same" not in result
    assert "new" in result


def test_diff_updates_line_that_became_empty():
    result = render_diff(["hello", ""], ["hello", "world"])
    assert "world" not in result
    assert "\033[2;1H" in result  # cursor moved to write empty line


def test_diff_adds_new_lines_beyond_previous():
    result = render_diff(["a", "b", "c"], ["a", "b"])
    assert "c" in result
    assert "a" not in result


# ── _pad ──────────────────────────────────────────────────────────────


def test_pad_short_line():
    from terminal.screen import pad

    assert pad("hi", 5) == "hi   "


def test_pad_full_width_line():
    from terminal.screen import pad

    assert pad("hello", 5) == "hello"


def test_pad_with_ansi():
    from terminal.screen import pad

    line = "\033[1mhi\033[0m"
    padded = pad(line, 5)
    assert padded == line + "   "


def test_render_full_no_erase_codes():
    """Full render uses padding, not \\033[K], to clear line remainders."""
    result = render_full(["hello", "world"])
    assert "\033[K" not in result


def test_render_diff_no_erase_codes():
    """Diff render uses padding, not \\033[K], to clear line remainders."""
    result = render_diff(["new"], ["old"])
    assert "\033[K" not in result


# ── clip edge cases ──────────────────────────────────────────────────


def test_clip_wide_chars_with_ansi():
    """Wide chars inside ANSI styling should still clip at the right column."""
    line = "\033[31m你好世界\033[0m"
    result = clip(line, 4)
    assert "你好" in result
    assert "世界" not in result


def test_clip_exact_width():
    assert clip("hello", 5) == "hello"


def test_clip_zero_width():
    from terminal.measure import display_width, strip_ansi

    assert clip("hello", 0) == ""
    # ANSI-styled content should include reset
    result = clip("\033[1mhello\033[0m", 0)
    assert "\033[0m" in result
    assert display_width(strip_ansi(result)) == 0
