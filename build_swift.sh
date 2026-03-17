#!/bin/bash
set -e
cd "$(dirname "$0")"

APP="dist_swift/Claude2x.app"
CONTENTS="$APP/Contents"

echo "→ Compiling Swift..."
swiftc swift/main.swift -o swift/Claude2x_bin -framework AppKit -framework Foundation -O

echo "→ Building app bundle..."
rm -rf dist_swift
mkdir -p "$CONTENTS/MacOS"
mkdir -p "$CONTENTS/Resources/frames"

cp swift/Claude2x_bin "$CONTENTS/MacOS/Claude2x"

# Copy pre-generated frames
cp frames/*.png "$CONTENTS/Resources/frames/"

# Info.plist
cat > "$CONTENTS/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>    <string>com.claude2x.app</string>
    <key>CFBundleName</key>          <string>Claude2x</string>
    <key>CFBundleDisplayName</key>   <string>Claude 2x</string>
    <key>CFBundleExecutable</key>    <string>Claude2x</string>
    <key>CFBundleVersion</key>       <string>2.0.0</string>
    <key>CFBundleShortVersionString</key><string>2.0.0</string>
    <key>CFBundlePackageType</key>   <string>APPL</string>
    <key>LSUIElement</key>           <true/>
    <key>NSHighResolutionCapable</key><true/>
    <key>LSMinimumSystemVersion</key><string>12.0</string>
</dict>
</plist>
EOF

echo "→ Creating DMG..."
hdiutil create -volname "Claude 2x" -srcfolder "$APP" -ov -format UDZO Claude2x.dmg

SIZE=$(du -sh Claude2x.dmg | cut -f1)
echo "✓ Done — Claude2x.dmg ($SIZE)"
