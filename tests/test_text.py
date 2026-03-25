from terminal import Text


class TestLen:
    def test_display_width(self):
        assert len(Text("hello")) == 5
        assert len(Text("\033[1mhello\033[0m")) == 5
        assert len(Text("")) == 0
        assert len(Text("日本")) == 4


class TestTruncate:
    def test_truncate(self):
        assert str(Text("short").truncate(10)) == "short"
        assert str(Text("hello world").truncate(8)) == "hello w…"
        t = Text("hi")
        assert t.truncate(10) is t

    def test_should_strip_ansi_before_truncating(self):
        result = Text("\033[1mhello world\033[0m").truncate(8)
        assert str(result) == "hello w…"
        assert len(result) == 8


class TestPad:
    def test_pad(self):
        assert str(Text("hi").pad(5)) == "hi   "
        assert str(Text("hi").pad(5, align="right")) == "   hi"
        t = Text("hello")
        assert t.pad(3) is t

    def test_should_account_for_ansi_codes(self):
        padded = Text("\033[1mhi\033[0m").pad(5)
        assert len(padded) == 5
        assert str(padded) == "\033[1mhi\033[0m   "


class TestConcatAndChaining:
    def test_chaining(self):
        result = Text("a very long name here").truncate(10).pad(15)
        assert len(result) == 15
        assert str(result) == "a very lo…     "

    def test_concatenation(self):
        result = Text("hello") + Text(" world")
        assert str(result) == "hello world"
        assert len(result) == 11
        assert str(Text("hello") + " world") == "hello world"
        assert str("hello " + Text("world")) == "hello world"


class TestStr:
    def test_str_representation(self):
        raw = "\033[32mgreen\033[0m"
        assert str(Text(raw)) == raw
        assert f"[{Text('hi').pad(5)}]" == "[hi   ]"
