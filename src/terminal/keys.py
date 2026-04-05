"""Key maps and escape sequence classification."""

from __future__ import annotations

import codecs
import os
import select
from dataclasses import dataclass


@dataclass(frozen=True)
class Paste:
    """Represents pasted text from bracketed paste."""

    text: str


# Single-byte → key name
BYTE_KEYS: dict[bytes, str] = {
    b"\t": "tab",
    b"\r": "enter",
    b"\n": "enter",
    b"\x01": "home",
    b"\x02": "ctrl-b",
    b"\x04": "ctrl-d",
    b"\x05": "end",
    b"\x06": "ctrl-f",
    b"\x07": "ctrl-g",
    b"\x0b": "ctrl-k",
    b"\x0c": "ctrl-l",
    b"\x0e": "ctrl-n",
    b"\x0f": "ctrl-o",
    b"\x10": "ctrl-p",
    b"\x11": "ctrl-q",
    b"\x12": "ctrl-r",
    b"\x14": "ctrl-t",
    b"\x15": "clear-line",
    b"\x16": "ctrl-v",
    b"\x17": "delete-word",
    b"\x18": "ctrl-x",
    b"\x19": "ctrl-y",
    b"\x1a": "ctrl-z",
    b" ": "space",
    b"\x7f": "backspace",
    b"\x08": "backspace",
}

# \x1b[ + 1-2 bytes → key name  (CSI sequences)
CSI_KEYS: dict[bytes, str] = {
    b"A": "up",
    b"B": "down",
    b"C": "right",
    b"D": "left",
    b"H": "home",
    b"F": "end",
    b"Z": "shift-tab",
    b"I": "focus",
    b"3~": "delete",
    b"5~": "page-up",
    b"6~": "page-down",
}

# \x1b + single byte → key name  (Alt / Option sequences)
ESC_KEYS: dict[bytes, str] = {
    b"\x7f": "delete-word",
    b"b": "word-left",
    b"f": "word-right",
    b"d": "delete-word",
}

# \x1b\x1b[X → key name  (double-escape Option+arrow on some terminals)
DBL_ESC_KEYS: dict[bytes, str] = {
    b"C": "word-right",
    b"D": "word-left",
    b"A": "up",
    b"B": "down",
}

# \x1b[1;{mod}{dir} → key name  (modifier arrow sequences)
MOD_KEYS: dict[tuple[bytes, bytes], str] = {
    (b"3", b"C"): "word-right",  # Option
    (b"3", b"D"): "word-left",
    (b"9", b"C"): "word-right",  # Cmd (iTerm2)
    (b"9", b"D"): "word-left",
    (b"2", b"C"): "end",  # Shift
    (b"2", b"D"): "home",
}


class KeyReader:
    """Reads and classifies terminal input from a file descriptor."""

    def __init__(self, fd: int, wake_fd: int | None = None) -> None:
        self._fd = fd
        self._wake_fd = wake_fd
        self._utf8 = codecs.getincrementaldecoder("utf-8")("ignore")

    def read(self, timeout: float = 1 / 60) -> str | Paste | None:
        """Read a single keypress. Returns None on timeout or wake."""
        fds = [self._fd] if self._wake_fd is None else [self._fd, self._wake_fd]
        try:
            ready = select.select(fds, [], [], timeout)[0]
        except InterruptedError:
            return None
        if self._wake_fd is not None and self._wake_fd in ready:
            os.read(self._wake_fd, 1024)
        if self._fd not in ready:
            return None
        return self._classify(os.read(self._fd, 1))

    def _classify(self, ch: bytes) -> str | Paste | None:
        if ch == b"\x1b":
            return self._read_escape()
        if ch == b"\x03":
            raise KeyboardInterrupt
        return BYTE_KEYS.get(ch) or self._read_utf8(ch)

    def _read_utf8(self, initial: bytes) -> str | None:
        result = self._utf8.decode(initial)
        while not result:
            if not select.select([self._fd], [], [], 0.01)[0]:
                self._utf8.reset()
                return None
            result = self._utf8.decode(os.read(self._fd, 1))
        return result

    def _read_escape(self) -> str | Paste | None:
        """Parse an escape sequence into a key name."""
        if not select.select([self._fd], [], [], 0.02)[0]:
            return "esc"
        seq = os.read(self._fd, 16)
        # Bracketed paste
        if seq.startswith(b"[200~"):
            return self._read_paste(seq[5:])
        # CSI sequence: \x1b[...
        if seq[:1] == b"[":
            return parse_csi(seq[1:])
        # Double escape: \x1b\x1b[X — Option+arrow on some terminals
        if seq[:1] == b"\x1b" and len(seq) >= 3:
            return DBL_ESC_KEYS.get(seq[2:3])
        # Alt/Option + key
        return ESC_KEYS.get(seq[:1])

    def _read_paste(self, initial: bytes) -> Paste:
        """Read bracketed paste content until \\x1b[201~."""
        buf = bytearray(initial)
        while True:
            idx = buf.find(b"\x1b[201~")
            if idx >= 0:
                return Paste(
                    buf[:idx].decode("utf-8", errors="replace").replace("\r", "\n")
                )
            if select.select([self._fd], [], [], 0.1)[0]:
                buf.extend(os.read(self._fd, 4096))
            else:
                return Paste(buf.decode("utf-8", errors="replace").replace("\r", "\n"))


def parse_csi(csi: bytes) -> str | None:
    """Parse a CSI (Control Sequence Introducer) payload."""
    if csi[:1] == b"O":
        return None  # focus lost
    # SGR mouse: <button;x;yM or <button;x;ym
    if csi[:1] == b"<":
        return parse_sgr_mouse(csi[1:])
    hit = CSI_KEYS.get(csi) or CSI_KEYS.get(csi[:2])
    if hit:
        return hit
    # Modifier: 1;{mod}{dir}
    if len(csi) >= 4 and csi[:1] == b"1":
        return MOD_KEYS.get((csi[2:3], csi[3:4]))
    return None


_MOUSE_BUTTONS = {64: "scroll-up", 65: "scroll-down"}


def parse_sgr_mouse(payload: bytes) -> str | None:
    """Parse SGR mouse payload: button;x;y{M|m}."""
    try:
        text = payload.decode()
        if text[-1] not in ("M", "m"):
            return None
        button = int(text[:-1].split(";")[0])
    except (ValueError, IndexError, UnicodeDecodeError):
        return None
    return _MOUSE_BUTTONS.get(button)
