"""Tests for TextInput."""

from terminal import TextInput, Paste


# ── Basic typing ─────────────────────────────────────────────────────

def test_empty_initial():
    ti = TextInput()
    assert ti.value == ""
    assert ti.cursor == 0

def test_initial_value():
    ti = TextInput("hello")
    assert ti.value == "hello"
    assert ti.cursor == 5

def test_type_characters():
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key("b")
    ti.handle_key("c")
    assert ti.value == "abc"
    assert ti.cursor == 3

def test_type_space():
    ti = TextInput("ab")
    ti.handle_key("space")
    ti.handle_key("c")
    assert ti.value == "ab c"


# ── Cursor navigation ───────────────────────────────────────────────

def test_left_right():
    ti = TextInput("abc")
    ti.handle_key("left")
    assert ti.cursor == 2
    ti.handle_key("left")
    assert ti.cursor == 1
    ti.handle_key("right")
    assert ti.cursor == 2

def test_left_at_start():
    ti = TextInput("abc")
    ti.cursor = 0
    ti.handle_key("left")
    assert ti.cursor == 0

def test_right_at_end():
    ti = TextInput("abc")
    ti.handle_key("right")
    assert ti.cursor == 3

def test_home_end():
    ti = TextInput("hello world")
    ti.handle_key("home")
    assert ti.cursor == 0
    ti.handle_key("end")
    assert ti.cursor == 11

def test_word_left():
    # "hello world foo" — cursor starts at 15 (end)
    ti = TextInput("hello world foo")
    ti.handle_key("word-left")
    assert ti.cursor == 12  # on 'f' of "foo"
    ti.handle_key("word-left")
    assert ti.cursor == 6   # on 'w' of "world"
    ti.handle_key("word-left")
    assert ti.cursor == 0   # on 'h' of "hello"
    ti.handle_key("word-left")
    assert ti.cursor == 0   # stays at start

def test_word_right():
    # "hello world foo" — cursor starts at 0
    ti = TextInput("hello world foo")
    ti.cursor = 0
    ti.handle_key("word-right")
    assert ti.cursor == 6   # on 'w' of "world"
    ti.handle_key("word-right")
    assert ti.cursor == 12  # on 'f' of "foo"
    ti.handle_key("word-right")
    assert ti.cursor == 15  # end
    ti.handle_key("word-right")
    assert ti.cursor == 15  # stays at end


# ── Backspace ────────────────────────────────────────────────────────

def test_backspace():
    ti = TextInput("abc")
    ti.handle_key("backspace")
    assert ti.value == "ab"
    assert ti.cursor == 2

def test_backspace_at_start():
    ti = TextInput("abc")
    ti.cursor = 0
    ti.handle_key("backspace")
    assert ti.value == "abc"
    assert ti.cursor == 0

def test_backspace_middle():
    ti = TextInput("abc")
    ti.cursor = 2
    ti.handle_key("backspace")
    assert ti.value == "ac"
    assert ti.cursor == 1


# ── Clear line / delete word ─────────────────────────────────────────

def test_clear_line():
    ti = TextInput("hello world")
    ti.cursor = 6
    ti.handle_key("clear-line")
    assert ti.value == "world"
    assert ti.cursor == 0

def test_delete_word():
    ti = TextInput("hello world")
    ti.handle_key("delete-word")
    assert ti.value == "hello "
    assert ti.cursor == 6

def test_delete_word_at_start():
    ti = TextInput("hello")
    ti.cursor = 0
    ti.handle_key("delete-word")
    assert ti.value == "hello"
    assert ti.cursor == 0


# ── Insert in middle ────────────────────────────────────────────────

def test_insert_middle():
    ti = TextInput("ac")
    ti.cursor = 1
    ti.handle_key("b")
    assert ti.value == "abc"
    assert ti.cursor == 2


# ── Paste ────────────────────────────────────────────────────────────

def test_paste():
    ti = TextInput()
    ti.handle_key(Paste("hello world this is a long prompt"))
    assert ti.value == "hello world this is a long prompt"
    assert ti.cursor == 33

def test_paste_display_shows_placeholder():
    ti = TextInput()
    ti.handle_key(Paste("hello world this is pasted text"))
    display = ti.display()
    assert "[Pasted +" in display
    assert "hello world" not in display

def test_paste_backspace_deletes_whole_paste():
    ti = TextInput()
    ti.handle_key(Paste("some long pasted text here"))
    assert ti.value == "some long pasted text here"
    ti.handle_key("backspace")
    assert ti.value == ""
    assert ti.cursor == 0

def test_paste_then_type_then_backspace():
    ti = TextInput()
    ti.handle_key(Paste("pasted text"))  # paste
    ti.handle_key("x")  # type
    assert ti.value == "pasted textx"
    ti.handle_key("backspace")  # deletes 'x'
    assert ti.value == "pasted text"
    ti.handle_key("backspace")  # deletes entire paste
    assert ti.value == ""

