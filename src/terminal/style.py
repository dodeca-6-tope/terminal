"""ANSI styling helpers — thin wrappers that produce escape codes."""


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def italic(s: str) -> str:
    return f"\033[3m{s}\033[0m"


def reverse(s: str) -> str:
    return f"\033[7m{s}\033[0m"


def color(c: int, s: str) -> str:
    return f"\033[38;5;{c}m{s}\033[0m"
