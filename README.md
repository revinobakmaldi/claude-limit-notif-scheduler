# Claude Limit Notif Scheduler

A lightweight notification tool that automatically starts a 5-hour countdown when you send your first message in Claude Code, and notifies you when your session limit resets. Notifications are sent to both macOS (native) and iPhone (via [ntfy](https://ntfy.sh)).

## How It Works

Claude session limits reset **5 hours after your first message**. This tool uses a [Claude Code hook](https://docs.anthropic.com/en/docs/claude-code/hooks) to detect when you send a message, starts a background timer, and sends notifications when your limit is about to reset.

1. You send a message in Claude Code
2. The `UserPromptSubmit` hook fires and starts a background 5-hour timer
3. Subsequent messages are ignored (timer already running)
4. 1 minute before reset: heads-up notification
5. At reset: final notification
6. Timer cleans up — next session starts a fresh timer

### Notification Channels

| Channel | How |
|---------|-----|
| **macOS** | Native `osascript` notification with sound |
| **iPhone** | Push via [ntfy.sh](https://ntfy.sh) — install the ntfy app and subscribe to the topic |

## Setup

### 1. Configure

Edit `notify.py` to set your ntfy topic:

```python
NTFY_TOPIC = "revinobakmaldi-claude-limit"  # your ntfy topic
```

### 2. iPhone Notifications

1. Install the **ntfy** app ([iOS](https://apps.apple.com/us/app/ntfy/id1625396347))
2. Subscribe to your topic (e.g. `revinobakmaldi-claude-limit`)

### 3. Install

```bash
./install.sh
```

This adds a `UserPromptSubmit` hook to your Claude Code settings (`~/.claude/settings.json`). The timer starts automatically on your next Claude Code session.

### 4. Verify

```bash
# Check if a timer is running
cat ~/.local/state/claude-limit-notif/timer.pid

# Test the hook manually
./notify_timer.sh
```

## Manual Timer

If you already know the remaining time (e.g. from `/usage` in Claude Code), you can start a timer manually:

```bash
# Start a timer with custom minutes (e.g. 3h48m = 228 minutes)
python3 notify.py 228
```

This is useful for sessions already in progress.

## Uninstall

```bash
./uninstall.sh
```

## Files

| File | Purpose |
|------|---------|
| `notify_timer.sh` | Hook script — checks for existing timer, starts one if needed |
| `notify.py` | Timer script — sleeps for 5 hours, sends notifications |
| `install.sh` | Adds the hook to Claude Code settings |
| `uninstall.sh` | Removes hook, kills timer, cleans up |

## Requirements

- macOS
- Python 3 (pre-installed on macOS)
- Claude Code
- No pip dependencies — stdlib only
