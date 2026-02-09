#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SETTINGS_FILE="$HOME/.claude/settings.json"
HOOK_CMD="$SCRIPT_DIR/notify_timer.sh"
STATE_DIR="$HOME/.local/state/claude-limit-notif"
LOCK_FILE="$STATE_DIR/timer.pid"

echo "Uninstalling Claude limit notification hook..."

# Kill running timer if any
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
        echo "Stopped running timer (PID $pid)."
    fi
    rm -f "$LOCK_FILE"
fi

# Remove hook from Claude Code settings
if [ -f "$SETTINGS_FILE" ]; then
    python3 -c "
import json

settings_file = '$SETTINGS_FILE'
hook_cmd = '$HOOK_CMD'

with open(settings_file) as f:
    settings = json.load(f)

hooks = settings.get('hooks', {})
if 'UserPromptSubmit' in hooks:
    hooks['UserPromptSubmit'] = [
        entry for entry in hooks['UserPromptSubmit']
        if not any(h.get('command') == hook_cmd for h in entry.get('hooks', []))
    ]
    if not hooks['UserPromptSubmit']:
        del hooks['UserPromptSubmit']
    if not hooks:
        del settings['hooks']

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print('Hook removed from Claude Code settings.')
"
fi

# Clean up state directory
rm -rf "$STATE_DIR"
echo "Cleaned up state files."

# Remove old launchd service if still present
OLD_PLIST="$HOME/Library/LaunchAgents/com.revinobakmaldi.limit-notif-scheduler.plist"
if [ -f "$OLD_PLIST" ]; then
    launchctl unload "$OLD_PLIST" 2>/dev/null || true
    rm "$OLD_PLIST"
    echo "Removed old launchd service."
fi

echo "Done."
