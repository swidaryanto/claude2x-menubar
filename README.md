# Claude 2x Menubar

Know exactly when Claude gives you double the usage — right from your menubar.

No more guessing the timezone. No more missing your best window to work.

<br>

## Install

Open Terminal (`⌘ Space` → type `Terminal` → Enter):

```bash
brew install swidaryanto/tap/claude2x
brew services start swidaryanto/tap/claude2x
```

That's it. The icon lives in your menubar and wakes up automatically every time you log in.

<br>

> **Don't have Homebrew?** Install it first at [brew.sh](https://brew.sh) — it takes about 2 minutes.

<br>

## Manage

**Update to the latest version:**
```bash
brew upgrade swidaryanto/tap/claude2x
brew services restart swidaryanto/tap/claude2x
```

**Stop it:**
```bash
brew services stop claude2x
```

**Uninstall:**
```bash
brew services stop claude2x && brew uninstall claude2x
```

<br>

## What you'll see

The icon in your menubar switches between two states:

| Icon | Means |
|---|---|
| `2x` | Double limits active — best time to use Claude |
| `1x` | Standard limits right now |

Click the icon anytime to open the menu:

```
You're on double limits
Until 7:00 PM WIB  ·  1h 40m left

2× is active:
  •  Mon–Fri  ·  1 AM – 7 PM WIB
  •  Sat–Sun  ·  All day

✓ Start at Login
```

Times are shown in **WIB (GMT+7)** — no timezone math needed.

<br>

## When does 2x kick in?

Anthropic doubles usage limits outside peak hours — a thank-you to everyone using Claude.

| Day | Your time (WIB) | US time (PT) |
|---|---|---|
| Monday – Friday | 1:00 AM – 7:00 PM | 5:00 AM – 11:00 AM |
| Saturday – Sunday | All day | All day |

Works across all plans (Free, Pro, Max, Team) and everywhere you use Claude — including Claude Code.

<br>

## What makes it tick

- Animated icon that floats in your menubar — you'll notice it
- Live countdown to the next switch, updated every 30 seconds
- Times shown in WIB — no timezone math needed
- Toggle **Start at Login** right from the menu
- Runs quietly in the background, zero config needed

<br>

## Heads up

This is an independent, open-source tool. It's **not affiliated with or endorsed by Anthropic** in any way.

The 2x promotion is fully Anthropic's call — they can change, pause, or end it at any time. This app just reads your clock and shows the schedule [as announced by @claudeai](https://x.com/claudeai/status/2032911276226257206). Think of it as a handy reminder, not a guarantee.

<br>

## License

MIT © 2026 [swidaryanto](https://github.com/swidaryanto) — see [LICENSE](./LICENSE)

<br>

---

Made with ☕ by [@swidaryanto](https://github.com/swidaryanto)
