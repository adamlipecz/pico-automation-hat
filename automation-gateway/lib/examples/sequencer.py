#!/usr/bin/env python3
"""
Relay Sequencer Example
=======================

Cycles through relays in sequence, useful for testing
or simple automation sequences.
"""

import sys
import time
import argparse

sys.path.insert(0, "../..")
from lib.automation2040w import Automation2040W


def main():
    parser = argparse.ArgumentParser(description="Relay sequencer")
    parser.add_argument("--port", help="Serial port", default=None)
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between toggles (seconds)"
    )
    parser.add_argument(
        "--cycles", type=int, default=3, help="Number of cycles (0 for infinite)"
    )
    args = parser.parse_args()

    print("Connecting to Automation 2040 W...")
    board = Automation2040W(args.port)
    print(f"Connected! Firmware: {board.version}")

    # Get number of relays
    status = board.status()
    num_relays = len(status["relays"])
    print(f"Found {num_relays} relay(s)")
    print()

    try:
        cycle = 0
        while args.cycles == 0 or cycle < args.cycles:
            cycle += 1
            print(f"Cycle {cycle}")

            # Turn on each relay in sequence
            for i in range(1, num_relays + 1):
                board.relay(i, True)
                board.led("A", 100)  # Flash LED A
                print(f"  Relay {i} ON")
                time.sleep(args.delay)
                board.led("A", 0)

            # Turn off each relay in sequence
            for i in range(1, num_relays + 1):
                board.relay(i, False)
                board.led("B", 100)  # Flash LED B
                print(f"  Relay {i} OFF")
                time.sleep(args.delay)
                board.led("B", 0)

            print()

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        board.reset()
        board.disconnect()
        print("Board reset and disconnected.")


if __name__ == "__main__":
    main()
