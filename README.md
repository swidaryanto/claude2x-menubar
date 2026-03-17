# Claude 2x Menubar

A tiny macOS menubar app that tells you **when you're getting double Claude usage** — so you always know the best time to work.

---

## Download

**[→ Download Claude2x.dmg](https://github.com/swidaryanto/claude2x-menubar/releases/latest/download/Claude2x.dmg)**

1. Open `Claude2x.dmg`
2. Drag **Claude 2x** into your Applications folder
3. Open it — the icon appears in your menubar instantly
4. Click the icon → check **Start at Login** so it's always there

> First time opening? macOS may ask you to confirm. Go to **System Settings → Privacy & Security → Open Anyway**.

---

## What is the 2x promotion?

Anthropic is doubling usage limits as a thank-you to everyone using Claude — across Claude.ai, Claude Code, and all plans (Free, Pro, Max, and Team). No setup needed. It's automatic.

### When you get double limits

| Day | Time (WIB · GMT+7) | Time (PT · US) |
|-----|-------------------|----------------|
| Monday – Friday | 7:00 PM – 1:00 AM | 5:00 AM – 11:00 AM |
| Saturday – Sunday | All day | All day |

**Promotion runs:** Mar 15 – Mar 29, 2026

---

## What the app shows you

| State | Menubar | What it means |
|-------|---------|---------------|
| 🟢 Active | `2x` | You're in the double-limit window — great time to use Claude |
| ⚪ Normal | `1x` | Standard limits apply right now |

The dropdown shows a live countdown to the next state change, in your local time (WIB).

---

## Features

- **Live status** — updates every 30 seconds
- **Countdown in WIB** — no mental timezone math
- **Expiry reminder** — tracks how many days are left in the promotion
- **Start at Login** — one click, always running
- **Dark menu** — WCAG-compliant contrast, easy to read

---

## Run from source

```bash
pip3 install rumps Pillow pytz numpy
python3 claude2x.py
```

---

## Build DMG yourself

```bash
pip3 install py2app
python3 setup.py py2app
hdiutil create -volname "Claude 2x" -srcfolder dist/Claude2x.app -ov -format UDZO Claude2x.dmg
```

---

Made with ☕ by [@swidaryanto](https://github.com/swidaryanto)
