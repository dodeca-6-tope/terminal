"""Terminal — full-screen TTY lifecycle with cell-level diffing."""

from __future__ import annotations

import atexit
import contextlib
import os
import signal
import sys
import termios
import tty
from collections.abc import Callable
from types import FrameType
from typing import Any

from ttyz.control import Command
from ttyz.ext import Buffer, render_to_buffer
from ttyz.keys import (
    KITTY_DISABLE,
    KITTY_ENABLE,
    Event,
    KeyReader,
    Resize,
)

_ENTER = (
    "\033[?1049h\033[?25l\033[?7l\033[?2004h\033[?1004h\033[?1000h\033[?1006h"
    + KITTY_ENABLE
)
_EXIT = (
    KITTY_DISABLE
    + "\033[?1006l\033[?1000l\033[?1004l\033[?2004l\033[?7h\033[?25h\033[?1049l"
)


class TTY:
    """Context manager for full-screen terminal UI sessions."""

    def __init__(
        self, size: Callable[[], os.terminal_size] = os.get_terminal_size
    ) -> None:
        self._fd: int | None = None
        self._saved: list[Any] | None = None
        self._active = False
        self._resized = False
        self._prev_sigwinch: Callable[[int, FrameType | None], Any] | int | None = None
        self._keys: KeyReader | None = None
        self._prev: Buffer | None = None
        self._wake_r, self._wake_w = os.pipe()
        self._size = size
        self._cached_size: os.terminal_size | None = None
        atexit.register(self.cleanup)

    def _current_size(self) -> os.terminal_size:
        if self._cached_size is None:
            self._cached_size = self._size()
        return self._cached_size

    def __enter__(self) -> TTY:
        fd = sys.stdin.fileno()
        self._fd = fd
        self._saved = termios.tcgetattr(fd)
        self._enter_raw()
        self._active = True
        self._prev_sigwinch = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._on_sigwinch)
        self._keys = KeyReader(fd, self._wake_r)
        return self

    def __exit__(self, *_: object) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        """Leave alt screen, show cursor, restore terminal."""
        if self._active:
            self._active = False
            self._prev = None
            sys.stdout.write(_EXIT)
            sys.stdout.flush()
            if self._saved and self._fd is not None:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
            if self._prev_sigwinch is not None:
                signal.signal(signal.SIGWINCH, self._prev_sigwinch)
                self._prev_sigwinch = None
        atexit.unregister(self.cleanup)
        if self._wake_r >= 0:
            os.close(self._wake_r)
            os.close(self._wake_w)
            self._wake_r = -1
            self._wake_w = -1

    def _on_sigwinch(self, signum: int, frame: FrameType | None) -> None:
        self._resized = True
        self._prev = None
        self._cached_size = None

    def _drain_resize(self) -> Resize | None:
        if not self._resized:
            return None
        self._resized = False
        size = self._current_size()
        return Resize(cols=size.columns, lines=size.lines)

    def readkey(self, timeout: float = 1 / 60) -> Event | None:
        """Read a single input event. Returns None on timeout."""
        assert self._keys is not None
        if (ev := self._drain_resize()) is not None:
            return ev
        result = self._keys.read(timeout)
        if result is None and (ev := self._drain_resize()) is not None:
            return ev
        return result

    def draw(self, node: object) -> None:
        """Draw a node tree to the terminal with cell-level diffing."""
        size = self._current_size()
        prev = self._prev

        buf = Buffer(size.columns, size.lines)
        render_to_buffer(node, buf)

        if prev is None or (buf.width, buf.height) != (prev.width, prev.height):
            body = f"\033[H\033[2J\033[0m{buf.dump()}"
        else:
            body = buf.diff(prev)

        sys.stdout.buffer.write(f"\033[?2026h{body}\033[?2026l".encode())
        sys.stdout.buffer.flush()

        self._prev = buf

    def write(self, *commands: Command) -> None:
        """Write control commands to the terminal.

        tty.write(SetTitle("my app"), CursorShape(2))
        """
        sys.stdout.write("".join(c.sequence() for c in commands))
        sys.stdout.flush()

    @property
    def size(self) -> os.terminal_size:
        """Current terminal dimensions (columns, lines)."""
        return self._current_size()

    def wake(self) -> None:
        """Wake the event loop from any thread."""
        with contextlib.suppress(OSError):
            os.write(self._wake_w, b"\x00")

    @property
    def active(self) -> bool:
        return self._active

    def suspend(self) -> None:
        """Leave alt screen and restore terminal for a child process."""
        sys.stdout.write(_EXIT)
        sys.stdout.flush()
        if self._saved and self._fd is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)

    def resume(self) -> None:
        """Re-enter alt screen and raw mode after a child process."""
        self._enter_raw()
        self._prev = None

    def _enter_raw(self) -> None:
        """Switch to raw mode with output processing, enter alt screen."""
        assert self._fd is not None
        tty.setraw(self._fd)
        attrs = termios.tcgetattr(self._fd)
        attrs[1] |= termios.OPOST
        termios.tcsetattr(self._fd, termios.TCSADRAIN, attrs)
        sys.stdout.write(_ENTER)
        sys.stdout.flush()
