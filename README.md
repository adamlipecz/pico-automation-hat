# Pimoroni Automation 2040 W USB Control

Control your [Pimoroni Automation 2040 W](https://shop.pimoroni.com/products/automation-2040-w) over USB from any computer using a simple text-based protocol.

## Features

- **Simple text protocol** - Human-readable commands, easy to debug with any serial terminal
- **Full peripheral control** - Relays, outputs (PWM), inputs, ADCs, button LEDs
- **Python host library** - Easy integration into your automation projects
- **Cross-platform** - Works on Windows, macOS, Linux
- **No special drivers** - Uses standard USB CDC (virtual COM port)
- **Two firmware options** - MicroPython or C++

## Hardware Support

| Board | Relays | Outputs | Inputs | ADCs |
|-------|--------|---------|--------|------|
| Automation 2040 W | 3 | 3 | 4 | 3 |
| Automation 2040 W Mini | 1 | 2 | 2 | 3 |

## Quick Start

### 1. Choose & Install Firmware

You have two firmware options - both implement the same protocol and work with the host library:

#### Option A: MicroPython (Easier)

1. Download the [Pimoroni MicroPython firmware](https://github.com/pimoroni/pimoroni-pico/releases) (.uf2 file)
2. Flash it to your board (hold BOOTSEL, connect USB, copy the .uf2 file)
3. Copy `firmware-python/main.py` to the board using [Thonny](https://thonny.org/)

#### Option B: C++ (Better performance)

1. Install prerequisites (see `firmware-cpp/README.md`)
2. Build the firmware:
   ```bash
   cd firmware-cpp
   mkdir build && cd build
   cmake ..
   make -j4
   ```
3. Flash `automation2040w_usb.uf2` to the board (hold BOOTSEL, connect USB, copy file)

### 2. Install Host Library

```bash
cd host
pip install -r requirements.txt
```

### 3. Connect and Control

```python
from automation2040w import Automation2040W

# Auto-detect and connect
board = Automation2040W()

# Control relays
board.relay(1, True)   # Turn on
board.relay(1, False)  # Turn off

# PWM outputs (0-100%)
board.output(1, 50)    # 50% duty cycle

# Read inputs
if board.input(1):
    print("Input 1 is HIGH")

# Read ADC voltage
voltage = board.adc(1)
print(f"ADC 1: {voltage:.2f}V")

# Get all states at once
status = board.status()
print(status)
```

## Protocol Reference

The protocol uses simple ASCII commands over USB serial (115200 baud). Commands are newline-terminated.

### Command Format

```
COMMAND [args...]     → OK [response]
COMMAND [args...]     → ERR message
QUERY?                → OK value
```

### Commands

| Command | Description | Response |
|---------|-------------|----------|
| `RELAY n ON/OFF` | Set relay n (1-3) | `OK` |
| `RELAY n?` | Query relay state | `OK ON` or `OK OFF` |
| `OUTPUT n 0-100` | Set output PWM % | `OK` |
| `OUTPUT n ON/OFF` | Set output full on/off | `OK` |
| `OUTPUT n?` | Query output value | `OK 50` (percentage) |
| `INPUT n?` | Query input state | `OK HIGH` or `OK LOW` |
| `ADC n?` | Query ADC voltage | `OK 12.345` (volts) |
| `LED A/B 0-100` | Set button LED brightness | `OK` |
| `BUTTON A/B?` | Query button state | `OK PRESSED/RELEASED` |
| `STATUS` | Get all states as JSON | `{...}` |
| `RESET` | Reset outputs to safe state | `OK` |
| `VERSION` | Get firmware version | `OK 1.0.0` |
| `PING` | Test connection | `OK PONG` |
| `HELP` | Show available commands | ... |

### Testing with Serial Terminal

You can test directly with any serial terminal:

```bash
# Linux/macOS
screen /dev/ttyACM0 115200

# Or use minicom, picocom, etc.
```

Then type commands:
```
PING
> OK PONG

RELAY 1 ON
> OK

ADC 1?
> OK 3.456

STATUS
> {"relays":[true,false,false],"outputs":[0,0,0],"inputs":[false,false,false,false],"adcs":[3.456,0.0,0.0],"buttons":{"a":false,"b":false}}
```

## Examples

See the `host/examples/` directory:

- **basic_control.py** - Simple demo of all features
- **monitor.py** - Continuously display all I/O states
- **sequencer.py** - Cycle through relays in sequence

## Project Structure

```
pico-automation-hat/
├── firmware-python/
│   └── main.py              # MicroPython firmware
├── firmware-cpp/
│   ├── src/
│   │   └── main.cpp         # C++ firmware
│   ├── CMakeLists.txt
│   └── README.md            # Build instructions
├── host/
│   ├── automation2040w.py   # Python control library
│   ├── requirements.txt     # Python dependencies
│   └── examples/
│       ├── basic_control.py
│       ├── monitor.py
│       └── sequencer.py
└── README.md
```

## Firmware Comparison

| Aspect | MicroPython | C++ |
|--------|-------------|-----|
| **Setup** | Easy - copy .py file | Requires SDK & build |
| **Performance** | Good | Excellent |
| **Response time** | ~1-5ms | <1ms |
| **Customization** | Edit .py on device | Recompile & flash |
| **Dependencies** | Pimoroni firmware | Pico SDK + Pimoroni libs |

Both firmwares use the **same protocol** and work with the **same host library**.

## Why Not MODBUS?

MODBUS is a great protocol for industrial networks with multiple devices, but for a single device controlled over USB:

| Aspect | Simple Text Protocol | MODBUS RTU |
|--------|---------------------|------------|
| Implementation | ~200 lines | 500+ lines |
| Debugging | Any terminal | Needs MODBUS tools |
| Learning curve | Minutes | Hours |
| Human readable | Yes | No (binary) |
| CRC overhead | None | Required |
| Best for | Single device, USB | Multi-device, RS-485 |

If you need MODBUS compatibility for integration with existing systems, it can be added as an alternative protocol mode.

## Troubleshooting

### Board not detected

1. Check USB cable supports data (not charge-only)
2. Verify firmware is installed and running
3. For MicroPython: connect with Thonny, check `main.py` is present
4. For C++: ensure the .uf2 was copied successfully

### Permission denied (Linux)

Add yourself to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Commands not working

1. Check baud rate is 115200
2. Ensure line endings are `\n` (not `\r\n`)
3. Try `PING` first to test connection

## License

MIT License - Feel free to use in your projects!

## Links

- [Pimoroni Automation 2040 W](https://shop.pimoroni.com/products/automation-2040-w)
- [Pimoroni MicroPython Examples](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/automation2040w)
- [Pimoroni Firmware Releases](https://github.com/pimoroni/pimoroni-pico/releases)
- [Pico SDK](https://github.com/raspberrypi/pico-sdk)
- [Pimoroni Pico Libraries](https://github.com/pimoroni/pimoroni-pico)
