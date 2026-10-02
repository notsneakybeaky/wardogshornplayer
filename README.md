# Wardogs H-key horn scripts

Two Python scripts that play the horn in Wardogs by pressing the H key for you.

| Script | What it does |
| --- | --- |
| `wardogs_h_melody.py` | Listens to an MP3 and honks along to its rhythm |
| `truck_honk.py` | Plays a built-in Indian-truck honk routine on a beat |

Both give you a countdown to click into the game window, and **Esc stops them at any time**.

## Setup

1. Install Python 3.9 or newer.
2. Install ffmpeg (only the melody script needs it, to decode MP3s).
   On Windows: `winget install ffmpeg`, then open a new terminal.
3. Install the libraries:

       pip install -r requirements.txt

   On Python 3.13 and newer this also installs `audioop-lts`, which pydub needs
   because 3.13 removed the built-in `audioop` module.

If the game ignores the key presses, run your terminal as administrator.

---

## wardogs_h_melody.py

The horn only has one note, so this script copies the song's **rhythm**. It finds
where each note starts and holds H for roughly as long as that note rings.

    python wardogs_h_melody.py song.mp3

| Option | Default | What it does |
| --- | --- | --- |
| `--start SEC` | 0 | Skip this many seconds into the song |
| `--length SEC` | whole song | Only use this many seconds |
| `--speed X` | 1.0 | Play faster (`1.2`) or slower (`0.8`) |
| `--sensitivity X` | 1.0 | Higher catches more notes, lower if it spams |
| `--no-drums` | off | Strip percussion so it follows the melody, not the beat |
| `--low HZ` / `--high HZ` | 200 / 3000 | Frequency band to listen to (narrow it to the lead melody) |
| `--key K` | h | Key to press |
| `--delay SEC` | 5 | Countdown before it starts |
| `--dry-run` | off | Analyse only, press nothing |
| `--export FILE` | none | Save the note timings as JSON |

**Getting it to sound good.** Full song mixes turn into random honking. Use a
simple instrumental or an "8-bit / MIDI version", and trim to just the riff with
`--start` and `--length`. Songs that work well because people recognise their rhythm:
We Will Rock You (leave `--no-drums` off), Shave and a Haircut, the Seven Nation
Army riff, the Imperial March opening, Another One Bites the Dust, and the
stadium "Charge!" fanfare.

---

## truck_honk.py

Plays a roughly 50-second honk routine at 110 BPM: intro, the "beep beep beeeep"
horn-OK riff, a 3-3-2 dhol groove, a build-up into a speeding honk roll, a drop,
the groove again, an even faster roll, and one long final honk. It prints each
section as it plays.

    python truck_honk.py

| Option | Default | What it does |
| --- | --- | --- |
| `--bpm N` | 110 | Tempo |
| `--loop` | off | Repeat the routine until you press Esc |
| `--key K` | h | Key to press |
| `--delay SEC` | 5 | Countdown before it starts |

**Making your own beat.** Edit `BARS` and `SONG` at the top of the file. Each bar
is 16 steps: `x` is a honk, `=` keeps holding it, `.` is silence. For example
`x.x.x===....x.x.` is beep, beep, beeeep, pause, beep, beep. `SONG` lists the
sections in order with how many times to repeat each one and a tempo multiplier.

---

## Libraries used

pydub (MP3 decoding through ffmpeg), audioop-lts (pydub support on Python 3.13+),
numpy (audio arrays), scipy (band-pass and smoothing filters), librosa (note
detection, drum separation, loudness, tempo), pynput (key presses and the Esc
hotkey), rich (countdown and tables), tqdm (progress bar), plus argparse, json,
threading, pathlib and time from the standard library.

## A word of caution

Some games ban automated input. A horn script gives no gameplay advantage, but
check Wardogs' rules if you care about your account, or try it on an alt first.
