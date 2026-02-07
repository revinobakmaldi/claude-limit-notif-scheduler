#!/bin/bash
set -euo pipefail

PLIST_NAME="com.revinobakmaldi.limit-notif-scheduler.plist"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Installing limit-notif-scheduler..."

# Unload first if already loaded
if launchctl list | grep -q "com.revinobakmaldi.limit-notif-scheduler"; then
    echo "Unloading existing service..."
    launchctl unload "$DEST" 2>/dev/null || true
fi

# Copy plist
cp "$SRC_DIR/$PLIST_NAME" "$DEST"
echo "Copied plist to $DEST"

# Load service
launchctl load "$DEST"
echo "Service loaded."

# Verify
if launchctl list | grep -q "com.revinobakmaldi.limit-notif-scheduler"; then
    echo "Service is running."
else
    echo "WARNING: Service does not appear in launchctl list."
    exit 1
fi

echo "Done. Logs at ~/Library/Logs/limit-notif-scheduler.log"
