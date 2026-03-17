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
from AppKit import (NSAppearance, NSAppearanceNameDarkAqua, NSApplication,
                    NSAttributedString, NSForegroundColorAttributeName, NSColor)

# Hide from Dock and App Switcher — must run before anything else
NSApplication.sharedApplication().setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PT  = pytz.timezone("America/Los_Angeles")
WIB = pytz.timezone("Asia/Jakarta")  # GMT+7

# Frames live next to the script (works both locally and in ~/.claude2x)
FRAMES_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
FRAME_COUNT = 24
ANIM_FPS    = 0.05  # seconds per frame (~20fps)

PLIST_LABEL = "com.claude2x.app"
PLIST_PATH  = os.path.expanduser(f"~/Library/LaunchAgents/{PLIST_LABEL}.plist")
SCRIPT_PATH = os.path.abspath(__file__)
PYTHON_BIN  = "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"


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
            line1 = "You're on double limits"
            line2 = "All weekend — resets Monday"
        else:
            peak_pt = (now_pt.replace(hour=5, minute=0, second=0, microsecond=0)
                       if hour < 5 else
                       (now_pt + timedelta(days=1)).replace(
                           hour=5, minute=0, second=0, microsecond=0))
            mins_until = int((peak_pt - now_pt).total_seconds() // 60)
            line1 = "You're on double limits"
            line2 = f"Until {pt_to_wib_str(peak_pt)}  ·  {mins_to_str(mins_until)} left"
    else:
        title = "1x"
        resume_pt  = now_pt.replace(hour=11, minute=0, second=0, microsecond=0)
        mins_until = int((resume_pt - now_pt).total_seconds() // 60)
        line1 = "Standard limits now"
        line2 = f"2× at {pt_to_wib_str(resume_pt)}  ·  in {mins_to_str(mins_until)}"

    return dict(title=title, line1=line1, line2=line2)


def _white_attr(text):
    """White attributed string — keeps text bright on dark menu even when item is disabled."""
    return NSAttributedString.alloc().initWithString_attributes_(
        text, {NSForegroundColorAttributeName: NSColor.whiteColor()}
    )


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

        # Info items have no callback → disabled by AppKit (no hover highlight).
        # White attributed titles are applied in _setup_appearance once the menu exists.
        self.menu = [
            rumps.MenuItem("line1"),
            rumps.MenuItem("line2"),
            rumps.separator,
            rumps.MenuItem("sched_header"),
            rumps.MenuItem("sched_1"),
            rumps.MenuItem("sched_2"),
            rumps.separator,
            rumps.MenuItem("Start at Login", callback=self.toggle_login),
            rumps.separator,
        ]

        # Set static schedule copy
        self.menu["sched_header"].title = "2× is active:"
        self.menu["sched_1"].title      = "  •  Mon–Fri   7 PM – 1 AM WIB"
        self.menu["sched_2"].title      = "  •  Sat–Sun   All day"

        self.menu["Start at Login"].state = is_login_enabled()
        self.update_status()

    @rumps.timer(0.5)
    def _setup_appearance(self, sender):
        try:
            dark = NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
            self._nsapp.nsstatusitem.menu().setAppearance_(dark)

            # Disable all info items (removes hover highlight) and force white text
            for key in ["line1", "line2", "sched_header", "sched_1", "sched_2"]:
                item    = self.menu[key]
                ns_item = item._menuitem
                ns_item.setEnabled_(False)
                ns_item.setAttributedTitle_(_white_attr(item.title))

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
        self.title = content["title"]

        for key in ["line1", "line2"]:
            item    = self.menu[key]
            item.title = content[key]
            # Keep attributed title in sync so white color persists after refresh
            try:
                item._menuitem.setAttributedTitle_(_white_attr(item.title))
            except Exception:
                pass


if __name__ == "__main__":
    Claude2xApp().run()
