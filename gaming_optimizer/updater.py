"""
GitHub release checker. Non-blocking, silently no-ops on failure.

Set RELEASES_URL to your public GitHub repo's releases-latest API endpoint
once you publish the project. Until then it's a stub that returns None.
"""
import json
import threading
import urllib.request
from packaging.version import Version, InvalidVersion

APP_VERSION = "1.2"

# Point this at your repo when you publish:
# e.g. "https://api.github.com/repos/jamesjames/kage-utility/releases/latest"
RELEASES_URL = ""

TIMEOUT = 4  # seconds — never block the UI


def _fetch_latest():
    if not RELEASES_URL:
        return None
    try:
        req = urllib.request.Request(
            RELEASES_URL,
            headers={"User-Agent": "KageUtility"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
        tag = (data.get("tag_name") or "").lstrip("vV").strip()
        url = data.get("html_url", "")
        notes = (data.get("body") or "").strip()[:400]
        if not tag:
            return None
        return {"version": tag, "url": url, "notes": notes}
    except Exception:
        return None


def _is_newer(remote: str, local: str) -> bool:
    try:
        return Version(remote) > Version(local)
    except InvalidVersion:
        return remote != local


def check_async(callback):
    """
    Runs fetch in a daemon thread. Calls callback(update_dict) on the main
    thread ONLY if a newer version exists. update_dict = {version,url,notes}.
    """
    def worker():
        info = _fetch_latest()
        if info and _is_newer(info["version"], APP_VERSION):
            callback(info)

    threading.Thread(target=worker, daemon=True).start()