def test_paste_with_newlines_converted_to_spaces():
    ti = TextInput()
    ti.handle_key(Paste("line one\nline two\tline three"))
    assert ti.value == "line one line two line three"

def test_type_then_paste():
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key("b")
    ti.handle_key(Paste("pasted stuff"))
    assert ti.value == "abpasted stuff"
    ti.handle_key("backspace")  # deletes paste
    assert ti.value == "ab"

def test_paste_in_middle():
    ti = TextInput("ac")
    ti.cursor = 1
    ti.handle_key(Paste("pasted text"))  # paste between a and c
    assert ti.value == "apasted textc"
    assert ti.cursor == 12

def test_paste_in_middle_backspace():
    ti = TextInput("ac")
    ti.cursor = 1
    ti.handle_key(Paste("pasted text"))
    assert ti.value == "apasted textc"
    # cursor is at 12, which is end of paste
    ti.handle_key("backspace")
    assert ti.value == "ac"
    assert ti.cursor == 1

def test_multiple_pastes():
    ti = TextInput()
    ti.handle_key(Paste("first paste"))
    ti.handle_key(" ")
    ti.handle_key(Paste("second paste"))
    assert ti.value == "first paste second paste"
    ti.handle_key("backspace")  # deletes second paste
    assert ti.value == "first paste "
    ti.handle_key("backspace")  # deletes space
    assert ti.value == "first paste"
    ti.handle_key("backspace")  # deletes first paste
    assert ti.value == ""

def test_display_no_paste():
    ti = TextInput("abc")
    display = ti.display()
    assert display == f"abc{ti.CURSOR_ON} {ti.CURSOR_OFF}"  # cursor at end

def test_display_cursor_middle():
    ti = TextInput("abc")
    ti.cursor = 1
    display = ti.display()
    assert display == f"a{ti.CURSOR_ON}b{ti.CURSOR_OFF}c"  # cursor ON 'b'

def test_display_cursor_start():
    ti = TextInput("abc")
    ti.cursor = 0
    display = ti.display()
    assert display == f"{ti.CURSOR_ON}a{ti.CURSOR_OFF}bc"  # cursor ON 'a'


# ── Unknown keys ─────────────────────────────────────────────────────

def test_unknown_key_returns_false():
    ti = TextInput()
    assert ti.handle_key("up") is False
    assert ti.handle_key("down") is False
    assert ti.handle_key("tab") is False


# ── Word navigation with paste ──────────────────────────────────────

def test_type_at_paste_start():
    """Typing at start of paste inserts before it."""
    ti = TextInput()
    ti.handle_key(Paste("hello world pasted"))
    ti.handle_key("home")
    assert ti.cursor == 0
    ti.handle_key("x")
    assert ti.value == "xhello world pasted"
    assert ti.cursor == 1
    assert ti._pastes == [(1, 19)]

def test_paste_at_cursor_between_typed_text():
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key("b")
    ti.cursor = 1  # between a and b
    ti.handle_key(Paste("pasted text here"))
    assert ti.value == "apasted text hereb"
    assert ti.cursor == 17
    # backspace should delete the paste
    ti.handle_key("backspace")
    assert ti.value == "ab"
    assert ti.cursor == 1

def test_backspace_at_paste_start_deletes_whole_paste():
    """word-left to paste start, then backspace — should delete entire paste."""
    ti = TextInput()
    text = "hello world pasted text here"
    ti.handle_key(Paste(text))
    # word-left skips entire paste now
    ti.handle_key("word-left")
    assert ti.cursor == 0  # paste starts at 0, skips to start
    # backspace at start does nothing
    ti.handle_key("backspace")
    assert ti.value == text

def test_backspace_right_after_paste():
    """Cursor right at end of paste, backspace deletes it."""
    ti = TextInput()
    ti.handle_key(Paste("hello world here"))
    assert ti.cursor == 16
    ti.handle_key("backspace")
    assert ti.value == ""
    assert ti._pastes == []


def test_delete_word_after_paste_does_not_eat_paste():
    """option+backspace one space after a paste should only delete the space."""
    ti = TextInput()
    ti.handle_key(Paste("hello world pasted"))
    ti.handle_key("space")
    ti.handle_key("x")
    # value: "hello world pasted x", paste at (0, 18), typed " x" at 18-20
    assert ti.value == "hello world pasted x"
    assert ti.cursor == 20
    ti.handle_key("delete-word")
    # Should delete "x" but NOT eat into the paste
    assert ti.value == "hello world pasted "
    assert ti.cursor == 19
    ti.handle_key("delete-word")
    # Should delete the space, stop at paste boundary
    assert ti.value == "hello world pasted"
    assert ti.cursor == 18
    # Paste should still be intact
    assert ti._pastes == [(0, 18)]


