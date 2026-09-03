"""
Synthesises a soft shuriken 'whoosh' WAV on first import (no external assets).
Uses only the stdlib. Plays on splash via winsound (Windows) or noop elsewhere.
"""
import os
import wave
import math
import struct
import threading

SFX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whoosh.wav")


def _generate():
    """Filtered-noise sweep — resembles a fast air cut."""
    sr = 22050
    dur = 0.55
    n = int(sr * dur)
    frames = bytearray()
    prev = 0.0
    import random
    random.seed(0xCAFE)
    for i in range(n):
        t = i / n  # 0..1
        # amplitude envelope: quick attack, long decay
        env = (t ** 0.35) * ((1 - t) ** 2.2) * 4.0
        # noise + slight low-freq wobble for 'wind' feel
        noise = random.uniform(-1.0, 1.0)
        # simple 1-pole lowpass
        prev = prev * 0.82 + noise * 0.18
        wobble = math.sin(2 * math.pi * (280 + 400 * t) * (i / sr)) * 0.15
        sample = max(-1.0, min(1.0, (prev + wobble) * env * 0.6))
        frames += struct.pack("<h", int(sample * 32767))
    with wave.open(SFX_PATH, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(frames))


def ensure_sfx():
    if not os.path.exists(SFX_PATH):
        try:
            _generate()
        except Exception:
            pass


def play_splash_sound():
    """Fire-and-forget. Windows: winsound. Elsewhere: no-op."""
    ensure_sfx()
    if os.name != "nt" or not os.path.exists(SFX_PATH):
        return

    def _play():
        try:
            import winsound
            winsound.PlaySound(SFX_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()
