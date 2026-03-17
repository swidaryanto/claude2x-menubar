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
                    NSView, NSTextField, NSFont, NSColor, NSImage)
from Foundation import NSTimer, NSDate, NSRunLoop, NSRunLoopCommonModes

# Hide from Dock and App Switcher — must run before anything else
NSApplication.sharedApplication().setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory

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

INFO_KEYS   = ["line1", "line2", "sched_header", "sched_1", "sched_2"]


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


def noop(_): pass


# ---------------------------------------------------------------------------
# Custom label view
# Renders white text independently of NSMenuItem's enabled/disabled state.
# setEnabled_(False) prevents hover; custom view bypasses disabled dimming.
# ---------------------------------------------------------------------------

def _make_label_view(text):
    """Return (NSView container, NSTextField label) for a non-interactive menu row."""
    outer = NSView.alloc().initWithFrame_(((0, 0), (300, 20)))
    label = NSTextField.alloc().initWithFrame_(((20, 3), (272, 15)))
    label.setStringValue_(text)
    label.setEditable_(False)
    label.setSelectable_(False)
    label.setBezeled_(False)
    label.setDrawsBackground_(False)
    label.setTextColor_(NSColor.whiteColor())
    label.setFont_(NSFont.menuFontOfSize_(13.0))
    outer.addSubview_(label)
    return outer, label


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class Claude2xApp(rumps.App):
    def __init__(self):
        frame_paths = [os.path.join(FRAMES_DIR, f"frame_{i:03d}.png")
                       for i in range(FRAME_COUNT)]

        super().__init__("1x", icon=frame_paths[0], template=True, quit_button="Quit")

        self._frame_index = 0

        # Pre-load all frames as NSImage objects — zero file I/O per animation tick
        self._frame_images = []
        for path in frame_paths:
            img = NSImage.alloc().initWithContentsOfFile_(path)
            img.setTemplate_(True)
            self._frame_images.append(img)

        self._labels = {}  # key → NSTextField; populated in _setup_appearance

        self.menu = [
            rumps.MenuItem("line1", callback=noop),
            rumps.MenuItem("line2", callback=noop),
            rumps.separator,
            rumps.MenuItem("sched_header", callback=noop),
            rumps.MenuItem("sched_1", callback=noop),
            rumps.MenuItem("sched_2", callback=noop),
            rumps.separator,
            rumps.MenuItem("Start at Login", callback=self.toggle_login),
            rumps.separator,
        ]

        self.menu["sched_header"].title = "2× is active:"
        self.menu["sched_1"].title      = "  •  Mon–Fri  ·  1 AM – 7 PM WIB"
        self.menu["sched_2"].title      = "  •  Sat–Sun  ·  All day"

        self.menu["Start at Login"].state = is_login_enabled()
        self.update_status()

    @rumps.timer(0.5)
    def _setup_appearance(self, sender):
        import traceback

        # 1. Dark menu + label views
        try:
            dark    = NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
            ns_menu = self._nsapp.nsstatusitem.menu()
            ns_menu.setAppearance_(dark)

            for key in INFO_KEYS:
                item = self.menu[key]
                outer, label = _make_label_view(item.title)
                item._menuitem.setView_(outer)
                item._menuitem.setEnabled_(False)
                self._labels[key] = label
        except Exception:
            traceback.print_exc()

        # 2. Animation — NSTimer with a Python block on the main run loop.
        #    NSRunLoopCommonModes includes NSEventTrackingRunLoopMode, so the timer
        #    fires even while the menu is open. Block-based NSTimer (PyObjC 9+) avoids
        #    custom selector registration entirely. Main-thread execution means no
        #    thread-safety concerns for AppKit calls.
        try:
            self._status_btn = self._nsapp.nsstatusitem.button()
            timer = NSTimer.alloc().initWithFireDate_interval_repeats_block_(
                NSDate.date(), ANIM_FPS, True, lambda _t: self._tick()
            )
            NSRunLoop.mainRunLoop().addTimer_forMode_(timer, NSRunLoopCommonModes)
            self._anim_timer = timer
        except Exception:
            traceback.print_exc()

        sender.stop()

    def _tick(self):
        self._frame_index = (self._frame_index + 1) % FRAME_COUNT
        self._status_btn.setImage_(self._frame_images[self._frame_index])

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
            text = content[key]
            if key in self._labels:
                self._labels[key].setStringValue_(text)
            else:
                self.menu[key].title = text


if __name__ == "__main__":
    Claude2xApp().run()
