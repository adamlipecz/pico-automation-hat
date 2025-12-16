"""
Automation 2040 W Host Control Library
======================================

Python library for controlling the Pimoroni Automation 2040 W
over USB serial from a host computer.

Usage:
    from automation2040w import Automation2040W

    # Auto-detect port
    board = Automation2040W()

    # Or specify port
    board = Automation2040W('/dev/ttyACM0')  # Linux
    board = Automation2040W('COM3')          # Windows

    # Control relays
    board.relay(1, True)   # Turn on relay 1
    board.relay(2, False)  # Turn off relay 2
    state = board.relay(1) # Query relay 1 state

    # Control outputs (PWM capable)
    board.output(1, 100)   # Full on
    board.output(2, 50)    # 50% PWM
    board.output(3, 0)     # Off

    # Read inputs
    value = board.input(1)  # Returns True/False

    # Read ADC
    voltage = board.adc(1)  # Returns voltage (0-40V)

    # Get all states
    status = board.status()  # Returns dict with all I/O states

Author: Generated for Pimoroni Automation 2040 W
License: MIT
"""

import serial
import serial.tools.list_ports
import json
import time
from typing import Optional, Union, Dict, List, Any


class Automation2040WError(Exception):
    """Base exception for Automation 2040 W errors."""

    pass


class ConnectionError(Automation2040WError):
    """Could not connect to the board."""

    pass


class CommandError(Automation2040WError):
    """Command execution failed."""

    pass


