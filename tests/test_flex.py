"""Tests for Flex."""

from terminal import Flex, Text

# ── Basic flow ───────────────────────────────────────────────────────

def test_wrap_basic():
    assert Flex.wrap(["hello"], 80) == ["hello"]
    assert Flex.wrap(["[⏎] select", "[esc] back"], 40) == ["[⏎] select [esc] back"]
    assert Flex.wrap(["[⏎] select", "[esc] back"], 15) == ["[⏎] select", "[esc] back"]
    assert Flex.wrap([], 80) == []
    assert Flex.wrap(["very long chunk"], 5) == ["very long chunk"]

def test_wrap_many_chunks():
    chunks = ["[a] one", "[b] two", "[c] three", "[d] four"]
    assert Flex.wrap(chunks, 24) == ["[a] one [b] two", "[c] three [d] four"]

def test_wrap_boundary():
    assert Flex.wrap(["aaa", "bbb"], 7) == ["aaa bbb"]
    assert Flex.wrap(["aaa", "bbb"], 6) == ["aaa", "bbb"]


# ── Custom separator ────────────────────────────────────────────────

def test_wrap_custom_sep():
    assert Flex.wrap(["a", "b", "c"], 20, sep="  ") == ["a  b  c"]
    assert Flex.wrap(["aaa", "bbb"], 8, sep=" | ") == ["aaa", "bbb"]
    assert Flex.wrap(["aaa", "bbb"], 9, sep=" | ") == ["aaa | bbb"]


# ── With Text objects ────────────────────────────────────────────────

def test_wrap_with_text_objects():
    assert Flex.wrap([Text("hello"), Text("world")], 40) == ["hello world"]
    assert Flex.wrap([Text("one"), "two", Text("three")], 20) == ["one two three"]

def test_wrap_ansi_text():
    green, rst = "\033[32m", "\033[0m"
    chunks = [Text(f"{green}[⏎]{rst} select"), "[esc] back"]
    result = Flex.wrap(chunks, 25)
    assert len(result) == 1
    assert green in result[0]
    assert len(Flex.wrap(chunks, 15)) == 2
