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

def test_type_single_char_returns_true():
    ti = TextInput()
    assert ti.handle_key("x") is True

def test_type_preserves_existing_text():
    ti = TextInput("hello")
    ti.cursor = 5
    ti.handle_key("!")
    assert ti.value == "hello!"

def test_type_unicode():
    ti = TextInput()
    ti.handle_key("é")
    ti.handle_key("ñ")
    assert ti.value == "éñ"
    assert ti.cursor == 2

def test_non_printable_returns_false():
    ti = TextInput()
    assert ti.handle_key("\x01") is False
    assert ti.value == ""


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

def test_home_on_empty():
    ti = TextInput()
    ti.handle_key("home")
    assert ti.cursor == 0

def test_end_on_empty():
    ti = TextInput()
    ti.handle_key("end")
    assert ti.cursor == 0

def test_word_left():
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

def test_word_left_single_word():
    ti = TextInput("hello")
    ti.handle_key("word-left")
    assert ti.cursor == 0

def test_word_right_single_word():
    ti = TextInput("hello")
    ti.cursor = 0
    ti.handle_key("word-right")
    assert ti.cursor == 5

def test_word_left_multiple_spaces():
    ti = TextInput("hello   world")
    ti.handle_key("word-left")
    assert ti.cursor == 8   # on 'w' of "world"
    ti.handle_key("word-left")
    assert ti.cursor == 0

def test_word_right_multiple_spaces():
    ti = TextInput("hello   world")
    ti.cursor = 0
    ti.handle_key("word-right")
    assert ti.cursor == 8   # on 'w' of "world"

def test_word_left_from_middle_of_word():
    ti = TextInput("hello world")
    ti.cursor = 8  # on 'r' of "world"
    ti.handle_key("word-left")
    assert ti.cursor == 6   # on 'w' of "world"

def test_word_right_from_middle_of_word():
    ti = TextInput("hello world")
    ti.cursor = 2  # on 'l' of "hello"
    ti.handle_key("word-right")
    assert ti.cursor == 6   # on 'w' of "world"


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

def test_backspace_all():
    ti = TextInput("ab")
    ti.handle_key("backspace")
    ti.handle_key("backspace")
    assert ti.value == ""
    assert ti.cursor == 0

def test_backspace_empty():
    ti = TextInput()
    ti.handle_key("backspace")
    assert ti.value == ""
    assert ti.cursor == 0


# ── Clear line / delete word ─────────────────────────────────────────

def test_clear_line():
    ti = TextInput("hello world")
    ti.cursor = 6
    ti.handle_key("clear-line")
    assert ti.value == "world"
    assert ti.cursor == 0

def test_clear_line_at_start():
    ti = TextInput("hello")
    ti.cursor = 0
    ti.handle_key("clear-line")
    assert ti.value == "hello"
    assert ti.cursor == 0

def test_clear_line_at_end():
    ti = TextInput("hello")
    ti.handle_key("clear-line")
    assert ti.value == ""
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

def test_delete_word_single_word():
    ti = TextInput("hello")
    ti.handle_key("delete-word")
    assert ti.value == ""
    assert ti.cursor == 0

def test_delete_word_with_trailing_spaces():
    ti = TextInput("hello   ")
    ti.handle_key("delete-word")
    assert ti.value == ""
    assert ti.cursor == 0

def test_delete_word_multiple_times():
    ti = TextInput("one two three")
    ti.handle_key("delete-word")
    assert ti.value == "one two "
    ti.handle_key("delete-word")
    assert ti.value == "one "
    ti.handle_key("delete-word")
    assert ti.value == ""


# ── Insert in middle ────────────────────────────────────────────────

def test_insert_middle():
    ti = TextInput("ac")
    ti.cursor = 1
    ti.handle_key("b")
    assert ti.value == "abc"
    assert ti.cursor == 2

def test_insert_at_start():
    ti = TextInput("bc")
    ti.cursor = 0
    ti.handle_key("a")
    assert ti.value == "abc"
    assert ti.cursor == 1

def test_insert_space_middle():
    ti = TextInput("helloworld")
    ti.cursor = 5
    ti.handle_key("space")
    assert ti.value == "hello world"
    assert ti.cursor == 6


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
    ti.handle_key(Paste("pasted text"))
    ti.handle_key("x")
    assert ti.value == "pasted textx"
    ti.handle_key("backspace")  # deletes 'x'
    assert ti.value == "pasted text"
    ti.handle_key("backspace")  # deletes entire paste
    assert ti.value == ""

