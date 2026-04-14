"""Benchmark measure.py functions — before/after C migration."""

import time

from ttyz.measure import distribute, slice_at_width, strip_ansi, truncate


def bench(name, fn, iterations=100_000):
    # warmup
    for _ in range(1000):
        fn()
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    us = elapsed / iterations * 1_000_000
    print(f"{name:40s}  {us:8.3f} µs/call  ({iterations} iters, {elapsed:.3f}s total)")


if __name__ == "__main__":
    # ── distribute ────────────────────────────────────────────────
    weights_small = [1, 2, 3, 4, 5]
    weights_large = list(range(1, 51))

    bench("distribute(100, 5 weights)", lambda: distribute(100, weights_small))
    bench("distribute(1000, 50 weights)", lambda: distribute(1000, weights_large))

    # ── slice_at_width ────────────────────────────────────────────
    ascii_str = "hello world this is a test string for slicing"
    wide_str = "你好世界" * 10
    mixed_str = "abc你好def世界ghi"

    bench("slice_at_width(ascii, 20)", lambda: slice_at_width(ascii_str, 20))
    bench("slice_at_width(wide, 20)", lambda: slice_at_width(wide_str, 20))
    bench("slice_at_width(mixed, 8)", lambda: slice_at_width(mixed_str, 8))

    # ── strip_ansi ────────────────────────────────────────────────
    plain = "hello world no escapes here"
    ansi_light = "\033[1mhello\033[0m"
    ansi_heavy = "\033[38;2;255;128;0m" + "x" * 100 + "\033[0m"
    ansi_many = "".join(f"\033[{i}m" + "ab" for i in range(30)) + "\033[0m"

    bench("strip_ansi(plain)", lambda: strip_ansi(plain))
    bench("strip_ansi(light ansi)", lambda: strip_ansi(ansi_light))
    bench("strip_ansi(heavy ansi)", lambda: strip_ansi(ansi_heavy))
    bench("strip_ansi(many escapes)", lambda: strip_ansi(ansi_many))

    # ── truncate ──────────────────────────────────────────────────
    long_plain = "a" * 200
    long_ansi = "\033[1m" + "a" * 200 + "\033[0m"
    short = "hi"

    bench("truncate(short, 10)", lambda: truncate(short, 10))
    bench("truncate(long plain, 20)", lambda: truncate(long_plain, 20))
    bench(
        "truncate(long plain, 20, ellipsis)",
        lambda: truncate(long_plain, 20, ellipsis=True),
    )
    bench("truncate(long ansi, 20)", lambda: truncate(long_ansi, 20))
    bench(
        "truncate(long ansi, 20, ellipsis)",
        lambda: truncate(long_ansi, 20, ellipsis=True),
    )
