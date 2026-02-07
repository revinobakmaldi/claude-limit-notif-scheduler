# Claude Limit Notif Scheduler

A lightweight macOS background service that sends notifications when your Claude Pro/Team session limit resets. Notifications are sent to both macOS (native) and iPhone (via [ntfy](https://ntfy.sh)).

## How It Works

Claude session limits reset every **5 hours** on a rolling schedule. The scheduler calculates the next reset time and sends a notification **1 minute before** each reset.

```
Reset schedule (example starting Feb 7):
11:00 AM → 4:00 PM → 9:00 PM → 2:00 AM → 7:00 AM → 12:00 PM → ...
```

### Notification Channels

| Channel | How |
|---------|-----|
| **macOS** | Native `osascript` notification with sound |
| **iPhone** | Push via [ntfy.sh](https://ntfy.sh) — install the ntfy app and subscribe to the topic |

## Setup

### 1. Configure

Edit `scheduler.py` to set your schedule:

```python
EPOCH = datetime.datetime(2026, 2, 7, 11, 0, 0)  # your first reset time
INTERVAL = datetime.timedelta(hours=5)              # reset interval
NTFY_TOPIC = "revinobakmaldi-claude-limit"          # your ntfy topic
```

### 2. iPhone Notifications

1. Install the **ntfy** app ([iOS](https://apps.apple.com/us/app/ntfy/id1625396347))
2. Subscribe to your topic (e.g. `revinobakmaldi-claude-limit`)

### 3. Install

```bash
./install.sh
```

This copies the launchd plist to `~/Library/LaunchAgents/` and starts the service. It will auto-start on login and restart if killed.

### 4. Verify

```bash
# Check service is running
launchctl list | grep limit-notif

# Check logs
cat ~/Library/Logs/limit-notif-scheduler.log
```

## Uninstall

```bash
./uninstall.sh
```

## Files

| File | Purpose |
|------|---------|
| `scheduler.py` | Main scheduler loop — calculates next reset, sleeps, sends notifications |
| `com.revinobakmaldi.limit-notif-scheduler.plist` | launchd service definition |
| `install.sh` | One-command install |
| `uninstall.sh` | One-command uninstall |

## Requirements

- macOS
- Python 3 (pre-installed on macOS)
- No pip dependencies — stdlib only
