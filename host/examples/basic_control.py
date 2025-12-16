#!/usr/bin/env python3
"""
Basic Control Example
=====================

Demonstrates basic control of the Automation 2040 W:
- Toggling relays
- PWM outputs
- Reading inputs and ADCs
"""

import sys
import time
sys.path.insert(0, '..')
from automation2040w import Automation2040W

def main():
    # Connect to board (auto-detect port)
    print("Connecting to Automation 2040 W...")
    board = Automation2040W()
    print(f"Connected! Firmware: {board.version}")
    print()
    
    try:
        # === RELAY CONTROL ===
        print("=== Relay Control ===")
        for relay in range(1, 4):
            try:
                board.relay(relay, True)
                print(f"Relay {relay}: ON")
                time.sleep(0.3)
                board.relay(relay, False)
                print(f"Relay {relay}: OFF")
            except Exception:
                print(f"Relay {relay}: not available (Mini version?)")
                break
        print()
        
        # === PWM OUTPUTS ===
        print("=== PWM Output Demo ===")
        print("Fading Output 1...")
        for brightness in range(0, 101, 10):
            board.output(1, brightness)
            print(f"  {brightness}%", end="\r")
            time.sleep(0.1)
        for brightness in range(100, -1, -10):
            board.output(1, brightness)
            print(f"  {brightness}%", end="\r")
            time.sleep(0.1)
        print("\nDone!")
        print()
        
        # === READ INPUTS ===
        print("=== Digital Inputs ===")
        for i in range(1, 5):
            try:
                state = board.input(i)
                print(f"Input {i}: {'HIGH' if state else 'LOW'}")
            except Exception:
                break
        print()
        
        # === READ ADCs ===
        print("=== ADC Readings ===")
        for i in range(1, 4):
            try:
                voltage = board.adc(i)
                print(f"ADC {i}: {voltage:.3f}V")
            except Exception:
                break
        print()
        
        # === BUTTON LEDs ===
        print("=== Button LEDs ===")
        board.led('A', 50)
        board.led('B', 50)
        print("Both button LEDs at 50%")
        time.sleep(1)
        
    finally:
        # Always reset to safe state
        board.reset()
        board.disconnect()
        print("Board reset and disconnected.")


if __name__ == "__main__":
    main()

