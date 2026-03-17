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
                    NSView, NSTextField, NSFont, NSColor)
from Foundation import NSObject, NSTimer, NSRunLoop

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
# Animation timer helper
# rumps schedules timers in NSDefaultRunLoopMode, which macOS suspends while
# a menu is open (NSEventTrackingRunLoopMode). To keep the icon animating
# during menu display, we create the NSTimer manually and add it to
# NSRunLoopCommonModes — which fires in both modes.
# ---------------------------------------------------------------------------

class AnimTick(NSObject):
    def setCallback_(self, cb):
        self._cb = cb

    def tick_(self, _timer):
        self._cb()


# ---------------------------------------------------------------------------
# Custom label view
# Renders white text independently of NSMenuItem's enabled/disabled state.
# setEnabled_(False) on the NSMenuItem prevents hover — the custom view
# controls appearance, so system disabled-dimming never touches the text.
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
        frames = [os.path.join(FRAMES_DIR, f"frame_{i:03d}.png")
                  for i in range(FRAME_COUNT)]
        super().__init__("1x", icon=frames[0], template=True, quit_button="Quit")

        self._frames      = frames
        self._frame_index = 0
        self._labels      = {}   # key → NSTextField; populated in _setup_appearance

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
        try:
            dark    = NSAppearance.appearanceNamed_(NSAppearanceNameDarkAqua)
            ns_menu = self._nsapp.nsstatusitem.menu()
            ns_menu.setAppearance_(dark)

            # Attach custom label views to info items:
            # - NSTextField renders full-white text (no system disabled dimming)
            # - setEnabled_(False) removes hover highlight entirely
            for key in INFO_KEYS:
                item = self.menu[key]
                outer, label = _make_label_view(item.title)
                item._menuitem.setView_(outer)
                item._menuitem.setEnabled_(False)
                self._labels[key] = label

            # Animation timer in NSRunLoopCommonModes — keeps firing while menu is open
            self._anim_tick = AnimTick.alloc().init()
            self._anim_tick.setCallback_(self._advance_frame)
            anim_timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
                ANIM_FPS, self._anim_tick, "tick:", None, True
            )
            NSRunLoop.mainRunLoop().addTimer_forMode_(anim_timer, "NSRunLoopCommonModes")
            self._anim_timer = anim_timer

            sender.stop()
        except Exception:
            pass

    def _advance_frame(self):
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
            text = content[key]
            if key in self._labels:
                # Update custom label view text directly
                self._labels[key].setStringValue_(text)
            else:
                # Fallback before _setup_appearance fires (first ~0.5s)
                self.menu[key].title = text


if __name__ == "__main__":
    Claude2xApp().run()