def test_delete_word_at_paste_end():
    """delete-word at end of paste deletes entire paste."""
    ti = TextInput()
    ti.handle_key(Paste("hello world pasted"))
    # cursor at end of paste
    ti.handle_key("delete-word")
    assert ti.value == ""
    assert ti._pastes == []


def test_type_after_paste_via_word_nav():
    """word-left jumps to paste start, typing inserts before paste."""
    ti = TextInput()
    text = "hello world pasted text here"
    ti.handle_key(Paste(text))
    # word-left skips entire paste
    ti.handle_key("word-left")
    assert ti.cursor == 0
    ti.handle_key("x")
    assert ti.value == "x" + text
    assert ti.cursor == 1


# ── Arrow navigation with paste ──────────────────────────────────────

def test_left_arrow_skips_paste():
    """Left arrow at end of paste should jump to start of paste."""
    ti = TextInput("ab")
    ti.cursor = 2
    ti.handle_key(Paste("cd hello world"))  # paste at (2, 16)
    ti.handle_key("e")
    ti.handle_key("f")
    # value: "abcd hello worldef", paste at (2, 16)
    assert ti.cursor == 18
    ti.handle_key("left")  # f→e
    assert ti.cursor == 17
    ti.handle_key("left")  # e→end of paste
    assert ti.cursor == 16
    ti.handle_key("left")  # should skip paste, land at 2
    assert ti.cursor == 2
    ti.handle_key("left")  # b
    assert ti.cursor == 1

def test_right_arrow_skips_paste():
    """Right arrow at start of paste should jump to end of paste."""
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key(Paste("hello world pasted"))  # paste at (1, 19)
    ti.handle_key("b")
    # value: "ahello world pastedb"
    assert ti.value == "ahello world pastedb"
    ti.cursor = 0
    ti.handle_key("right")  # a→start of paste
    assert ti.cursor == 1
    ti.handle_key("right")  # should skip paste, land at 19
    assert ti.cursor == 19
    ti.handle_key("right")  # b
    assert ti.cursor == 20

def test_word_left_skips_paste():
    """option+left should treat paste as one unit."""
    ti = TextInput()
    ti.handle_key("h")
    ti.handle_key("e")
    ti.handle_key("l")
    ti.handle_key("l")
    ti.handle_key("o")
    ti.handle_key("space")
    ti.handle_key(Paste("big pasted block"))  # paste at (6, 22)
    ti.handle_key("space")
    ti.handle_key("w")
    ti.handle_key("o")
    ti.handle_key("r")
    ti.handle_key("l")
    ti.handle_key("d")
    # value: "hello big pasted block world", paste at (6, 22)
    assert ti.value == "hello big pasted block world"
    assert ti.cursor == 28
    ti.handle_key("word-left")  # on 'w' of "world"
    assert ti.cursor == 23
    ti.handle_key("word-left")  # skips paste → on start of paste (6)
    assert ti.cursor == 6
    ti.handle_key("word-left")  # on 'h' of "hello"
    assert ti.cursor == 0

def test_word_right_skips_paste():
    """option+right should treat paste as one unit."""
    ti = TextInput()
    ti.handle_key("h")
    ti.handle_key("i")
    ti.handle_key("space")
    ti.handle_key(Paste("pasted content here"))  # paste at (3, 22)
    ti.handle_key("space")
    ti.handle_key("b")
    ti.handle_key("y")
    ti.handle_key("e")
    # value: "hi pasted content here bye"
    assert ti.value == "hi pasted content here bye"
    ti.cursor = 0
    ti.handle_key("word-right")  # on 'p' of paste (start of next word)
    assert ti.cursor == 3
    ti.handle_key("word-right")  # skips paste → on 'b' of "bye"
    assert ti.cursor == 23
    ti.handle_key("word-right")  # end
    assert ti.cursor == 26

def test_left_right_no_paste():
    """Normal left/right should work as before without pastes."""
    ti = TextInput("abc")
    ti.handle_key("left")
    assert ti.cursor == 2
    ti.handle_key("right")
    assert ti.cursor == 3

def test_word_nav_with_paste():
    ti = TextInput("before ")
    ti.handle_key(Paste("pasted words here"))
    ti.handle_key(" ")
    ti.handle_key("a")
    ti.handle_key("f")
    ti.handle_key("t")
    ti.handle_key("e")
    ti.handle_key("r")
    # value: "before pasted words here after"
    assert ti.value == "before pasted words here after"
    ti.handle_key("word-left")
    assert ti.cursor == 25  # on 'a' of "after"
    ti.handle_key("word-left")
    assert ti.cursor == 7   # on start of paste
