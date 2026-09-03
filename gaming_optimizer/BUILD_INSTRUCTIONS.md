# How to Build KageUtility.exe

You do this **once** on any Windows 10 or 11 PC. After it finishes you'll have a single `KageUtility.exe` file you can send to friends.

---

## Step 1 — Install Python (one-time, ~3 min)

If you don't already have Python 3.10+:

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **Download Python 3.12.x** button
3. Run the installer
4. ⚠️ **IMPORTANT:** on the first screen, tick the box that says
   **"Add python.exe to PATH"** at the bottom
5. Click **Install Now** → wait ~1 minute → Close

Verify it worked: open Command Prompt (press `Win + R`, type `cmd`, Enter) and type:
```
python --version
```
You should see something like `Python 3.12.5`.

---

## Step 2 — Copy the Kage source folder to your PC

Put the whole `gaming_optimizer` folder anywhere you like — Desktop is fine.
Example: `C:\Users\James\Desktop\gaming_optimizer\`

---

## Step 3 — Run the build

1. Open the `gaming_optimizer` folder in File Explorer
2. **Double-click `build.bat`**
3. A black terminal window opens and does its thing (installing libraries, generating the icon, packaging the EXE). Takes about 2 minutes.
4. When it says **"Done!"** press any key to close it

Your finished file is at:
```
gaming_optimizer\dist\KageUtility.exe
```

That's your app. Drag it to your Desktop, upload it to Discord, email it — it's a single self-contained file (~35 MB) that runs on any Windows 10 or 11 PC without Python installed.

---

## Rebuilding after code changes

If you ever tweak the source, just double-click `build.bat` again. It overwrites the old EXE.

---

## Troubleshooting

**"python is not recognized"**
→ You forgot to tick the "Add to PATH" box in Step 1. Reinstall Python and tick it.

**"pip install" errors**
→ Right-click `build.bat` → "Run as administrator".

**Antivirus blocks the EXE**
→ Some AVs flag PyInstaller-built files. Add `KageUtility.exe` to your AV's exclusions, or tell your friend to.

**Windows SmartScreen blue warning on first run**
→ Totally normal for indie apps. Tell your friend:
   *"Click **More info** then **Run anyway**"* — one time, then Windows remembers.
