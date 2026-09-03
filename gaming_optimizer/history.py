"""Undo history — remembers the last N applied tweaks so users can single-step revert."""
from collections import deque

_HISTORY = deque(maxlen=50)


def record(tweak):
    """Called after a tweak is successfully applied."""
    _HISTORY.append(tweak)


def drop(tweak_id):
    """Called when a tweak is turned off manually — remove it from history."""
    for t in list(_HISTORY):
        if t["id"] == tweak_id:
            try:
                _HISTORY.remove(t)
            except ValueError:
                pass


def has_undo() -> bool:
    return len(_HISTORY) > 0


def peek():
    return _HISTORY[-1] if _HISTORY else None


def pop():
    """Returns the most recent tweak and removes it from history."""
    return _HISTORY.pop() if _HISTORY else None


def clear():
    _HISTORY.clear()
