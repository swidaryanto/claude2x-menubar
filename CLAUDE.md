# CLAUDE.md — Source of Truth for claude2x-menubar

This file is read automatically by Claude Code at the start of every session.
It contains all the hard-won knowledge about this project — architecture, bugs, and decisions.

---

## What this project is

A macOS menubar app that shows whether Claude Pro's 2x usage period is currently active.
Distributed via Homebrew Formula (not Cask, not .app bundle — see why below).
**Final release. No new features or bug fixes planned.**

---

## Repo layout

```
claude2x.py          # Main app — the only file that matters for logic
frames/              # 24 PNG frames for the animated menubar icon
README.md            # User-facing docs
CLAUDE.md            # This file
/tmp/homebrew-tap/   # Separate repo: homebrew-tap (Formula + Cask)
```

Homebrew tap repo lives at `/tmp/homebrew-tap` (also `/private/tmp/homebrew-tap`).
Formula: `/tmp/homebrew-tap/Formula/claude2x.rb`
Cask: `/tmp/homebrew-tap/Casks/claude2x.rb` (unused — see distribution section)

---

## Architecture

**Stack:** Python 3 + rumps + PyObjC + AppKit/Foundation

**Key dependencies (bundled by Homebrew into libexec/lib):**
- `rumps` — menubar framework
- `pytz` — timezone handling

**PyObjC** comes from the system (CommandLineTools Python 3.9), version 12.1.

**Runtime path:** The service runs via a brew wrapper script:
```bash
export PYTHONPATH="/opt/homebrew/Cellar/claude2x/<version>/libexec/lib:$PYTHONPATH"
exec python3 "/opt/homebrew/Cellar/claude2x/<version>/libexec/claude2x.py"
```

**Installed path:** `/opt/homebrew/Cellar/claude2x/<version>/libexec/claude2x.py`

**Logs:** `/opt/homebrew/var/log/claude2x.log`

---

## How to hot-swap during development (no version bump needed)

```bash
brew services stop swidaryanto/tap/claude2x
cp claude2x.py /opt/homebrew/Cellar/claude2x/2.2.0/libexec/claude2x.py
brew services start swidaryanto/tap/claude2x
sleep 4
tail -20 /opt/homebrew/var/log/claude2x.log
```

Check the log line count before and after — if it doesn't grow, no Python exceptions.

---

## Animation — the full story

The icon animates through 24 pre-loaded PNG frames at 20fps (~0.05s per frame).
All frames are loaded as `NSImage` objects at startup — no file I/O per tick.

**Working implementation (current):**
```python
from Foundation import NSTimer, NSDate, NSRunLoop, NSRunLoopCommonModes

timer = NSTimer.alloc().initWithFireDate_interval_repeats_block_(
    NSDate.date(), ANIM_FPS, True, lambda _t: self._tick()
)
NSRunLoop.mainRunLoop().addTimer_forMode_(timer, NSRunLoopCommonModes)
self._anim_timer = timer
```

`_tick()` calls `self._status_btn.setImage_(self._frame_images[self._frame_index])` directly.
Fires on the **main thread**. Works while menu is open because of `NSRunLoopCommonModes`.

**The root cause of all previous animation failures:**
`NSRunLoopCommonModes` was passed as a raw string `"NSRunLoopCommonModes"`.
The actual constant value is `'kCFRunLoopCommonModes'`.
Using the string causes the timer to silently never fire.
**Always import `NSRunLoopCommonModes` from Foundation. Never use the string.**

**Approaches that do NOT work (do not retry these):**
| Approach | Why it fails |
|---|---|
| `@rumps.timer(ANIM_FPS)` | Pauses when menu is open (NSDefaultRunLoopMode only) |
| NSTimer + `"NSRunLoopCommonModes"` string | Wrong constant — timer never fires |
| Background thread + `self.icon = path` | NSInternalInconsistencyException (AppKit not thread-safe) |
| `objc.selector` as class attribute on NSObject | Corrupts PyObjC class registration |
| `performSelector:withObject:afterDelay:inModes:` with `["NSRunLoopCommonModes"]` | Same wrong string issue |
| NSTimer block with `"NSRunLoopCommonModes"` string | Same wrong string issue |

**Thread approach (works but laggy — avoid):**
```python
btn.performSelectorOnMainThread_withObject_waitUntilDone_modes_(
    "setImage:", img, False,
    ["NSDefaultRunLoopMode", "NSEventTrackingRunLoopMode"]
)
```
This works but `time.sleep` drift causes visible stutter. The NSTimer+block approach is preferred.

---

## Menu appearance

- Menu is forced dark: `ns_menu.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua))`
- Info rows (line1, line2, sched_header, sched_1, sched_2) use custom `NSView`/`NSTextField` views
  to display white text without hover highlight and without system disabled-dimming
- `setEnabled_(False)` on the NSMenuItem removes hover, but dims text — the custom view bypasses this
- Only "Start at Login" and "Quit" are interactive/hoverable
- Appearance is applied in `_setup_appearance`, a one-shot `@rumps.timer(0.5)` that fires after the
  app's NSStatusItem is fully initialized

---

## 2x schedule logic

```
Pacific Time (PT):
- Weekdays Mon–Fri: 2x OUTSIDE 5am–11am PT → i.e., 11am–5am PT next day
- Weekends Sat–Sun: 2x ALL DAY

WIB (GMT+7, Asia/Jakarta):
- Mon–Fri: 1:00 AM – 7:00 PM WIB
- Sat–Sun: All day
```

All times displayed to user are in **WIB**. The `get_status()` function computes in PT.

---

## Distribution

**Homebrew Formula** (not Cask) is used to avoid Gatekeeper on macOS Sequoia.
A Cask requires a signed .app bundle. The Formula installs a Python script directly — no signing needed.

**Formula path:** `/tmp/homebrew-tap/Formula/claude2x.rb`
**Tap repo:** `https://github.com/swidaryanto/homebrew-tap`
**App repo:** `https://github.com/swidaryanto/claude2x-menubar`

To release a new version:
1. Create a source tarball: `git archive --format=tar.gz --prefix=claude2x-2.x.x/ HEAD > claude2x-source-2.x.x.tar.gz`
2. Upload to GitHub Releases
3. Get the SHA256: `shasum -a 256 claude2x-source-2.x.x.tar.gz`
4. Update `Formula/claude2x.rb` with new url, sha256, version
5. Push the tap repo

---

## Login item

Toggle via the "Start at Login" menu item. Uses a LaunchAgent plist at:
`~/Library/LaunchAgents/com.claude2x.app.plist`

The `brew services start` approach is the recommended way to run it — it manages its own plist.

---

## PyObjC gotchas (hard-won)

- `NSRunLoopCommonModes` must be **imported from Foundation**, never passed as a string
- `objc.python_method` decorator is needed for Python-only helper methods on NSObject subclasses (methods not meant to be ObjC-callable)
- NSObject subclass methods WITHOUT `@objc.python_method` are auto-registered as ObjC methods
- `alloc().init()` on an NSObject subclass can fail silently if the class is corrupted (e.g., by misusing `objc.selector`)
- AppKit UI updates (setImage:, etc.) MUST happen on the main thread
- PyObjC 12.1 supports Python callables as ObjC blocks — `initWithFireDate_interval_repeats_block_` works

---

## Copy/tone

All UI copy follows GoJek Senior UX Writer style: clear, direct, warm, no jargon.
Times always in WIB. Bullet separator between schedule label and time range: `·`
