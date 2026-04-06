from __future__ import annotations

from unittest.mock import patch

from terminal.components.toast import Toast


def test_show_and_active():
    t = Toast()
    t.show("hello")
    msgs = t.active()
    assert len(msgs) == 1
    assert msgs[0].text == "hello"
    assert msgs[0].level == "info"


def test_multiple_active():
    t = Toast()
    t.show("first")
    t.show("second")
    msgs = t.active()
    assert [m.text for m in msgs] == ["second", "first"]


def test_expired_pruned():
    t = Toast(ttl=1)
    with patch("terminal.components.toast.time") as mock_time:
        mock_time.monotonic.return_value = 0.0
        t.show("old")
        mock_time.monotonic.return_value = 0.5
        t.show("new")
        mock_time.monotonic.return_value = 1.2
        msgs = t.active()
    assert [m.text for m in msgs] == ["new"]


def test_custom_duration():
    t = Toast(ttl=1)
    with patch("terminal.components.toast.time") as mock_time:
        mock_time.monotonic.return_value = 0.0
        t.show("short", duration=0.5)
        t.show("long", duration=5)
        mock_time.monotonic.return_value = 0.6
        msgs = t.active()
    assert [m.text for m in msgs] == ["long"]


def test_level():
    t = Toast()
    t.show("fail", level="error")
    assert t.active()[0].level == "error"


def test_visible():
    t = Toast(ttl=1)
    assert not t.visible
    with patch("terminal.components.toast.time") as mock_time:
        mock_time.monotonic.return_value = 0.0
        t.show("x")
        assert t.visible
        mock_time.monotonic.return_value = 2.0
        assert not t.visible


def test_empty_active():
    t = Toast()
    assert t.active() == []
