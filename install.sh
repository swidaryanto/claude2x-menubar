#!/bin/bash
set -e

REPO="https://raw.githubusercontent.com/swidaryanto/claude2x-menubar/main"
INSTALL_DIR="$HOME/.claude2x"
PLIST_LABEL="com.claude2x.app"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
PYTHON=$(which python3)

echo ""
echo "Claude 2x Menubar — Installer"
echo "=============================="
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "✗ Python 3 is not installed."
    echo "  Install it from https://www.python.org/downloads/macos/"
    exit 1
fi
echo "✓ Python 3 found ($PYTHON)"

# 2. Install dependencies
echo "→ Installing dependencies..."
pip3 install --quiet rumps pytz
echo "✓ Dependencies ready"

# 3. Download files
echo "→ Downloading Claude 2x..."
mkdir -p "$INSTALL_DIR/frames"
curl -fsSL "$REPO/claude2x.py"            -o "$INSTALL_DIR/claude2x.py"
for i in $(seq -f "%03g" 0 23); do
    curl -fsSL "$REPO/frames/frame_${i}.png" -o "$INSTALL_DIR/frames/frame_${i}.png"
done
echo "✓ Files downloaded to $INSTALL_DIR"

# 4. Create LaunchAgent (auto-start at login)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>             <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$INSTALL_DIR/claude2x.py</string>
    </array>
    <key>RunAtLoad</key>         <true/>
    <key>KeepAlive</key>         <true/>
</dict>
</plist>
EOF
echo "✓ Start at Login enabled"

# 5. Start now
echo "→ Starting Claude 2x..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "✓ Done! Claude 2x is running — look for the icon in your menubar."
echo ""
