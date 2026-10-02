#!/usr/bin/env python3
"""Wardogs H-key melody player: turns an MP3 into timed H-key presses.

The H key plays a single tone, so this reproduces the song's rhythm:
each detected note onset becomes a press, held for the note's length.
Press Esc at any time to abort.
"""
import argparse, json, threading, time
from pathlib import Path

import numpy as np
import librosa
from scipy.signal import butter, sosfiltfilt, medfilt
from pydub import AudioSegment
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from pynput.keyboard import Controller, Key, Listener

console = Console()
stop = threading.Event()


def load_audio(path, sr=22050, start=0.0, length=None):
    """Decode any format ffmpeg understands (MP3 included) with pydub."""
    seg = AudioSegment.from_file(path).set_channels(1).set_frame_rate(sr)
    seg = seg[int(start * 1000):int((start + length) * 1000) if length else None]
    y = np.array(seg.get_array_of_samples(), dtype=np.float32)
    return y / float(1 << (8 * seg.sample_width - 1)), sr


def extract_notes(y, sr, low=200, high=3000, sens=1.0, min_gap=0.08, max_hold=0.6, no_drums=False):
    """Return a list of (start_seconds, hold_seconds) note events."""
    y = sosfiltfilt(butter(4, [low, high], btype="band", fs=sr, output="sos"), y)
    if no_drums:
        y = librosa.effects.harmonic(y)  # drop drums, keep the melodic part
    hop = 256
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onsets = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop,
                                        delta=0.07 / sens, backtrack=True, units="time")
    rms = medfilt(librosa.feature.rms(y=y, hop_length=hop)[0], 5)
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    level = lambda a, b: rms[(times >= a) & (times < b)].max(initial=0.0)
    # a real note makes the energy rise; note-offs and echoes do not
    onsets = [t for t in onsets if level(t, t + 0.06) > 1.5 * level(t - 0.06, t) + 0.01 * rms.max()]
    onsets = [t for i, t in enumerate(onsets) if i == 0 or t - onsets[i - 1] >= min_gap]
    notes = []
    for i, t in enumerate(onsets):
        nxt = onsets[i + 1] if i + 1 < len(onsets) else times[-1]
        win = (times >= t) & (times < nxt)
        if not win.any():
            continue
        peak = rms[win].max()
        quiet = np.where(rms[win] < peak * 0.35)[0]  # note ends when it decays
        end = times[win][quiet[0]] if len(quiet) else nxt
        hold = float(np.clip(end - t, 0.03, min(max_hold, (nxt - t) * 0.85)))
        notes.append((float(t), hold))
    return notes


def countdown(seconds):
    with console.status("") as status:
        for s in range(seconds, 0, -1):
            status.update(f"[bold yellow]Focus the Wardogs window... starting in {s}s (Esc aborts)")
            time.sleep(1)


def play(notes, key="h", speed=1.0):
    kb, t0 = Controller(), time.perf_counter()
    for start, hold in tqdm(notes, desc="Playing", unit="note"):
        while (wait := start / speed - (time.perf_counter() - t0)) > 0:
            if stop.wait(min(wait, 0.005)):
                return
        if stop.is_set():
            return
        kb.press(key)
        stop.wait(hold / speed)
        kb.release(key)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mp3", type=Path)
    ap.add_argument("--key", default="h", help="key to press (default h)")
    ap.add_argument("--start", type=float, default=0.0, help="skip this many seconds of the song")
    ap.add_argument("--length", type=float, help="only use this many seconds")
    ap.add_argument("--speed", type=float, default=1.0, help="tempo multiplier")
    ap.add_argument("--sensitivity", type=float, default=1.0, help="higher = more notes")
    ap.add_argument("--low", type=float, default=200, help="melody band low Hz")
    ap.add_argument("--high", type=float, default=3000, help="melody band high Hz")
    ap.add_argument("--no-drums", action="store_true", help="strip percussion first (HPSS)")
    ap.add_argument("--delay", type=int, default=5, help="countdown seconds")
    ap.add_argument("--dry-run", action="store_true", help="analyse only, press nothing")
    ap.add_argument("--export", type=Path, help="save note timings as JSON")
    a = ap.parse_args()

    with console.status(f"Analysing {a.mp3.name}..."):
        y, sr = load_audio(str(a.mp3), start=a.start, length=a.length)
        notes = extract_notes(y, sr, a.low, a.high, a.sensitivity, no_drums=a.no_drums)
    tempo = float(np.atleast_1d(librosa.beat.beat_track(y=y, sr=sr)[0])[0])
    table = Table(title="Wardogs H-key melody")
    for k, v in [("Duration", f"{len(y) / sr:.1f}s"), ("Notes", str(len(notes))),
                 ("Tempo", f"{tempo:.0f} BPM"), ("Speed", f"x{a.speed}")]:
        table.add_row(k, v)
    console.print(table)
    if a.export:
        a.export.write_text(json.dumps([{"start": s, "hold": h} for s, h in notes], indent=1))
        console.print(f"[green]Saved timings to {a.export}")
    if a.dry_run or not notes:
        return
    Listener(on_press=lambda k: (stop.set(), False)[1] if k == Key.esc else None).start()
    countdown(a.delay)
    play(notes, a.key, a.speed)
    console.print("[red]Aborted." if stop.is_set() else "[green]Done!")


if __name__ == "__main__":
    main()
