# Claude 2x Menubar

A tiny macOS menubar app that tells you **when you're getting double Claude usage** — so you always know the best time to work.

<br>

## Install

Open **Terminal** (press `⌘ Space`, type `Terminal`, hit Enter) and paste this:

```bash
curl -fsSL https://raw.githubusercontent.com/swidaryanto/claude2x-menubar/main/install.sh | bash
```

That's it. The icon appears in your menubar and starts automatically on every login.

<br>

> **To uninstall**, paste this in Terminal:
> ```bash
> launchctl unload ~/Library/LaunchAgents/com.claude2x.app.plist
> rm -rf ~/.claude2x ~/Library/LaunchAgents/com.claude2x.app.plist
> ```

<br>

## What is the 2x promotion?

Anthropic is doubling usage limits as a thank-you to everyone using Claude — across Claude.ai, Claude Code, and all plans (Free, Pro, Max, and Team). No setup needed. It's automatic.

<br>

### When you get double limits

| Day | Time (WIB · GMT+7) | Time (PT · US) |
|---|---|---|
| Monday – Friday | 7:00 PM – 1:00 AM | 5:00 AM – 11:00 AM |
| Saturday – Sunday | All day | All day |

Works on all plans — Free, Pro, Max, and Team. Applies everywhere you use Claude, including Claude Code.

<br>

## What the app shows you

| State | Menubar | What it means |
|---|---|---|
| 🟢 Active | `2x` | You're in the double-limit window — great time to use Claude |
| ⚪ Normal | `1x` | Standard limits apply right now |

The dropdown shows a live countdown to the next state change, in your local time (WIB).

<br>

## Features

- **Live status** — updates every 30 seconds
- **Animated icon** — smooth floating animation
- **Countdown in WIB** — no mental timezone math
- **Expiry reminder** — tracks how many days are left in the promotion
- **Auto-starts at login** — always running, zero maintenance

<br>

---

Made with ☕ by [@swidaryanto](https://github.com/swidaryanto)
