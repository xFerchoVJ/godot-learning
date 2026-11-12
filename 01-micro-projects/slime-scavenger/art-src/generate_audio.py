#!/usr/bin/env python3
"""Chiptune sound effects for Slime Scavenger, synthesised with numpy (no samples).

Outputs (in $OUT_DIR): one mono 16-bit 44.1 kHz .wav per effect, all peak-normalised.
Usage: ./run_char.sh audio
"""
import os
import wave

import numpy as np

# =============================== TUNABLES ===============================
SR = 44100                 # sample rate, Hz
PEAK = 0.6                 # every effect is normalised to this peak (0..1) so none is much louder
FADE_MS = 3                # tiny fade in/out: avoids clicks at the start and end


# =============================== BUILDING BLOCKS ===============================
def pulse(freq, duty=0.5):
    """Pulse wave from a frequency curve (Hz per sample). Integrating the frequency keeps the phase
    continuous, so sweeps do not click."""
    phase = np.cumsum(freq) / SR
    return np.where((phase % 1.0) < duty, 1.0, -1.0)


def triangle(freq):
    phase = np.cumsum(freq) / SR
    return 2.0 * np.abs(2.0 * (phase % 1.0) - 1.0) - 1.0


def sweep(f0, f1, dur):
    return np.linspace(f0, f1, int(SR * dur))


def decay(n, power=2.0):
    return (1.0 - np.linspace(0.0, 1.0, n)) ** power


def note(freq, dur, duty=0.5, release=0.6):
    n = int(SR * dur)
    return pulse(np.full(n, freq), duty) * decay(n, release * 3)


def silence(dur):
    return np.zeros(int(SR * dur))


# =============================== EFFECTS ===============================
def gem_collect():
    f = sweep(660, 1320, 0.11)                       # quick rising blip
    return pulse(f, 0.5) * decay(len(f), 1.5)


def win():
    notes = [523.25, 659.25, 783.99, 1046.50]        # C5 E5 G5 C6 arpeggio
    parts = [note(n, 0.11, 0.25) for n in notes[:-1]]
    parts.append(note(notes[-1], 0.38, 0.25, release=0.9))
    return np.concatenate(parts)


def lose():
    f = sweep(440, 110, 0.9)                         # falling tone with a slow wobble
    f = f * (1.0 + 0.03 * np.sin(np.arange(len(f)) / SR * 2 * np.pi * 7))
    return pulse(f, 0.25) * decay(len(f), 1.2)


def restart():
    f = sweep(900, 700, 0.05)                        # short soft click
    return triangle(f) * decay(len(f), 1.0)


EFFECTS = {"gem_collect": gem_collect, "win": win, "lose": lose, "restart": restart}


# =============================== EXPORT ===============================
def finish(x):
    x = x.astype(np.float64)
    fade = int(SR * FADE_MS / 1000)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    return x / np.max(np.abs(x)) * PEAK


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def read_wav(path):
    with wave.open(path, "rb") as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype="<i2") / 32767.0
    return ch, width, rate, data


def main():
    out = os.environ.get("OUT_DIR", "output")
    os.makedirs(out, exist_ok=True)
    print(f"Wrote {len(EFFECTS)} effects to {out}")
    for name, fn in EFFECTS.items():
        path = f"{out}/{name}.wav"
        write_wav(path, finish(fn()))
        ch, width, rate, data = read_wav(path)             # check what was really written
        peak = float(np.max(np.abs(data)))
        rms = float(np.sqrt(np.mean(data ** 2)))
        dur = len(data) / rate
        ok = (ch == 1 and width == 2 and rate == SR and peak <= PEAK + 0.01
              and abs(data[0]) < 0.02 and abs(data[-1]) < 0.02)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}.wav  {dur:.2f}s  peak {peak:.2f}  rms {rms:.2f}")


if __name__ == "__main__":
    main()
