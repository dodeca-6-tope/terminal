"""Tests for Notifications."""

import time

from terminal import Notifications


def test_add_and_active():
    n = Notifications()
    n.add("hello")
    active = n.active()
    assert len(active) == 1
    assert active[0].text == "hello"
    assert active[0].level == "info"

def test_custom_level():
    n = Notifications()
    n.add("fail", "error")
    assert n.active()[0].level == "error"

def test_expiry():
    n = Notifications(ttl=0.05)
    n.add("gone soon")
    assert len(n.active()) == 1
    time.sleep(0.06)
    assert len(n.active()) == 0

def test_newest_first():
    n = Notifications()
    n.add("first")
    n.add("second")
    active = n.active()
    assert active[0].text == "second"
    assert active[1].text == "first"

def test_empty():
    assert Notifications().active() == []
