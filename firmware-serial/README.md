# Firmware: USB Serial

MicroPython firmware for USB serial control of Automation 2040 W.

## Overview

This firmware implements a simple text-based protocol for controlling the Automation 2040 W over USB serial. It's designed to work with the host service running on a Raspberry Pi.

## Features

- Text-based command protocol (human-readable)
- All I/O control (relays, outputs, inputs, ADCs, LEDs, buttons)
- JSON status reporting
- 115200 baud rate
- Auto-response to commands
- Error handling

## Protocol

### Commands

```
RELAY <n> <ON|OFF>      Set relay n (1-3) on or off
RELAY <n>?              Query relay n state
OUTPUT <n> <0-100>      Set output n (1-3), value 0-100 (PWM %)
OUTPUT <n> <ON|OFF>     Set output on/off
OUTPUT <n>?             Query output n state
INPUT <n>?              Query digital input n (1-4)
ADC <n>?                Query ADC n (1-3) voltage
LED <A|B> <0-100>       Set button LED brightness
BUTTON <A|B>?           Query button state
STATUS                  Get all I/O states as JSON
RESET                   Reset all outputs to safe state
VERSION                 Get firmware version
PING                    Test connection (returns PONG)
HELP                    Show available commands
```

### Responses

```
OK                      Command executed successfully
OK <value>              Query result
ERR <message>           Error with description
{...}                   JSON data (for STATUS)
```

### Example Session

```
PING
> OK PONG

RELAY 1 ON
> OK

OUTPUT 1 50
> OK

ADC 1?
> OK 3.456

STATUS
> {"relays":[true,false,false],"outputs":[50,0,0],"inputs":[false,false,false,false],"adcs":[3.456,0.0,0.0],"buttons":{"a":false,"b":false}}
```

## Deployment

### Prerequisites

1. **Pimoroni MicroPython firmware** installed on Automation 2040 W
   - Download from: https://github.com/pimoroni/pimoroni-pico/releases
   - Install `mpremote` tool: `pip install mpremote`

### Installation

```bash
cd firmware-serial
./deploy.sh
```

The script will:
1. Auto-detect the connected board
2. Ask for board type (standard or mini)
3. Upload `main.py` to the board
4. Optionally reset the board

### Manual Installation

```bash
# Connect board and install mpremote
pip install mpremote

# Copy firmware
mpremote cp main.py :main.py

# Reset board
mpremote reset
```

## Testing

### With mpremote REPL

```bash
mpremote repl
```

You should see:
```
# Automation 2040 W Controller v1.0.0
# Relays: 3, Outputs: 3, Inputs: 4, ADCs: 3
# Ready - type HELP for commands
```

Type commands directly:
```
PING
RELAY 1 ON
STATUS
```

### With Python Library

```python
from automation2040w import Automation2040W

with Automation2040W() as board:
    print(board.version)
    board.relay(1, True)
```

## Board Types

The firmware supports both variants:

**Automation 2040 W (Standard)**
- 3 relays
- 3 outputs
- 4 inputs
- 3 ADCs

**Automation 2040 W Mini**
- 1 relay
- 2 outputs
- 2 inputs
- 3 ADCs

Set the board type at the end of `main.py`:
```python
# Change to "mini" for Automation 2040 W Mini
controller = AutomationController(board_type="standard")
```

## Architecture

```
┌─────────────────────────────────┐
│  Automation 2040 W              │
│  ┌───────────────────────────┐  │
│  │  main.py                  │  │
│  │  ├─ Command parser        │  │
│  │  ├─ I/O control           │  │
│  │  └─ Status reporter       │  │
│  └───────────────────────────┘  │
│         ↕ USB Serial             │
└─────────────────────────────────┘
```

## Pin Mapping

The firmware uses the Pimoroni Automation library which handles all pin mappings. Refer to:
https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/automation

## Troubleshooting

### Board not detected

```bash
# List serial ports
mpremote connect list

# Check USB cable (must support data, not just power)
```

### Permission denied (Linux)

```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Firmware not responding

1. Check baud rate is 115200
2. Verify Pimoroni MicroPython is installed
3. Try `mpremote repl` to see error messages
4. Re-upload firmware: `mpremote cp main.py :main.py && mpremote reset`

### Commands not working

- Ensure line endings are `\n` (not `\r\n`)
- Commands are case-insensitive
- Try `PING` first to test connection

## Development

### Modifying the Firmware

1. Edit `main.py` locally
2. Deploy: `./deploy.sh`
3. Test via `mpremote repl`

### Adding New Commands

Add to the `parse_command` method in `AutomationController`:

```python
elif cmd == "NEWCMD":
    self.cmd_newcmd(args)
```

Then implement the handler:

```python
def cmd_newcmd(self, args):
    """Handle NEWCMD command."""
    # Implementation
    self.send_response("OK")
```

## Resources

- [Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico)
- [Automation 2040 W](https://shop.pimoroni.com/products/automation-2040-w)
- [MicroPython Docs](https://docs.micropython.org/)
- [mpremote Tool](https://docs.micropython.org/en/latest/reference/mpremote.html)
