# Claude 2x Menubar

A macOS menubar app that tells you when you're in a **2x Claude Pro usage** period — so you never waste your double limits.

## What is 2x?

Anthropic announced double usage limits for Claude Pro:
- **Weeknights** — 7pm–1am WIB (outside 5–11am PT)
- **All weekend** — all day Saturday & Sunday
- Automatic, nothing to enable

Active since **Mar 15, 2026** · Ends **Mar 29, 2026**

## Features

- Live menubar icon with smooth floating animation
- Shows current status: double limits active or normal
- Countdown to next state change (in WIB / GMT+7)
- Expiry countdown with urgency-aware copy
- Dark menu with WCAG-compliant contrast
- **Start at Login** toggle built-in

## Install

Download `Claude2x.dmg` from [Releases](../../releases), open it, and drag **Claude 2x** to your Applications folder.

## Run from source

```bash
pip3 install rumps Pillow pytz numpy
python3 claude2x.py
```

## Build DMG

```bash
pip3 install py2app
python3 setup.py py2app
hdiutil create -volname "Claude2x" -srcfolder dist/Claude2x.app -ov -format UDZO Claude2x.dmg
```
