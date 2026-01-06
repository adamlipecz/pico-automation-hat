#!/usr/bin/env python3
"""
I/O Monitor Example
===================

Continuously monitors all inputs and ADCs and displays them.
Press Ctrl+C to exit.
"""

import sys
import time
sys.path.insert(0, '../..')
from lib.automation2040w import Automation2040W

def main():
    print("Connecting to Automation 2040 W...")
    board = Automation2040W()
    print(f"Connected! Firmware: {board.version}")
    print()
    print("Monitoring I/O (Ctrl+C to exit)...")
    print("-" * 50)
    
    try:
        while True:
            # Get all states at once
            status = board.status()
            
            # Build display line
            parts = []
            
            # Inputs
            inputs = " ".join(
                f"I{i+1}:{'H' if v else 'L'}" 
                for i, v in enumerate(status['inputs'])
            )
            parts.append(f"IN[{inputs}]")
            
            # ADCs
            adcs = " ".join(
                f"A{i+1}:{v:5.2f}V" 
                for i, v in enumerate(status['adcs'])
            )
            parts.append(f"ADC[{adcs}]")
            
            # Buttons
            btn_a = "A" if status['buttons']['a'] else "-"
            btn_b = "B" if status['buttons']['b'] else "-"
            parts.append(f"BTN[{btn_a}{btn_b}]")
            
            # Relays (for reference)
            relays = "".join(
                str(i+1) if v else "-"
                for i, v in enumerate(status['relays'])
            )
            parts.append(f"RLY[{relays}]")
            
            # Print with carriage return for updating in place
            print(" | ".join(parts), end="\r")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n")
        print("Stopped.")
    finally:
        board.disconnect()


if __name__ == "__main__":
    main()

