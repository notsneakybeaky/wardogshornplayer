#!/usr/bin/env python3
"""Indian-truck honk routine on the H key, played on a beat. Press Esc to stop.

Each bar is 16 steps (16th notes): x = honk, = = keep holding, . = silence.
"""
import argparse, threading, time

from pynput.keyboard import Controller, Key, Listener
from rich.console import Console

console = Console()
stop = threading.Event()

BARS = {
    "intro":   "x===....x===....",
    "horn ok": "x.x.x===....x.x.",                    # beep beep beeeep
    "groove":  "x..x..x.x..x..x.",                    # 3-3-2 dhol rhythm
    "bounce":  "x.xx.x.xx.x.x===",
    "build":   "x.x.x.x.xxxxxxxx",
    "roll":    "xxxxxxxxxxxxxxxx",
    "drop":    "x===x===x.x.x===",
    "outro":   "x===============",
}
# (section, times to repeat, tempo multiplier)
SONG = [
    ("intro", 2, 1.0), ("horn ok", 2, 1.0), ("groove", 4, 1.0), ("bounce", 2, 1.0),
    ("build", 2, 1.0), ("roll", 1, 1.25), ("roll", 1, 1.5), ("drop", 2, 1.0),
    ("groove", 4, 1.1), ("horn ok", 2, 1.1), ("build", 1, 1.2), ("roll", 2, 1.6),
    ("outro", 1, 1.0),
]


def play_bar(kb, key, bar, step):
    t, i = time.perf_counter(), 0
    while i < len(bar) and not stop.is_set():
        if bar[i] == "x":
            n = 1
            while i + n < len(bar) and bar[i + n] == "=":
                n += 1
            kb.press(key)
            stop.wait(max(n * step - 0.03, step * 0.6))  # tiny gap so repeats sound separate
            kb.release(key)
            i += n
        else:
            i += 1
        stop.wait(max(0, t + i * step - time.perf_counter()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", default="h")
    ap.add_argument("--bpm", type=float, default=110, help="tempo (default 110)")
    ap.add_argument("--loop", action="store_true", help="repeat the routine until Esc")
    ap.add_argument("--delay", type=int, default=5, help="countdown seconds")
    a = ap.parse_args()

    Listener(on_press=lambda k: (stop.set(), False)[1] if k == Key.esc else None).start()
    with console.status("") as status:
        for s in range(a.delay, 0, -1):
            status.update(f"[bold yellow]Focus Wardogs... honking in {s}s (Esc stops)")
            if stop.wait(1):
                return

    kb = Controller()
    while not stop.is_set():
        for name, reps, mult in SONG:
            if stop.is_set():
                break
            console.print(f"[bold magenta]{name.upper():8}[/] [dim]{BARS[name]}[/] x{reps}")
            step = 60 / (a.bpm * mult) / 4
            for _ in range(reps):
                play_bar(kb, a.key, BARS[name], step)
        if not a.loop:
            break
    kb.release(a.key)
    console.print("[red]Stopped." if stop.is_set() else "[green]HORN OK PLEASE")


if __name__ == "__main__":
    main()
