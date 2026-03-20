"""Tests for Flex."""

from terminal import Flex, Text

# ── Basic flow ───────────────────────────────────────────────────────

def test_wrap_single_chunk():
    assert Flex.wrap(["hello"], 80) == ["hello"]

def test_wrap_all_fit_one_line():
    result = Flex.wrap(["[⏎] select", "[esc] back"], 40)
    assert result == ["[⏎] select [esc] back"]

def test_wrap_wraps_to_multiple_lines():
    result = Flex.wrap(["[⏎] select", "[esc] back"], 15)
    assert result == ["[⏎] select", "[esc] back"]

def test_wrap_empty():
    assert Flex.wrap([], 80) == []

def test_wrap_many_chunks():
    chunks = ["[a] one", "[b] two", "[c] three", "[d] four"]
    result = Flex.wrap(chunks, 24)
    assert result == ["[a] one [b] two", "[c] three [d] four"]

def test_wrap_exact_fit():
    # "aaa bbb" = 7 chars
    result = Flex.wrap(["aaa", "bbb"], 7)
    assert result == ["aaa bbb"]

def test_wrap_one_char_over():
    # "aaa bbb" = 7 chars, width=6 should wrap
    result = Flex.wrap(["aaa", "bbb"], 6)
    assert result == ["aaa", "bbb"]

def test_wrap_chunk_wider_than_width():
    result = Flex.wrap(["very long chunk"], 5)
    assert result == ["very long chunk"]


# ── Custom separator ────────────────────────────────────────────────

def test_wrap_custom_sep():
    result = Flex.wrap(["a", "b", "c"], 20, sep="  ")
    assert result == ["a  b  c"]

def test_wrap_custom_sep_wraps():
    result = Flex.wrap(["aaa", "bbb"], 8, sep=" | ")
    assert result == ["aaa", "bbb"]

def test_wrap_custom_sep_fits():
    result = Flex.wrap(["aaa", "bbb"], 9, sep=" | ")
    assert result == ["aaa | bbb"]


# ── With Text objects ────────────────────────────────────────────────

def test_wrap_with_text_objects():
    chunks = [Text("hello"), Text("world")]
    result = Flex.wrap(chunks, 40)
    assert result == ["hello world"]

def test_wrap_with_ansi_text():
    green = "\033[32m"
    rst = "\033[0m"
    chunks = [Text(f"{green}[⏎]{rst} select"), "[esc] back"]
    result = Flex.wrap(chunks, 25)
    assert len(result) == 1
    assert green in result[0]

def test_wrap_ansi_text_wraps_by_visible_width():
    green = "\033[32m"
    rst = "\033[0m"
    chunks = [Text(f"{green}[⏎]{rst} select"), "[esc] back"]
    result = Flex.wrap(chunks, 15)
    assert len(result) == 2

def test_wrap_mixed_text_and_str():
    chunks = [Text("one"), "two", Text("three")]
    result = Flex.wrap(chunks, 20)
    assert result == ["one two three"]
