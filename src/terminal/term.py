"""Terminal — TTY lifecycle that composes Screen and KeyReader."""

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
from typing import Any, Protocol

from terminal.keys import KeyReader, Paste
from terminal.screen import Screen


class Terminal(Protocol):
    """Protocol for terminal backends (real TTY or test fake)."""

    def __enter__(self) -> Terminal: ...
    def __exit__(self, *_: object) -> None: ...
    @property
    def size(self) -> os.terminal_size: ...
    def readkey(self, timeout: float = 1 / 60) -> str | Paste | None: ...
    def readkey_nowait(self) -> str | Paste | None: ...
    def render(self, lines: list[str]) -> None: ...
    def cleanup(self) -> None: ...
    def wake(self) -> None: ...


class TTY:
    """Context manager for full-screen terminal UI sessions."""

    def __init__(self) -> None:
        self._fd: int | None = None
        self._saved: list[Any] | None = None
        self._active = False
        self._atexit = False
        self._resized = False
        self._prev_sigwinch: Callable[[int, FrameType | None], Any] | int | None = None
        self._keys: KeyReader | None = None
        self.screen = Screen()
        self._wake_r, self._wake_w = os.pipe()

    def __enter__(self) -> TTY:
        fd = sys.stdin.fileno()
        self._fd = fd
        self._saved = termios.tcgetattr(fd)
        self._enter_raw()
        self._active = True
        sys.stdout.write(
            "\033[?1049h\033[?25l\033[?7l\033[?2004h\033[?1004h\033[?1000h\033[?1006h"
        )
        sys.stdout.flush()
        self._prev_sigwinch = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._on_sigwinch)
        self._keys = KeyReader(fd, self._wake_r)
        if not self._atexit:
            atexit.register(self.cleanup)
            self._atexit = True
        return self

    def __exit__(self, *_: object) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        """Leave alt screen, show cursor, restore terminal."""
        if not self._active:
            return
        self._active = False
        self.screen.invalidate()
        sys.stdout.write(
            "\033[?1006l\033[?1000l\033[?1004l\033[?2004l\033[?7h\033[?25h\033[?1049l"
        )
        sys.stdout.flush()
        self._restore()
        if self._prev_sigwinch is not None:
            signal.signal(signal.SIGWINCH, self._prev_sigwinch)
            self._prev_sigwinch = None

    def _on_sigwinch(self, signum: int, frame: FrameType | None) -> None:
        self._resized = True
        self.screen.invalidate()

    def readkey(self, timeout: float = 1 / 60) -> str | Paste | None:
        """Read a single keypress. Returns 'resize' on terminal resize, None on timeout."""
        assert self._keys is not None
        if self._consume_resize():
            return "resize"
        result = self._keys.read(timeout)
        if result is None and self._consume_resize():
            return "resize"
        return result

    def readkey_nowait(self) -> str | Paste | None:
        """Read a keypress if one is immediately available, else None."""
        return self.readkey(timeout=0)

    @property
    def size(self) -> os.terminal_size:
        """Current terminal dimensions (columns, lines)."""
        return os.get_terminal_size()

    def render(self, lines: list[str]) -> None:
        """Render a frame to the screen."""
        self.screen.render(lines)

    def wake(self) -> None:
        """Wake the event loop from any thread."""
        with contextlib.suppress(OSError):
            os.write(self._wake_w, b"\x00")

    def _consume_resize(self) -> bool:
        if self._resized:
            self._resized = False
            return True
        return False

    def _enter_raw(self) -> None:
        """Switch to raw mode, re-enable output processing for \\n → \\r\\n."""
        assert self._fd is not None
        tty.setraw(self._fd)
        attrs = termios.tcgetattr(self._fd)
        attrs[1] |= termios.OPOST
        termios.tcsetattr(self._fd, termios.TCSADRAIN, attrs)

    def _restore(self) -> None:
        """Restore saved terminal attributes."""
        if self._saved and self._fd is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
