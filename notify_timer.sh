#!/bin/bash
# Claude Code hook: starts a 5-hour notification timer on first message.
# Skips if a timer is already running for the current session window.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="$HOME/.local/state/claude-limit-notif"
LOCK_FILE="$STATE_DIR/timer.pid"
NOTIFY_SCRIPT="$SCRIPT_DIR/notify.py"

mkdir -p "$STATE_DIR"

# Check if a timer is already running
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        # Timer already running, skip
        exit 0
    fi
    # Stale lock file, clean up
    rm -f "$LOCK_FILE"
fi

# Start background timer
python3 "$NOTIFY_SCRIPT" &
echo $! > "$LOCK_FILE"

exit 0
