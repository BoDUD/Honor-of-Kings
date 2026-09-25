"""Rebuild Arthur's six combat SFX from a gameplay recording (they are not committed).

    ffmpeg -i arthur_recording.mp4 -vn -ac 1 -ar 44100 rec.wav
    python tools/audio/cut_recording_sfx.py rec.wav

The clips were cut from a 2:28 Honor of Kings gameplay recording of Arthur with the music
turned off. The cut points below were picked by cross-correlating the official voice lines
(skills) and checking video frames (ult), then taking the cleanest instance of each sound.
Audio (c) Tencent; for a non-commercial fan mod.
"""
import os
import sys
import wave

import numpy as np

CUTS = {  # clip name: (start s, end s) in the recording
    "hok_arthur_sfx_attack": (59.40, 59.85),
    "hok_arthur_sfx_skill_cast": (118.56, 118.80),
    "hok_arthur_sfx_skill_hit": (119.30, 119.90),
    "hok_arthur_sfx_skill2": (44.70, 45.20),
    "hok_arthur_sfx_ult_cast": (130.38, 130.76),
    "hok_arthur_sfx_ult_hit": (130.76, 131.76),
}
PEAK_DBFS = -3.0
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hok", "sound", "sfx")


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    w = wave.open(sys.argv[1])
    sr, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
    if width != 2:
        sys.exit("expected 16-bit PCM wav")
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).mean(axis=1).astype(np.float32)
    os.makedirs(lp(OUT), exist_ok=True)
    for name, (a, b) in CUTS.items():
        y = x[int(a * sr):int(b * sr)].copy()
        y *= (10 ** (PEAK_DBFS / 20) * 32767) / max(1.0, float(np.abs(y).max()))
        fi, fo = int(0.004 * sr), int(0.03 * sr)
        y[:fi] *= np.linspace(0, 1, fi)
        y[-fo:] *= np.linspace(1, 0, fo)
        with wave.open(lp(os.path.join(OUT, name + ".wav")), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(sr)
            out.writeframes(y.astype(np.int16).tobytes())
        print("wrote", name, f"{b - a:.2f}s")


if __name__ == "__main__":
    main()
