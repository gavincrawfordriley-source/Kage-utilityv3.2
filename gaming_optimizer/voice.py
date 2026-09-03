"""
Voice Line Pack — synthesises a whispered "Kage engaged" line using pyttsx3
(Windows SAPI). Falls back to the existing whoosh WAV if pyttsx3 isn't
installed or synthesis fails.
"""
import os
import threading

VOICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice.wav")
WHOOSH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whoosh.wav")

VOICE_LINE = "Kage engaged."


def _synthesize():
    """Generate voice.wav once. Returns True on success."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Whisper-ish: slower rate, softer volume
        engine.setProperty("rate", 135)
        engine.setProperty("volume", 0.85)
        # Prefer a lower / male voice if available
        voices = engine.getProperty("voices")
        for v in voices:
            n = (v.name or "").lower()
            if "david" in n or "mark" in n or "male" in n:
                engine.setProperty("voice", v.id)
                break
        engine.save_to_file(VOICE_LINE, VOICE_PATH)
        engine.runAndWait()
        return os.path.exists(VOICE_PATH) and os.path.getsize(VOICE_PATH) > 0
    except Exception:
        return False


def ensure_voice():
    if not os.path.exists(VOICE_PATH):
        ok = _synthesize()
        # Fallback: if TTS unavailable, copy whoosh so voice.wav always exists
        if not ok and os.path.exists(WHOOSH_PATH):
            try:
                import shutil
                shutil.copyfile(WHOOSH_PATH, VOICE_PATH)
            except Exception:
                pass


def play_intro():
    """Play the voice line async; fall back to whoosh if unavailable."""
    if os.name != "nt":
        return
    ensure_voice()
    path = VOICE_PATH if os.path.exists(VOICE_PATH) else WHOOSH_PATH
    if not os.path.exists(path):
        return

    def _play():
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()
