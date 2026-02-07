#!/usr/bin/env python3
"""Limit Reset Notification Scheduler.

Sends a macOS notification 1 minute before each session limit reset.
Resets occur every 5 hours starting from Feb 7, 2026 11:00 AM local time.
"""

import datetime
import math
import subprocess
import sys
import time

EPOCH = datetime.datetime(2026, 2, 7, 11, 0, 0)
INTERVAL = datetime.timedelta(hours=5)
HEADS_UP = datetime.timedelta(minutes=1)
NTFY_TOPIC = "revinobakmaldi-claude-limit"


def next_reset(now: datetime.datetime) -> tuple[int, datetime.datetime]:
    """Return (reset_number, next_reset_time) relative to EPOCH."""
    elapsed = now - EPOCH
    if elapsed.total_seconds() < 0:
        return 1, EPOCH
    intervals_passed = math.floor(elapsed / INTERVAL)
    reset_num = intervals_passed + 1
    reset_time = EPOCH + reset_num * INTERVAL
    return reset_num, reset_time


def notify(reset_num: int, reset_time: datetime.datetime) -> None:
    """Send notification via macOS and ntfy."""
    next_num, next_time = next_reset(reset_time + datetime.timedelta(seconds=1))
    title = "Claude Limit Reset!"
    body = (
        f"Reset #{reset_num} — Your Claude limit has been reset. "
        f"Next reset at {next_time.strftime('%-I:%M %p')}"
    )
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


def log(msg: str) -> None:
    """Print and flush so launchd logs appear immediately."""
    print(msg, flush=True)


def main() -> None:
    log(f"Limit Notif Scheduler started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Epoch: {EPOCH.strftime('%Y-%m-%d %H:%M %p')}")
    log(f"Interval: {INTERVAL}")

    while True:
        now = datetime.datetime.now()
        reset_num, reset_time = next_reset(now)
        notify_at = reset_time - HEADS_UP

        log(f"Next reset #{reset_num} at {reset_time.strftime('%Y-%m-%d %H:%M %p')}")
        log(f"Will notify at {notify_at.strftime('%Y-%m-%d %H:%M %p')}")

        sleep_seconds = (notify_at - now).total_seconds()
        if sleep_seconds > 0:
            log(f"Sleeping {sleep_seconds:.0f}s ...")
            time.sleep(sleep_seconds)

        log(f"Sending notification for reset #{reset_num}")
        notify(reset_num, reset_time)

        # Sleep until just past the reset time to avoid re-firing
        remaining = (reset_time - datetime.datetime.now()).total_seconds()
        if remaining > 0:
            time.sleep(remaining + 1)


if __name__ == "__main__":
    main()
