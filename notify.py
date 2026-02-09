#!/usr/bin/env python3
"""Claude limit reset notification timer.

Waits 5 hours from invocation (first message), then sends notifications
via macOS and ntfy. Sends a heads-up 1 minute before reset, and a final
notification at reset time. Cleans up its own lock file on exit.
"""

import datetime
import os
import signal
import subprocess
import sys
import time

LIMIT_WINDOW = datetime.timedelta(hours=5)
HEADS_UP = datetime.timedelta(minutes=1)
NTFY_TOPIC = "revinobakmaldi-claude-limit"
STATE_DIR = os.path.expanduser("~/.local/state/claude-limit-notif")
LOCK_FILE = os.path.join(STATE_DIR, "timer.pid")


def cleanup(*_):
    """Remove lock file on exit."""
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass
    sys.exit(0)


def send_notification(title, body):
    """Send notification via macOS and ntfy."""
    # macOS notification
    script = (
        f'display notification "{body}" '
        f'with title "{title}" '
        f'sound name "default"'
    )
    subprocess.run(["osascript", "-e", script], check=False)
    # ntfy push notification (iPhone)
    subprocess.run(
        ["curl", "-s",
         "-H", f"Title: {title}",
         "-H", "Tags: bell",
         "-d", body,
         f"https://ntfy.sh/{NTFY_TOPIC}"],
        check=False,
    )


def main():
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # Accept optional minutes argument (e.g. `python3 notify.py 228` for 3h48m)
    if len(sys.argv) > 1:
        minutes = int(sys.argv[1])
        window = datetime.timedelta(minutes=minutes)
    else:
        window = LIMIT_WINDOW

    start_time = datetime.datetime.now()
    reset_time = start_time + window
    heads_up_time = reset_time - HEADS_UP

    # Sleep until 1 minute before reset
    sleep_seconds = (heads_up_time - datetime.datetime.now()).total_seconds()
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    # Heads-up notification
    send_notification(
        "Claude Limit Resets Soon",
        f"Your Claude limit resets in 1 minute (at {reset_time.strftime('%-I:%M %p')})",
    )

    # Sleep the remaining minute
    remaining = (reset_time - datetime.datetime.now()).total_seconds()
    if remaining > 0:
        time.sleep(remaining)

    # Reset notification
    send_notification(
        "Claude Limit Reset!",
        f"Your Claude limit has been reset. Started at {start_time.strftime('%-I:%M %p')}, reset at {reset_time.strftime('%-I:%M %p')}",
    )

    cleanup()


if __name__ == "__main__":
    main()
