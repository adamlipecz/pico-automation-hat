"""
Automation 2040 W USB Control Firmware
======================================

A simple text-based command protocol for controlling the Pimoroni Automation 2040 W
over USB serial (CDC ACM).

Protocol Design:
- Commands are newline-terminated ASCII strings
- Responses always start with OK, ERR, or the requested data
- Query commands end with '?'
- Human-readable and easy to debug with any serial terminal

Commands:
---------
RELAY <n> <ON|OFF>      Set relay n (1-3) on or off
RELAY <n>?              Query relay n state
OUTPUT <n> <value>      Set output n (1-3), value 0-100 (PWM %) or ON/OFF
OUTPUT <n>?             Query output n state
INPUT <n>?              Query digital input n (1-4)
ADC <n>?                Query ADC n (1-3) voltage
LED <A|B> <value>       Set button LED brightness (0-100)
BUTTON <A|B>?           Query button state
STATUS                  Get all I/O states as JSON
RESET                   Reset all outputs to safe state
VERSION                 Get firmware version
HELP                    Show available commands

Responses:
----------
OK                      Command executed successfully
OK <value>              Query result
ERR <message>           Error with description
{...}                   JSON data (for STATUS)

Author: Generated for Pimoroni Automation 2040 W
License: MIT
"""

import sys
import select
import json

# Import the Pimoroni automation library (must have Pimoroni MicroPython firmware)
from automation import Automation2040W, Automation2040WMini, SWITCH_A, SWITCH_B

VERSION = "1.0.0"


