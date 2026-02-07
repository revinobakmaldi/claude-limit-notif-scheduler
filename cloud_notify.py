#!/usr/bin/env python3
"""Cloud notification script for GitHub Actions.

Runs every hour. Checks if a Claude limit reset is within the next 65 minutes.
If yes, sleeps until 1 minute before and sends an ntfy push notification.
If no, exits immediately.
"""

import datetime
import math
import os
import subprocess
import sys
import time

EPOCH = datetime.datetime(2026, 2, 7, 11, 0, 0)
INTERVAL = datetime.timedelta(hours=5)
HEADS_UP = datetime.timedelta(minutes=1)
CHECK_WINDOW = datetime.timedelta(minutes=65)
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "revinobakmaldi-claude-limit")


def next_reset(now):
    elapsed = now - EPOCH
    if elapsed.total_seconds() < 0:
        return 1, EPOCH
    intervals_passed = math.floor(elapsed / INTERVAL)
    reset_num = intervals_passed + 1
    reset_time = EPOCH + reset_num * INTERVAL
    return reset_num, reset_time


def main():
    now = datetime.datetime.now()
    reset_num, reset_time = next_reset(now)
    time_until_reset = (reset_time - now).total_seconds()

    print(f"Now: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Next reset #{reset_num} at {reset_time.strftime('%Y-%m-%d %H:%M %p')}")
    print(f"Time until reset: {time_until_reset:.0f}s ({time_until_reset / 60:.0f} min)")

    if time_until_reset > CHECK_WINDOW.total_seconds():
        print("Reset is not within the next 65 minutes. Exiting.")
        return

    notify_at = reset_time - HEADS_UP
    sleep_seconds = (notify_at - now).total_seconds()

    if sleep_seconds > 0:
        print(f"Sleeping {sleep_seconds:.0f}s until notification time...")
        time.sleep(sleep_seconds)

    # Send notification
    _, next_time = next_reset(reset_time + datetime.timedelta(seconds=1))
    title = "Claude Limit Reset!"
    body = (
        f"Reset #{reset_num} — Your Claude limit has been reset. "
        f"Next reset at {next_time.strftime('%-I:%M %p')}"
    )

    print(f"Sending ntfy notification: {body}")
    result = subprocess.run(
        ["curl", "-s",
         "-H", f"Title: {title}",
         "-H", "Tags: bell",
         "-d", body,
         f"https://ntfy.sh/{NTFY_TOPIC}"],
        capture_output=True, text=True,
    )
    print(f"ntfy response: {result.stdout}")


if __name__ == "__main__":
    main()
