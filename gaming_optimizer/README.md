# FragBoost — Windows 11 Gaming Optimizer

53 real, reversible Windows 11 gaming tweaks in one dark-themed desktop app.
Free tier ships 32 tweaks; premium tier unlocks all 53 with your secret code.

---

## 🔑 Your codes (keep these private!)

| Code | Purpose |
|------|---------|
| `FRAG42` | **Premium unlock** — anyone with this code unlocks all 53 tweaks on their PC |
| `2006james` | **Owner override** — YOUR master key. Entering it on any PC toggles between: revoking that PC's premium access, OR restoring it. |

**How the owner code works in practice:**
1. Friend types `FRAG42` on their PC → premium unlocked for them.
2. They share it with someone you don't like.
3. You visit that PC (or send them a build), type `2006james` in the unlock dialog → their premium access is REVOKED. `FRAG42` will no longer work on that machine until you re-enter `2006james` on it.

Codes are set in `licensing.py` at the top — edit that file to rotate them.

---

## 🧩 Tweak catalogue (53 total)

### 🔒 Premium (need `FRAG42`) — 21 tweaks
- **CPU & Power (5):** Ultimate Power Plan, Disable Core Parking, Disable CPU Throttling, Disable USB Selective Suspend, Disable PCIe Link Power Mgmt
- **Network (5):** Disable Nagle's Algorithm, Cloudflare DNS, Disable Network Throttling, Increase Network Buffers, Disable QoS Reservation
- **GPU / DirectX (3):** Prefer HP GPU Globally, GPU Prefer Max Perf, Games Launch at High Priority
- **Input (4):** Disable Mouse Accel, Disable Sticky/Filter/Toggle Keys, Reduce Keyboard Delay, HID Priority Boost
- **System (4):** Foreground Priority Boost, No Notifs in Fullscreen, Disable Focus Assist Auto, Boost System Responsiveness

### 🆓 Free — 32 tweaks
- **Gaming (6):** Disable Xbox Game Bar, Disable Game DVR, Enable Game Mode, HAGS, Auto HDR, Disable FSO Globally
- **Visuals (5):** Best Performance mode, Disable Window Animations, Disable Transparency, Cursor Shadow, Zero Menu Delay
- **Startup (7):** Disable Startup Apps, Disable Telemetry Tasks, Disable Cortana, Disable Search Indexing, Disable SysMain, Disable Widgets, Disable Background Apps
- **Disk (7):** Clean Temp Files, Clear WU Cache, Flush DNS, Disable Hibernation, Pagefile only on C:, Disable NTFS atime, Enable TRIM
- **Privacy (5):** Disable Telemetry, Advertising ID, Activity History, Location, Feedback Prompts
- **Audio (2):** Disable Audio Enhancements, Boost Audio DPC Priority

Every tweak stores its original value in `%APPDATA%\GamingOptimizer\backup.json` before writing.

---

## 🖥 Running from source (development)

```bat
pip install -r requirements.txt
python main.py
```

Right-click → **Run as administrator** for full functionality.

---

## 📦 Building the shareable `.exe`

On any Windows 11 PC with Python 3.10+:

```bat
build.bat
```

Result: `dist\FragBoost.exe` — one portable file (~25 MB, self-contained).
It auto-requests UAC elevation via the `--uac-admin` PyInstaller flag.

Send that one file to friends. They double-click, tweak, done.

---

## 🛡 Safety guarantees

- Every registry / powercfg value backed up **before** mutation
- Restore All returns everything to the exact prior value
- No telemetry, no network calls (except when you enable Cloudflare DNS)
- Temp cleanup only touches files Windows itself considers disposable
