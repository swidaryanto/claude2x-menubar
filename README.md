# Claude 2x Menubar

A tiny macOS menubar app that tells you **when you're getting double Claude usage** — so you always know the best time to work.

<br>

## Install

Choose the option that works best for you:

<br>

### Option A — DMG (Swift native, 40KB)

**[→ Download Claude2x.dmg](https://github.com/swidaryanto/claude2x-menubar/releases/latest/download/Claude2x.dmg)**

1. Open `Claude2x.dmg`
2. Drag **Claude 2x** into your Applications folder
3. Open **Terminal** (`⌘ Space` → type `Terminal` → Enter) and paste:
   ```bash
   xattr -cr /Applications/Claude2x.app
   ```
4. Double-click **Claude 2x** — the icon appears in your menubar instantly

<br>

### Option B — One-line installer (Python)

Open **Terminal** (`⌘ Space` → type `Terminal` → Enter) and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/swidaryanto/claude2x-menubar/main/install.sh | bash
```

The icon appears in your menubar and starts automatically on every login. No DMG, no Gatekeeper prompt.

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
- **Auto-starts at login** — always running, zero maintenance

<br>

---

## Disclaimer

This app is an independent, open-source tool and is **not affiliated with, endorsed by, or connected to Anthropic** in any way.

The double usage promotion is entirely Anthropic's initiative. This app only reads your local clock and displays the schedule as publicly announced by [@claudeai on X](https://x.com/claudeai/status/2032911276226257206). The promotion may start, pause, change, or end at any time solely at Anthropic's discretion — this app has no control over that.

Use it as a convenience reminder, not as a guarantee of any usage benefit.

<br>

## License

MIT © 2026 [swidaryanto](https://github.com/swidaryanto) — see [LICENSE](./LICENSE) for full text.

<br>

---

Made with ☕ by [@swidaryanto](https://github.com/swidaryanto)