def test_paste_with_newlines_converted_to_spaces():
    ti = TextInput()
    ti.handle_key(Paste("line one\nline two\tline three"))
    assert ti.value == "line one line two line three"

def test_paste_with_carriage_returns():
    ti = TextInput()
    ti.handle_key(Paste("line one\r\nline two"))
    assert ti.value == "line one line two"

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
    ti.handle_key(Paste("pasted text"))
    assert ti.value == "apasted textc"
    assert ti.cursor == 12

def test_paste_in_middle_backspace():
    ti = TextInput("ac")
    ti.cursor = 1
    ti.handle_key(Paste("pasted text"))
    assert ti.value == "apasted textc"
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

def test_paste_empty_string():
    ti = TextInput("hello")
    ti.handle_key(Paste(""))
    assert ti.value == "hello"
    assert ti.cursor == 5

def test_paste_single_char():
    """Single char paste is still tracked as paste."""
    ti = TextInput()
    ti.handle_key(Paste("x"))
    assert ti.value == "x"
    assert len(ti._pastes) == 1

def test_paste_preserves_value_after_clear():
    ti = TextInput()
    ti.handle_key(Paste("pasted"))
    ti.handle_key("clear-line")
    assert ti.value == ""
    assert ti._pastes == []


# ── Display ──────────────────────────────────────────────────────────

def test_display_no_paste():
    ti = TextInput("abc")
    display = ti.display()
    assert display == f"abc{ti.CURSOR_ON} {ti.CURSOR_OFF}"

def test_display_cursor_middle():
    ti = TextInput("abc")
    ti.cursor = 1
    display = ti.display()
    assert display == f"a{ti.CURSOR_ON}b{ti.CURSOR_OFF}c"

def test_display_cursor_start():
    ti = TextInput("abc")
    ti.cursor = 0
    display = ti.display()
    assert display == f"{ti.CURSOR_ON}a{ti.CURSOR_OFF}bc"

def test_display_empty():
    ti = TextInput()
    display = ti.display()
    assert display == f"{ti.CURSOR_ON} {ti.CURSOR_OFF}"

def test_display_paste_placeholder_length():
    ti = TextInput()
    ti.handle_key(Paste("x" * 100))
    display = ti.display()
    assert "[Pasted +100 chars]" in display
    assert len(display) < 100  # much shorter than raw value

def test_display_typed_around_paste():
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key("b")
    ti.handle_key(Paste("long pasted content"))
    ti.handle_key("c")
    display = ti.display()
    assert display.startswith("ab")
    assert "[Pasted +" in display
    # cursor is at end, on the trailing space
    assert ti.CURSOR_ON in display


# ── Unknown keys ─────────────────────────────────────────────────────

def test_unknown_key_returns_false():
    ti = TextInput()
    assert ti.handle_key("up") is False
    assert ti.handle_key("down") is False
    assert ti.handle_key("tab") is False
    assert ti.handle_key("esc") is False
    assert ti.handle_key("enter") is False
    assert ti.handle_key("ctrl-r") is False
    assert ti.handle_key("focus") is False
    assert ti.handle_key("shift-tab") is False

def test_unknown_key_doesnt_modify_value():
    ti = TextInput("hello")
    ti.handle_key("up")
    ti.handle_key("down")
    ti.handle_key("tab")
    assert ti.value == "hello"
    assert ti.cursor == 5


# ── Paste navigation ────────────────────────────────────────────────

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
    ti.cursor = 1
    ti.handle_key(Paste("pasted text here"))
    assert ti.value == "apasted text hereb"
    assert ti.cursor == 17
    ti.handle_key("backspace")
    assert ti.value == "ab"
    assert ti.cursor == 1

def test_backspace_at_paste_start():
    """word-left to paste start, then backspace — does nothing."""
    ti = TextInput()
    text = "hello world pasted text here"
    ti.handle_key(Paste(text))
    ti.handle_key("word-left")
    assert ti.cursor == 0
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
    assert ti.value == "hello world pasted x"
    assert ti.cursor == 20
    ti.handle_key("delete-word")
    assert ti.value == "hello world pasted "
    assert ti.cursor == 19
    ti.handle_key("delete-word")
    assert ti.value == "hello world pasted"
    assert ti.cursor == 18
    assert ti._pastes == [(0, 18)]

def test_delete_word_at_paste_end():
    """delete-word at end of paste deletes entire paste."""
    ti = TextInput()
    ti.handle_key(Paste("hello world pasted"))
    ti.handle_key("delete-word")
    assert ti.value == ""
    assert ti._pastes == []

