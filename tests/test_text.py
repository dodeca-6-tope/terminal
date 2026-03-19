from terminal import Text


class TestLen:
    def test_should_return_length_of_plain_string(self):
        assert len(Text("hello")) == 5

    def test_should_ignore_ansi_escape_codes(self):
        assert len(Text("\033[1mhello\033[0m")) == 5

    def test_should_return_zero_for_empty_string(self):
        assert len(Text("")) == 0

    def test_should_count_wide_characters_as_two(self):
        assert len(Text("日本")) == 4


class TestTruncate:
    def test_should_not_truncate_when_within_limit(self):
        t = Text("short")
        assert str(t.truncate(10)) == "short"

    def test_should_truncate_with_ellipsis(self):
        t = Text("hello world")
        assert str(t.truncate(8)) == "hello w…"

    def test_should_strip_ansi_before_truncating(self):
        t = Text("\033[1mhello world\033[0m")
        result = t.truncate(8)
        assert str(result) == "hello w…"
        assert len(result) == 8

    def test_should_return_same_instance_when_not_needed(self):
        t = Text("hi")
        assert t.truncate(10) is t


class TestPad:
    def test_should_right_pad_by_default(self):
        t = Text("hi")
        assert str(t.pad(5)) == "hi   "

    def test_should_left_pad_with_right_align(self):
        t = Text("hi")
        assert str(t.pad(5, align="right")) == "   hi"

    def test_should_not_pad_when_already_wide_enough(self):
        t = Text("hello")
        assert t.pad(3) is t

    def test_should_account_for_ansi_codes(self):
        t = Text("\033[1mhi\033[0m")
        padded = t.pad(5)
        assert len(padded) == 5
        assert str(padded) == "\033[1mhi\033[0m   "


class TestChaining:
    def test_should_chain_truncate_then_pad(self):
        t = Text("a very long name here")
        result = t.truncate(10).pad(15)
        assert len(result) == 15
        assert str(result) == "a very lo…     "


class TestConcat:
    def test_should_concatenate_two_texts(self):
        a = Text("hello")
        b = Text(" world")
        result = a + b
        assert str(result) == "hello world"
        assert len(result) == 11

    def test_should_concatenate_with_plain_string(self):
        t = Text("hello")
        result = t + " world"
        assert str(result) == "hello world"

    def test_should_support_radd(self):
        t = Text("world")
        result = "hello " + t
        assert str(result) == "hello world"


class TestStr:
    def test_should_preserve_ansi_codes(self):
        raw = "\033[32mgreen\033[0m"
        assert str(Text(raw)) == raw

    def test_should_work_in_fstrings(self):
        t = Text("hi").pad(5)
        assert f"[{t}]" == "[hi   ]"
