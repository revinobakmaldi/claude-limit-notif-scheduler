#!/bin/bash
set -euo pipefail

PLIST_NAME="com.revinobakmaldi.limit-notif-scheduler.plist"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Uninstalling limit-notif-scheduler..."

if [ -f "$DEST" ]; then
    launchctl unload "$DEST" 2>/dev/null || true
    echo "Service unloaded."
    rm "$DEST"
    echo "Removed $DEST"
else
    echo "Plist not found at $DEST, nothing to unload."
fi

echo "Done."