class Automation2040W:
    """Control interface for Automation 2040 W over USB serial."""

    # USB VID/PID for Raspberry Pi Pico
    PICO_VID = 0x2E8A
    PICO_PID_PICO = 0x0005
    PICO_PID_PICOW = 0x000A

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 115200,
        timeout: float = 1.0,
        auto_connect: bool = True,
    ):
        """
        Initialize connection to Automation 2040 W.

        Args:
            port: Serial port path. If None, auto-detect.
            baudrate: Serial baudrate (default 115200).
            timeout: Read timeout in seconds.
            auto_connect: Automatically connect on init.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self._version: Optional[str] = None

        if auto_connect:
            self.connect()

    @classmethod
    def find_ports(cls) -> List[str]:
        """
        Find all potential Automation 2040 W ports.

        Returns:
            List of serial port paths that might be a Pico.
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            # Check for Raspberry Pi Pico VID
            if port.vid == cls.PICO_VID:
                ports.append(port.device)
            # Also check for generic CDC ACM devices on Linux/Mac
            elif "ACM" in port.device or "usbmodem" in port.device:
                ports.append(port.device)
        return ports

    def connect(self, port: Optional[str] = None) -> None:
        """
        Connect to the board.

        Args:
            port: Serial port path. Uses stored port or auto-detects if None.

        Raises:
            ConnectionError: If connection fails.
        """
        if port:
            self.port = port

        if self.port is None:
            # Auto-detect
            ports = self.find_ports()
            if not ports:
                raise ConnectionError(
                    "No Automation 2040 W found. Make sure the board is connected "
                    "and has the firmware installed."
                )
            self.port = ports[0]

        try:
            self.serial = serial.Serial(
                self.port, baudrate=self.baudrate, timeout=self.timeout
            )
            # Wait for board to be ready
            time.sleep(0.5)
            # Flush any startup messages
            self.serial.reset_input_buffer()

            # Test connection
            response = self._send_command("PING")
            if response != "PONG":
                raise ConnectionError(
                    f"Board did not respond correctly to PING. Got: {response}"
                )

            # Get version
            self._version = self._send_command("VERSION")

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to open {self.port}: {e}")

    def disconnect(self) -> None:
        """Disconnect from the board."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.serial = None

    def _send_command(self, command: str) -> str:
        """
        Send a command and get the response.

        Args:
            command: Command string to send.

        Returns:
            Response string (without OK prefix).

        Raises:
            CommandError: If command fails.
        """
        if not self.serial or not self.serial.is_open:
            raise CommandError("Not connected to board")

        # Send command
        self.serial.write(f"{command}\n".encode())
        self.serial.flush()

        # Read response (handle multi-line responses like HELP)
        lines = []
        while True:
            line = self.serial.readline().decode().strip()
            if not line:
                break
            # Skip comment lines
            if line.startswith("#"):
                continue
            lines.append(line)
            # Single-line responses end here
            if line.startswith("OK") or line.startswith("ERR") or line.startswith("{"):
                break

        if not lines:
            raise CommandError("No response from board")

        response = "\n".join(lines)

        # Check for error
        if response.startswith("ERR"):
            raise CommandError(response[4:])

        # Strip OK prefix if present
        if response.startswith("OK"):
            response = response[2:].strip()

        return response

    @property
    def version(self) -> str:
        """Get firmware version."""
        if self._version is None:
            self._version = self._send_command("VERSION")
        return self._version

    def relay(self, index: int, state: Optional[bool] = None) -> bool:
        """
        Get or set relay state.

        Args:
            index: Relay number (1-3).
            state: If provided, set relay to this state. If None, query state.

        Returns:
            Current relay state (True = on, False = off).
        """
        if state is not None:
            self._send_command(f"RELAY {index} {'ON' if state else 'OFF'}")
            return state
        else:
            response = self._send_command(f"RELAY {index}?")
            return response == "ON"

    def output(self, index: int, value: Optional[Union[int, bool]] = None) -> int:
        """
        Get or set output state.

        Args:
            index: Output number (1-3).
            value: If provided, set output to this value:
                   - int (0-100): PWM percentage
                   - bool: True = 100%, False = 0%
                   If None, query current value.

        Returns:
            Current output value (0-100%).
        """
        if value is not None:
            if isinstance(value, bool):
                value = 100 if value else 0
            self._send_command(f"OUTPUT {index} {value}")
            return value
        else:
            response = self._send_command(f"OUTPUT {index}?")
            return int(response)

    def input(self, index: int) -> bool:
        """
        Read digital input state.

        Args:
            index: Input number (1-4).

        Returns:
            Input state (True = HIGH, False = LOW).
        """
        response = self._send_command(f"INPUT {index}?")
        return response == "HIGH"

    def adc(self, index: int) -> float:
        """
        Read ADC voltage.

        Args:
            index: ADC channel (1-3).

        Returns:
            Voltage reading (typically 0-40V range).
        """
        response = self._send_command(f"ADC {index}?")
        return float(response)

    def led(self, button: str, brightness: int) -> None:
        """
        Set button LED brightness.

        Args:
            button: "A" or "B".
            brightness: 0-100%.
        """
        self._send_command(f"LED {button.upper()} {brightness}")

    def button(self, button: str) -> bool:
        """
        Read button state.

        Args:
            button: "A" or "B".

        Returns:
            True if pressed, False if released.
        """
        response = self._send_command(f"BUTTON {button.upper()}?")
        return response == "PRESSED"

    def status(self) -> Dict[str, Any]:
        """
        Get all I/O states.

        Returns:
            Dictionary with all relay, output, input, ADC, and button states.
        """
        response = self._send_command("STATUS")
        return json.loads(response)

    def reset(self) -> None:
        """Reset all outputs to safe state."""
        self._send_command("RESET")

    def __enter__(self):
        """Context manager entry."""
        if not self.serial or not self.serial.is_open:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False


class Automation2040WMini(Automation2040W):
    """
    Control interface for Automation 2040 W Mini.

    Same as Automation2040W but with different I/O counts:
    - 1 relay
    - 2 outputs
    - 2 inputs
    - 3 ADCs
    """

    pass  # Same interface, the firmware handles the differences


# Convenience functions for quick testing
def find_board() -> Optional[str]:
    """Find and return the first Automation 2040 W port, or None."""
    ports = Automation2040W.find_ports()
    return ports[0] if ports else None


def quick_test(port: Optional[str] = None) -> None:
    """
    Quick test of all board features.

    Args:
        port: Serial port, or None to auto-detect.
    """
    print("Automation 2040 W Quick Test")
    print("=" * 40)

    with Automation2040W(port) as board:
        print(f"Connected to: {board.port}")
        print(f"Firmware version: {board.version}")
        print()

        # Get status
        status = board.status()
        print("Current Status:")
        print(f"  Relays:  {status['relays']}")
        print(f"  Outputs: {status['outputs']}")
        print(f"  Inputs:  {status['inputs']}")
        print(f"  ADCs:    {status['adcs']}")
        print(f"  Buttons: A={status['buttons']['a']}, B={status['buttons']['b']}")
        print()

        # Test relay toggle
        print("Testing Relay 1...")
        board.relay(1, True)
        print(f"  Relay 1 ON: {board.relay(1)}")
        time.sleep(0.5)
        board.relay(1, False)
        print(f"  Relay 1 OFF: {board.relay(1)}")
        print()

        # Test output PWM
        print("Testing Output 1 PWM...")
        for pwm in [0, 25, 50, 75, 100, 0]:
            board.output(1, pwm)
            print(f"  Output 1 = {pwm}%")
            time.sleep(0.3)
        print()

        # Read all ADCs
        print("ADC Readings:")
        for i in range(1, 4):
            try:
                voltage = board.adc(i)
                print(f"  ADC {i}: {voltage:.3f}V")
            except CommandError:
                break  # Mini has fewer ADCs
        print()

        # Reset
        board.reset()
        print("Board reset to safe state.")


if __name__ == "__main__":
    import sys

    port = sys.argv[1] if len(sys.argv) > 1 else None
    quick_test(port)
