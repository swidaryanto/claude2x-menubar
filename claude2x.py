#!/usr/bin/env python3
"""
Claude 2x Usage Menubar App
Shows whether you're in a 2x Claude Pro usage period.

2x periods:
- Weekdays: outside 5–11am PT (UTC-7/UTC-8)
- Weekends: all day
"""

import os
import plistlib
import rumps
from datetime import datetime, timedelta
import pytz
from AppKit import NSAppearance, NSAppearanceNameDarkAqua

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PT  = pytz.timezone("America/Los_Angeles")
WIB = pytz.timezone("Asia/Jakarta")  # GMT+7

FRAMES_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
FRAME_COUNT = 24
ANIM_FPS    = 0.05  # seconds per frame (~20fps)

PLIST_LABEL = "com.claude2x.app"
PLIST_PATH  = os.path.expanduser(f"~/Library/LaunchAgents/{PLIST_LABEL}.plist")
SCRIPT_PATH = os.path.abspath(__file__)
PYTHON_BIN  = "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"

EXPIRES_WIB = WIB.localize(datetime(2026, 3, 29, 23, 59, 59))


# ---------------------------------------------------------------------------
# Login item helpers
# ---------------------------------------------------------------------------

def is_login_enabled() -> bool:
    return os.path.exists(PLIST_PATH)


def enable_login():
    plist = {
        "Label": PLIST_LABEL,
        "ProgramArguments": [PYTHON_BIN, SCRIPT_PATH],
        "RunAtLoad": True,
        "KeepAlive": False,
    }
    os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)


def disable_login():
    if os.path.exists(PLIST_PATH):
        os.remove(PLIST_PATH)


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_status():
    now_pt  = datetime.now(PT)
    weekday = now_pt.weekday()
    hour    = now_pt.hour
    if weekday >= 5:
        return True, now_pt
    return (5 <= hour < 11) is False, now_pt


def mins_to_str(total_mins):
    hrs, mins = divmod(abs(int(total_mins)), 60)
    return f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"


def pt_to_wib_str(pt_dt):
    return pt_dt.astimezone(WIB).strftime("%-I:%M %p WIB")


def build_menu_content(is_2x, now_pt):
    weekday    = now_pt.weekday()
    hour       = now_pt.hour
    is_weekend = weekday >= 5

    if is_2x:
        title = "2x"
        if is_weekend:
            line1 = "●  Double limits active"
            line2 = "All weekend — no reset until Monday"
        else:
            peak_pt = (now_pt.replace(hour=5, minute=0, second=0, microsecond=0)
                       if hour < 5 else
                       (now_pt + timedelta(days=1)).replace(
                           hour=5, minute=0, second=0, microsecond=0))
            mins_until = int((peak_pt - now_pt).total_seconds() // 60)
            line1 = "●  Double limits active"
            line2 = f"↻  Resets in {mins_to_str(mins_until)} — at {pt_to_wib_str(peak_pt)}"
    else:
        title = "1x"
        resume_pt  = now_pt.replace(hour=11, minute=0, second=0, microsecond=0)
        mins_until = int((resume_pt - now_pt).total_seconds() // 60)
        line1 = "○  Normal limits right now"
        line2 = f"↻  Double limits in {mins_to_str(mins_until)} — at {pt_to_wib_str(resume_pt)}"

    return dict(title=title, line1=line1, line2=line2)


def build_expires_line(now_pt):
    delta = EXPIRES_WIB - now_pt.astimezone(WIB)
    days  = delta.days
    if delta.total_seconds() <= 0:
        return "◆  This benefit has ended (Mar 29)"
    elif days == 0:
        return "◆  Ends today — make the most of it"
    elif days == 1:
        return "◆  Ends tomorrow, Mar 29"
    elif days <= 5:
        return f"◆  Ends Mar 29  ·  {days} days left"
    else:
        return f"◆  Ends Mar 29, 2026  ·  {days} days left"


def noop(_): pass


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class Claude2xApp(rumps.App):
    def __init__(self):
        frames = [os.path.join(FRAMES_DIR, f"frame_{i:03d}.png")
                  for i in range(FRAME_COUNT)]
        super().__init__("1x", icon=frames[0], template=True, quit_button="Quit")

        self._frames      = frames
        self._frame_index = 0

        self.menu = [
            rumps.MenuItem("line1", callback=noop),
            rumps.MenuItem("line2", callback=noop),
            rumps.separator,
            rumps.MenuItem("When you get double limits:", callback=noop),
            rumps.MenuItem("  • Weeknights  7pm – 1am WIB", callback=noop),
            rumps.MenuItem("  • All weekend, all day", callback=noop),
            rumps.separator,
            rumps.MenuItem("expires_line", callback=noop),
            rumps.separator,
            rumps.MenuItem("Start at Login", callback=self.toggle_login),
            rumps.separator,
        ]
        self.menu["Start at Login"].state = is_login_enabled()
        self.update_status()

    @rumps.timer(0.5)
    def _setup_appearance(self, sender):
        try:
            dark = NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
            self._nsapp.nsstatusitem.menu().setAppearance_(dark)
            sender.stop()
        except Exception:
            pass

    @rumps.timer(ANIM_FPS)
    def animate(self, _):
        self._frame_index = (self._frame_index + 1) % len(self._frames)
        self.icon = self._frames[self._frame_index]

    @rumps.timer(30)
    def refresh(self, _):
        self.update_status()

    def toggle_login(self, sender):
        if sender.state:
            disable_login()
        else:
            enable_login()
        sender.state = not sender.state

    def update_status(self):
        is_2x, now_pt = get_status()
        content = build_menu_content(is_2x, now_pt)
        self.title                   = content["title"]
        self.menu["line1"].title     = content["line1"]
        self.menu["line2"].title     = content["line2"]
        self.menu["expires_line"].title = build_expires_line(now_pt)


if __name__ == "__main__":
    Claude2xApp().run()
