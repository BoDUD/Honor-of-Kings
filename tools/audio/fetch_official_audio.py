"""Rebuild the official Honor of Kings voice clips used by the mod (they are not committed).

    python tools/audio/fetch_official_audio.py

Downloads Arthur's default-skin skill voice lines from the official site (game.gtimg.cn, listed in
https://pvp.qq.com/zlkdatasys/yuzhouzhan/herovoice/166.json), trims silence, normalises to -2 dBFS
and writes mono 16-bit WAVs into hok/sound/sfx/. Audio (c) Tencent; for a non-commercial fan mod.
"""
import io
import os
import sys
import urllib.request
import wave

import numpy as np

BASE = "https://game.gtimg.cn/images/yxzj/zlkdatasys/audios/audio/20220412/"
CLIPS = {
    "hok_arthur_vo_skill": "16497670561695.wav",   # skill 1 voice line
    "hok_arthur_vo_skill2": "16497670979654.wav",  # skill 2 voice line
    "hok_arthur_vo_ult": "16497671229903.wav",     # ultimate voice line
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hok", "sound", "sfx")


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def process(raw):
    w = wave.open(io.BytesIO(raw))
    sr, ch = w.getframerate(), w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).mean(axis=1).astype(np.float32)
    idx = np.where(np.abs(x) > np.max(np.abs(x)) * 0.02)[0]
    y = x[max(0, idx[0] - int(0.01 * sr)): min(len(x), idx[-1] + int(0.06 * sr))]
    y = y / np.max(np.abs(y)) * 32767 * 0.79
    n = int(0.015 * sr)
    y[-n:] *= np.linspace(1, 0, n)
    return sr, y.astype(np.int16).tobytes()


def main():
    os.makedirs(lp(OUT), exist_ok=True)
    for name, src in CLIPS.items():
        with urllib.request.urlopen(BASE + src, timeout=30) as r:
            sr, pcm = process(r.read())
        with wave.open(lp(os.path.join(OUT, name + ".wav")), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(sr)
            out.writeframes(pcm)
        print("wrote", name)


if __name__ == "__main__":
    sys.exit(main())
