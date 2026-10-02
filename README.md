# Wardogs H-key melody player

Turns an MP3 into timed presses of the H key (the single-tone key in Wardogs).
The key has one pitch, so the script reproduces the song's rhythm: every note
it hears becomes a press, held for roughly as long as the note rings.

## Setup
1. Install Python 3.9+ and ffmpeg (needed to decode MP3; on Windows, `winget install ffmpeg`).
2. `pip install -r requirements.txt`

## Use
    python wardogs_h_melody.py song.mp3

You get a 5 second countdown to click into the game window, then it plays.
Press **Esc** to stop at any time.

Useful options:
- `--dry-run --export notes.json` analyse only and save the timings, no key presses
- `--start 30 --length 20` play just a 20 s slice starting at 0:30
- `--sensitivity 1.5` catch more notes (lower it if it spams)
- `--no-drums` strip percussion so it follows the melody instead of the beat
- `--low 300 --high 2000` narrow the frequency band to the lead melody
- `--speed 1.2` play faster, `--key j` press a different key, `--delay 10` longer countdown

If presses don't register in the game, run the terminal as administrator
(some games ignore input from non-elevated programs).

## Libraries and what each does
pydub (MP3 decoding via ffmpeg), numpy (signal arrays), scipy (band-pass and
median filters), librosa (onset detection, drum separation, RMS, tempo),
pynput (key presses and the Esc abort hotkey), rich (countdown and summary
table), tqdm (progress bar), plus argparse, json, threading, pathlib and time.
