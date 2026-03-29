from terminal import Choice, Picker


def _choices(*names: str) -> list[Choice]:
    return [Choice(name=n, value=n) for n in names]


class TestInit:
    def test_initial_state(self):
        p = Picker(_choices("alpha", "beta", "gamma"))
        v = p.view()
        assert v.filtered == 3
        assert len(v.items) == 3
        assert v.items[0].cursor is True
        assert v.items[1].cursor is False

    def test_should_start_with_no_selection(self):
        p = Picker(_choices("a", "b"), multiselect=True)
        v = p.view()
        assert all(not item.selected for item in v.items)


class TestNavigation:
    def test_cursor_movement(self):
        p = Picker(_choices("a", "b", "c"))
        p.handle_key("down")
        assert p.view().items[1].cursor is True
        p.handle_key("up")
        assert p.view().items[0].cursor is True

    def test_cursor_boundaries(self):
        p = Picker(_choices("a", "b"))
        p.handle_key("up")
        assert p.cursor == 0
        p.handle_key("down")
        p.handle_key("down")
        assert p.cursor == 1

    def test_should_scroll_when_cursor_exceeds_max_height(self):
        p = Picker(_choices("a", "b", "c", "d"), max_height=2)
        p.handle_key("down")
        p.handle_key("down")
        assert p.scroll == 1
        v = p.view()
        assert len(v.items) == 2
        assert v.items[1].cursor is True


class TestFuzzyFilter:
    def test_should_filter_by_typed_query(self):
        p = Picker(_choices("apple", "banana", "apricot"))
        p.handle_key("a")
        p.handle_key("p")
        v = p.view()
        assert v.filtered == 2
        names = [item.name for item in v.items]
        assert "apple" in names
        assert "apricot" in names
        assert "banana" not in names

    def test_should_be_case_insensitive(self):
        p = Picker(_choices("Alpha", "beta"))
        p.handle_key("A")
        p.handle_key("l")
        v = p.view()
        assert v.filtered == 1
        assert v.items[0].name == "Alpha"

    def test_should_show_all_when_query_cleared(self):
        p = Picker(_choices("a", "b"))
        p.handle_key("x")
        p.handle_key("backspace")
        v = p.view()
        assert v.filtered == 2

    def test_should_clamp_cursor_when_filter_shrinks(self):
        p = Picker(_choices("apple", "banana", "cherry"))
        p.handle_key("down")
        p.handle_key("down")
        assert p.cursor == 2
        p.handle_key("b")  # only banana matches
        assert p.cursor == 0


class TestSelection:
    def test_should_toggle_item_with_tab(self):
        p = Picker(_choices("a", "b"), multiselect=True)
        p.handle_key("tab")
        v = p.view()
        assert v.items[0].selected is True
        assert sum(i.selected for i in v.items) == 1

    def test_should_deselect_with_second_tab(self):
        p = Picker(_choices("a", "b"), multiselect=True)
        p.handle_key("tab")
        p.handle_key("tab")
        v = p.view()
        assert v.items[0].selected is False

    def test_should_select_all_with_shift_tab(self):
        p = Picker(_choices("a", "b", "c"), multiselect=True)
        p.handle_key("shift-tab")
        v = p.view()
        assert all(item.selected for item in v.items)

    def test_should_deselect_all_with_shift_tab_when_any_selected(self):
        p = Picker(_choices("a", "b"), multiselect=True)
        p.handle_key("tab")
        p.handle_key("shift-tab")
        v = p.view()
        assert not any(item.selected for item in v.items)

    def test_should_ignore_tab_when_not_multiselect(self):
        p = Picker(_choices("a", "b"))
        p.handle_key("tab")
        assert len(p.selected) == 0


class TestEvents:
    def test_event_keys(self):
        p = Picker(_choices("a", "b"))
        assert p.handle_key("enter") == "select"
        assert p.handle_key("esc") == "cancel"
        assert p.handle_key("ctrl-r") == "confirm"
        assert p.handle_key("down") is None


class TestValue:
    def test_should_return_cursor_value_in_single_mode(self):
        p = Picker(_choices("a", "b", "c"))
        p.handle_key("down")
        assert p.value == "b"

    def test_should_return_selected_values_in_multiselect(self):
        p = Picker(_choices("a", "b", "c"), multiselect=True)
        p.handle_key("tab")
        p.handle_key("down")
        p.handle_key("down")
        p.handle_key("tab")
        assert p.value == ["a", "c"]

    def test_should_return_none_when_no_matches(self):
        p = Picker(_choices("a"))
        p.handle_key("z")
        assert p.value is None


class TestQuerySetter:
    def test_query_property(self):
        p = Picker(_choices("apple", "banana", "apricot"))
        p.query = "ap"
        assert p.view().filtered == 2
        p.query = ""
        assert p.view().filtered == 3


class TestView:
    def test_view_limits_and_query(self):
        p = Picker(_choices("a", "b", "c", "d", "e"), max_height=3)
        assert len(p.view().items) == 3
        p2 = Picker(_choices("a"))
        p2.handle_key("h")
        p2.handle_key("i")
        assert "hi" in p2.view().query
