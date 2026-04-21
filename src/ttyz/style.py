"""ANSI styling helpers — thin wrappers that produce escape codes."""

_BOLD_ON, _BOLD_OFF = "\033[1m", "\033[22m"
_DIM_ON, _DIM_OFF = "\033[2m", "\033[22m"
_ITALIC_ON, _ITALIC_OFF = "\033[3m", "\033[23m"
_UNDERLINE_ON, _UNDERLINE_OFF = "\033[4m", "\033[24m"
_BLINK_ON, _BLINK_OFF = "\033[5m", "\033[25m"
_REVERSE_ON, _REVERSE_OFF = "\033[7m", "\033[27m"
_INVISIBLE_ON, _INVISIBLE_OFF = "\033[8m", "\033[28m"
_STRIKE_ON, _STRIKE_OFF = "\033[9m", "\033[29m"
_OVERLINE_ON, _OVERLINE_OFF = "\033[53m", "\033[55m"
_FG_OFF = "\033[39m"
_BG_OFF = "\033[49m"


def bold(s: str) -> str:
    return f"{_BOLD_ON}{s}{_BOLD_OFF}"


def dim(s: str) -> str:
    return f"{_DIM_ON}{s}{_DIM_OFF}"


def italic(s: str) -> str:
    return f"{_ITALIC_ON}{s}{_ITALIC_OFF}"


def underline(s: str) -> str:
    return f"{_UNDERLINE_ON}{s}{_UNDERLINE_OFF}"


def blink(s: str) -> str:
    return f"{_BLINK_ON}{s}{_BLINK_OFF}"


def reverse(s: str) -> str:
    return f"{_REVERSE_ON}{s}{_REVERSE_OFF}"


def invisible(s: str) -> str:
    return f"{_INVISIBLE_ON}{s}{_INVISIBLE_OFF}"


def strikethrough(s: str) -> str:
    return f"{_STRIKE_ON}{s}{_STRIKE_OFF}"


def overline(s: str) -> str:
    return f"{_OVERLINE_ON}{s}{_OVERLINE_OFF}"


def color(c: int, s: str) -> str:
    """Apply 256-color foreground."""
    return f"\033[38;5;{c}m{s}{_FG_OFF}"


def bg(c: int, s: str) -> str:
    """Apply 256-color background."""
    return f"\033[48;5;{c}m{s}{_BG_OFF}"


def rgb(r: int, g: int, b: int, s: str) -> str:
    """Apply 24-bit true-color foreground."""
    return f"\033[38;2;{r};{g};{b}m{s}{_FG_OFF}"


def bg_rgb(r: int, g: int, b: int, s: str) -> str:
    """Apply 24-bit true-color background."""
    return f"\033[48;2;{r};{g};{b}m{s}{_BG_OFF}"
