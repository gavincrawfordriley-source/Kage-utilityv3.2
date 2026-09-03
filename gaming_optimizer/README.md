# Kage Utility 影

**Move like a shadow.** 53 real Windows 11 gaming tweaks in a dark, purple-accented desktop app. Fully reversible. Free tier + premium tier gated by your secret code.

---

## 🔑 Your codes (keep private)

| Code | Purpose |
|------|---------|
| `FRAG42` | **Premium unlock** — anyone with it unlocks all 53 tweaks on their PC |
| `2006james` | **Owner override** — your master key. On any PC it toggles between revoking premium and re-enabling it, and reveals the hidden Owner Console tab. |

You can rotate the secret code at runtime via **⚙ Settings → 👑 Owner** without recompiling.

---

## ✨ What's inside

### 53 tweaks in 11 categories
- **CPU & Power** (5, 🔒) — Ultimate Power Plan, Core Parking, CPU Throttling, USB Suspend, PCIe LPM
- **Network** (5, 🔒) — Nagle, Cloudflare DNS, Throttling Index, TCP Buffers, QoS Reserve
- **GPU / DirectX** (3, 🔒) — HP GPU Global, HwSchMode + TDR, Games High Priority
- **Input** (4, 🔒) — Mouse Accel, Sticky Keys, Keyboard Delay, HID Priority
- **System** (4, 🔒) — Foreground CPU Boost, Fullscreen Notif Block, Focus Assist Off, Sys Responsiveness
- **Gaming** (6) — Xbox Game Bar off, Game DVR off, Game Mode on, HAGS, Auto HDR, no FSO
- **Visuals** (5) — Best Perf FX, no Animations, no Transparency, no Cursor Shadow, 0 Menu Delay
- **Startup** (7) — Startup Apps, Telemetry Tasks, Cortana, Search Index, SysMain, Widgets, BG Apps
- **Disk** (7) — Temp Clean, WU Cache, DNS Flush, Hibernation, Pagefile, NTFS atime, TRIM
- **Privacy** (5) — Telemetry, Ad ID, Activity History, Location, Feedback
- **Audio** (2) — Enhancements, Higher DPC Priority

### Extras
- 🎨 **6 themes** — Kage Purple (default), Neon Green, Cyberpunk Pink, Arctic Blue, Solar Orange, Void Purple
- 📋 **4 built-in profiles** — Competitive FPS, AAA Cinematic, Streaming Setup, Minimal / Safe. Save your own.
- 📊 **Benchmark tab** — live snapshot with Optimization Score %
- 👑 **Owner Console** — rotate secret code, revoke/re-enable premium per PC
- ⌫ **Undo Last** — single-step revert of the most recent applied tweak
- 🌐 **Auto-update check** — silently pings a GitHub releases URL on launch (set `RELEASES_URL` in `updater.py`)

---

## 🖥 Running from source

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

Auto-generates the custom purple K icon, then packages into:

```
dist\KageUtility.exe
```

Single file, ~30 MB, includes the icon, auto-requests admin on launch.
Send it to friends. They double-click and go.

---

## 🛡 Safety

- Every registry / powercfg value backed up **before** mutation → `%APPDATA%\GamingOptimizer\backup.json`
- **Undo Last** for one-step revert; **Restore All** for full rollback
- No telemetry, only outbound call is the (optional) GitHub update check
- Non-Windows platforms: warned once, tweaks silently no-op

---

*Kage (影) — Japanese for "shadow". Optimizes silently.*