class AutomationController:
    """Main controller for USB serial commands."""

    def __init__(self, board_type="standard"):
        """
        Initialize the controller.

        Args:
            board_type: "standard" for Automation2040W, "mini" for Automation2040WMini
        """
        if board_type == "mini":
            self.board = Automation2040WMini()
        else:
            self.board = Automation2040W()

        self.running = True
        self.buffer = ""

    def send_response(self, response):
        """Send a response back over USB serial."""
        print(response)

    def parse_command(self, line):
        """Parse and execute a command."""
        line = line.strip()
        if not line or line.startswith("#"):
            return  # Ignore empty lines and comments

        parts = line.upper().split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        try:
            if cmd == "RELAY":
                self.cmd_relay(args)
            elif cmd == "OUTPUT":
                self.cmd_output(args)
            elif cmd == "INPUT":
                self.cmd_input(args)
            elif cmd == "ADC":
                self.cmd_adc(args)
            elif cmd == "LED":
                self.cmd_led(args)
            elif cmd == "BUTTON":
                self.cmd_button(args)
            elif cmd == "STATUS":
                self.cmd_status()
            elif cmd == "RESET":
                self.cmd_reset()
            elif cmd == "VERSION":
                self.send_response(f"OK {VERSION}")
            elif cmd == "HELP":
                self.cmd_help()
            elif cmd == "PING":
                self.send_response("OK PONG")
            else:
                self.send_response(f"ERR Unknown command: {cmd}")
        except Exception as e:
            self.send_response(f"ERR {type(e).__name__}: {e}")

    def cmd_relay(self, args):
        """Handle RELAY commands."""
        if not args:
            self.send_response("ERR RELAY requires arguments")
            return

        # Check if it's a query
        if args[0].endswith("?"):
            index = int(args[0].rstrip("?")) - 1
            if not (0 <= index < self.board.NUM_RELAYS):
                self.send_response(
                    f"ERR Relay index out of range (1-{self.board.NUM_RELAYS})"
                )
                return
            state = (
                self.board.relay(index)
                if self.board.NUM_RELAYS > 1
                else self.board.relay()
            )
            self.send_response(f"OK {'ON' if state else 'OFF'}")
        else:
            # Setting relay state
            if len(args) < 2:
                self.send_response("ERR RELAY requires index and state (ON/OFF)")
                return

            index = int(args[0]) - 1
            if not (0 <= index < self.board.NUM_RELAYS):
                self.send_response(
                    f"ERR Relay index out of range (1-{self.board.NUM_RELAYS})"
                )
                return

            state = args[1] in ("ON", "1", "TRUE", "HIGH")
            if self.board.NUM_RELAYS > 1:
                self.board.relay(index, state)
            else:
                self.board.relay(state)
            self.send_response("OK")

    def cmd_output(self, args):
        """Handle OUTPUT commands."""
        if not args:
            self.send_response("ERR OUTPUT requires arguments")
            return

        # Check if it's a query
        if args[0].endswith("?"):
            index = int(args[0].rstrip("?")) - 1
            if not (0 <= index < self.board.NUM_OUTPUTS):
                self.send_response(
                    f"ERR Output index out of range (1-{self.board.NUM_OUTPUTS})"
                )
                return
            value = self.board.output(index)
            # Return as percentage
            self.send_response(f"OK {int(value * 100)}")
        else:
            # Setting output state
            if len(args) < 2:
                self.send_response(
                    "ERR OUTPUT requires index and value (0-100 or ON/OFF)"
                )
                return

            index = int(args[0]) - 1
            if not (0 <= index < self.board.NUM_OUTPUTS):
                self.send_response(
                    f"ERR Output index out of range (1-{self.board.NUM_OUTPUTS})"
                )
                return

            # Parse value - can be ON/OFF or 0-100
            val_str = args[1]
            if val_str in ("ON", "TRUE", "HIGH"):
                value = 1.0
            elif val_str in ("OFF", "FALSE", "LOW"):
                value = 0.0
            else:
                value = float(val_str) / 100.0  # Convert percentage to 0-1
                value = max(0.0, min(1.0, value))  # Clamp

            self.board.output(index, value)
            self.send_response("OK")

    def cmd_input(self, args):
        """Handle INPUT commands (query only)."""
        if not args:
            self.send_response("ERR INPUT requires index")
            return

        index_str = args[0].rstrip("?")
        index = int(index_str) - 1

        if not (0 <= index < self.board.NUM_INPUTS):
            self.send_response(
                f"ERR Input index out of range (1-{self.board.NUM_INPUTS})"
            )
            return

        value = self.board.read_input(index)
        self.send_response(f"OK {'HIGH' if value else 'LOW'}")

    def cmd_adc(self, args):
        """Handle ADC commands (query only)."""
        if not args:
            self.send_response("ERR ADC requires index")
            return

        index_str = args[0].rstrip("?")
        index = int(index_str) - 1

        if not (0 <= index < self.board.NUM_ADCS):
            self.send_response(f"ERR ADC index out of range (1-{self.board.NUM_ADCS})")
            return

        voltage = self.board.read_adc(index)
        self.send_response(f"OK {voltage:.3f}")

    def cmd_led(self, args):
        """Handle LED commands for button LEDs."""
        if not args:
            self.send_response("ERR LED requires button (A/B) and brightness")
            return

        button_str = args[0].upper()
        if button_str == "A":
            button = SWITCH_A
        elif button_str == "B":
            button = SWITCH_B
        else:
            self.send_response("ERR LED button must be A or B")
            return

        if len(args) < 2:
            self.send_response("ERR LED requires brightness (0-100)")
            return

        brightness = int(args[1])
        brightness = max(0, min(100, brightness))
        self.board.switch_led(button, brightness)
        self.send_response("OK")

    def cmd_button(self, args):
        """Handle BUTTON queries."""
        if not args:
            self.send_response("ERR BUTTON requires button (A/B)")
            return

        button_str = args[0].rstrip("?").upper()
        if button_str == "A":
            button = SWITCH_A
        elif button_str == "B":
            button = SWITCH_B
        else:
            self.send_response("ERR BUTTON must be A or B")
            return

        pressed = self.board.switch_pressed(button)
        self.send_response(f"OK {'PRESSED' if pressed else 'RELEASED'}")

    def cmd_status(self):
        """Return all I/O states as JSON."""
        status = {
            "relays": [],
            "outputs": [],
            "inputs": [],
            "adcs": [],
            "buttons": {
                "a": self.board.switch_pressed(SWITCH_A),
                "b": self.board.switch_pressed(SWITCH_B),
            },
        }

        # Collect relay states
        for i in range(self.board.NUM_RELAYS):
            if self.board.NUM_RELAYS > 1:
                status["relays"].append(bool(self.board.relay(i)))
            else:
                status["relays"].append(bool(self.board.relay()))

        # Collect output states
        for i in range(self.board.NUM_OUTPUTS):
            status["outputs"].append(round(self.board.output(i) * 100, 1))

        # Collect input states
        for i in range(self.board.NUM_INPUTS):
            status["inputs"].append(bool(self.board.read_input(i)))

        # Collect ADC values
        for i in range(self.board.NUM_ADCS):
            status["adcs"].append(round(self.board.read_adc(i), 3))

        self.send_response(json.dumps(status))

    def cmd_reset(self):
        """Reset all outputs to safe state."""
        self.board.reset()
        self.send_response("OK")

    def cmd_help(self):
        """Show available commands."""
        help_text = """OK Commands:
RELAY <n> <ON|OFF>   - Set relay (1-{relays})
RELAY <n>?           - Query relay state
OUTPUT <n> <0-100>   - Set output PWM % (1-{outputs})
OUTPUT <n> <ON|OFF>  - Set output full on/off
OUTPUT <n>?          - Query output state
INPUT <n>?           - Query input (1-{inputs})
ADC <n>?             - Query ADC voltage (1-{adcs})
LED <A|B> <0-100>    - Set button LED brightness
BUTTON <A|B>?        - Query button state
STATUS               - Get all states as JSON
RESET                - Reset to safe state
VERSION              - Show firmware version
PING                 - Test connection""".format(
            relays=self.board.NUM_RELAYS,
            outputs=self.board.NUM_OUTPUTS,
            inputs=self.board.NUM_INPUTS,
            adcs=self.board.NUM_ADCS,
        )
        self.send_response(help_text)

    def run(self):
        """Main loop - read and process USB serial commands."""
        print(f"# Automation 2040 W Controller v{VERSION}")
        print(
            f"# Relays: {self.board.NUM_RELAYS}, Outputs: {self.board.NUM_OUTPUTS}, Inputs: {self.board.NUM_INPUTS}, ADCs: {self.board.NUM_ADCS}"
        )
        print("# Ready - type HELP for commands")

        # Use select for non-blocking input on MicroPython
        poll = select.poll()
        poll.register(sys.stdin, select.POLLIN)

        while self.running:
            # Check for input with timeout
            events = poll.poll(100)  # 100ms timeout

            for fd, event in events:
                if event & select.POLLIN:
                    char = sys.stdin.read(1)
                    if char == "\n" or char == "\r":
                        if self.buffer:
                            self.parse_command(self.buffer)
                            self.buffer = ""
                    else:
                        self.buffer += char


# Main entry point
if __name__ == "__main__":
    # Change to "mini" for Automation 2040 W Mini
    controller = AutomationController(board_type="standard")
    controller.run()