def test_type_after_paste_via_word_nav():
    """word-left jumps to paste start, typing inserts before paste."""
    ti = TextInput()
    text = "hello world pasted text here"
    ti.handle_key(Paste(text))
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
    ti.handle_key(Paste("cd hello world"))
    ti.handle_key("e")
    ti.handle_key("f")
    assert ti.cursor == 18
    ti.handle_key("left")  # f→e
    assert ti.cursor == 17
    ti.handle_key("left")  # e→end of paste
    assert ti.cursor == 16
    ti.handle_key("left")  # skip paste → 2
    assert ti.cursor == 2
    ti.handle_key("left")  # b
    assert ti.cursor == 1

def test_right_arrow_skips_paste():
    """Right arrow at start of paste should jump to end of paste."""
    ti = TextInput()
    ti.handle_key("a")
    ti.handle_key(Paste("hello world pasted"))
    ti.handle_key("b")
    assert ti.value == "ahello world pastedb"
    ti.cursor = 0
    ti.handle_key("right")  # a
    assert ti.cursor == 1
    ti.handle_key("right")  # skip paste → 19
    assert ti.cursor == 19
    ti.handle_key("right")  # b
    assert ti.cursor == 20

def test_word_left_skips_paste():
    """option+left should treat paste as one unit."""
    ti = TextInput()
    for c in "hello":
        ti.handle_key(c)
    ti.handle_key("space")
    ti.handle_key(Paste("big pasted block"))
    ti.handle_key("space")
    for c in "world":
        ti.handle_key(c)
    assert ti.value == "hello big pasted block world"
    assert ti.cursor == 28
    ti.handle_key("word-left")  # on 'w' of "world"
    assert ti.cursor == 23
    ti.handle_key("word-left")  # skips paste → 6
    assert ti.cursor == 6
    ti.handle_key("word-left")  # on 'h' of "hello"
    assert ti.cursor == 0

def test_word_right_skips_paste():
    """option+right should treat paste as one unit."""
    ti = TextInput()
    for c in "hi":
        ti.handle_key(c)
    ti.handle_key("space")
    ti.handle_key(Paste("pasted content here"))
    ti.handle_key("space")
    for c in "bye":
        ti.handle_key(c)
    assert ti.value == "hi pasted content here bye"
    ti.cursor = 0
    ti.handle_key("word-right")  # start of paste
    assert ti.cursor == 3
    ti.handle_key("word-right")  # skip paste → 'b' of "bye"
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
    for c in "after":
        ti.handle_key(c)
    assert ti.value == "before pasted words here after"
    ti.handle_key("word-left")
    assert ti.cursor == 25  # on 'a' of "after"
    ti.handle_key("word-left")
    assert ti.cursor == 7   # on start of paste


# ── Edge cases ───────────────────────────────────────────────────────

def test_rapid_backspace_on_empty():
    ti = TextInput()
    for _ in range(10):
        ti.handle_key("backspace")
    assert ti.value == ""
    assert ti.cursor == 0

def test_cursor_never_negative():
    ti = TextInput("a")
    ti.cursor = 0
    ti.handle_key("left")
    ti.handle_key("word-left")
    ti.handle_key("home")
    assert ti.cursor == 0

def test_cursor_never_exceeds_length():
    ti = TextInput("abc")
    ti.handle_key("right")
    ti.handle_key("right")
    ti.handle_key("word-right")
    ti.handle_key("end")
    assert ti.cursor == 3

def test_paste_then_clear_line_then_type():
    ti = TextInput()
    ti.handle_key(Paste("big paste"))
    ti.handle_key("clear-line")
    ti.handle_key("a")
    assert ti.value == "a"
    assert ti._pastes == []

def test_multiple_operations_sequence():
    """Full editing sequence: type, paste, navigate, delete, type more."""
    ti = TextInput()
    for c in "hello":
        ti.handle_key(c)
    ti.handle_key("space")
    ti.handle_key(Paste("pasted world"))
    ti.handle_key("space")
    for c in "end":
        ti.handle_key(c)
    assert ti.value == "hello pasted world end"
    # Delete "end"
    ti.handle_key("delete-word")
    assert ti.value == "hello pasted world "
    # Delete space (stops at paste boundary)
    ti.handle_key("delete-word")
    assert ti.value == "hello pasted world"
    # Delete paste
    ti.handle_key("delete-word")
    assert ti.value == "hello "
    # Delete "hello "
    ti.handle_key("delete-word")
    assert ti.value == ""
