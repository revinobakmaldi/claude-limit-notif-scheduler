#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SETTINGS_FILE="$HOME/.claude/settings.json"
HOOK_CMD="$SCRIPT_DIR/notify_timer.sh"

echo "Installing Claude limit notification hook..."

# Ensure settings file exists
mkdir -p "$(dirname "$SETTINGS_FILE")"
if [ ! -f "$SETTINGS_FILE" ]; then
    echo '{}' > "$SETTINGS_FILE"
fi

# Add hook to Claude Code settings using python (stdlib only)
python3 -c "
import json, sys

settings_file = '$SETTINGS_FILE'
hook_cmd = '$HOOK_CMD'

with open(settings_file) as f:
    settings = json.load(f)

hook_entry = {
    'hooks': [{'type': 'command', 'command': hook_cmd}]
}

if 'hooks' not in settings:
    settings['hooks'] = {}

hooks = settings['hooks']
if 'UserPromptSubmit' not in hooks:
    hooks['UserPromptSubmit'] = []

# Check if hook already installed
for entry in hooks['UserPromptSubmit']:
    for h in entry.get('hooks', []):
        if h.get('command') == hook_cmd:
            print('Hook already installed.')
            sys.exit(0)

hooks['UserPromptSubmit'].append(hook_entry)

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print('Hook added to Claude Code settings.')
"

# Create state directory
mkdir -p "$HOME/.local/state/claude-limit-notif"

echo "Done. The notification timer will start automatically when you send your first message in Claude Code."
