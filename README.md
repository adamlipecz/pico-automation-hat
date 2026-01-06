# Pimoroni Automation 2040 W Control System

Raspberry Pi + MicroPython automation stack for the [Pimoroni Automation 2040 W](https://shop.pimoroni.com/products/automation-2040-w). Ships with MQTT, REST, and a responsive web UI so you can drop it into home-automation, lab control, or industrial monitoring projects fast.

## Features

- **USB Serial Control** - Automation gateway (Raspberry Pi) with MQTT, REST API, and web interface
- **WiFi Standalone** - Direct WiFi operation with built-in MQTT and web server
- **Simple text protocol** - Human-readable commands, easy to debug
- **Full peripheral control** - Relays, outputs (PWM), inputs, ADCs, button LEDs
- **Python gateway library** - Easy integration into automation projects
- **Modern tooling** - uv for packages, ruff for linting, Astral Ty for type checking, systemd integration
- **Cloud-ready** - MQTT-first design, REST health checks, and API endpoints suited for dashboards and IoT brokers

## Use Cases

- Raspberry Pi gateway for Home Assistant, Node-RED, or Grafana dashboards
- MQTT bridge for lab equipment and sensor logging
- Local-only industrial controls where offline operation matters
- Fast prototyping for Pimoroni Automation 2040 W and Automation 2040 W Mini

## Hardware Support

| Board | Relays | Outputs | Inputs | ADCs |
|-------|--------|---------|--------|------|
| Automation 2040 W | 3 | 3 | 4 | 3 |
| Automation 2040 W Mini | 1 | 2 | 2 | 3 |

## Architecture Options

### Option 1: USB Serial with Raspberry Pi Automation Gateway (Recommended)

```
Raspberry Pi 5 ──USB──> Automation 2040 W
     │
     ├─ MQTT Client (publishes/subscribes)
     ├─ REST API (:8080)
     └─ Web Interface
```

**Best for:** Centralized control, advanced features, reliable MQTT

### Option 2: WiFi Standalone

```
Automation 2040 W (WiFi + MQTT + HTTP server)
```

**Best for:** Simple deployments, no gateway computer needed

## Quick Start

### USB Serial Setup (Raspberry Pi)

See **[SETUP.md](SETUP.md)** for detailed instructions.

**Quick version:**

1. Flash firmware to board:
   ```bash
   cd automation-firmware-serial && ./deploy.sh
   ```

2. Deploy automation gateway service on Raspberry Pi:
   ```bash
   cd automation-gateway && ./deploy.sh
   ```

3. Access web interface: `http://raspberry-pi-ip:8080`

### WiFi Standalone Setup

1. Edit WiFi config in `automation-firmware-wifi/main.py`
2. Deploy:
   ```bash
   cd automation-firmware-wifi && ./deploy.sh
   ```
3. Access web interface at board's IP address

## Development

### Setup development environment:

```bash
# Install uv package manager (auto-installed by deploy.sh)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install

# Lint code
make lint

# Format code
make format

# Type check everything with Astral Ty
./typecheck.sh
```

### VSCode Setup

The project includes VSCode configuration for automatic linting and formatting:

1. Install recommended extensions (VSCode will prompt):
   - **Astral Ty** CLI available via `uv pip install astral-ty` (used by `typecheck.sh`)
   - **Ruff** - Fast Python linter and formatter
   - **Python** - Python language support
   - **Pylance** - Python language server

2. Ruff will automatically:
   - Format code on save
   - Organize imports
   - Show linting errors in real-time
   - Fix issues automatically where possible

3. The Python interpreter is automatically set to `automation-gateway/.venv/bin/python`

### Using the Python Library

```python
from automation2040w import Automation2040W

with Automation2040W() as board:
    print(f"Firmware: {board.version}")

    # Control relays
    board.relay(1, True)

    # PWM outputs (0-100%)
    board.output(1, 50)

    # Read inputs
    if board.input(1):
        print("Input 1 is HIGH")

    # Read ADC voltage
    voltage = board.adc(1)
    print(f"ADC 1: {voltage:.2f}V")

    # Get all states
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

See the `automation-gateway/examples/` directory:

- **basic_control.py** - Simple demo of all features
- **monitor.py** - Continuously display all I/O states
- **sequencer.py** - Cycle through relays in sequence

## Project Structure

```
pico-automation-hat/
├── automation-firmware-serial/          # USB serial firmware (INDEPENDENT)
│   ├── main.py              # MicroPython implementation
│   ├── deploy.sh            # Deployment script
│   └── README.md            # Firmware-specific docs
├── automation-firmware-wifi/           # WiFi standalone firmware (INDEPENDENT)
│   ├── main.py             # Controller with WiFi & MQTT
│   ├── http_server.py      # Web server
│   ├── deploy.sh           # Deployment script
│   └── README.md            # Firmware-specific docs
├── automation-gateway/                    # Raspberry Pi automation gateway service (INDEPENDENT)
│   ├── automation2040w.py  # Serial control library
│   ├── automation_service.py  # Main service (MQTT/HTTP/systemd)
│   ├── automation-service.service  # Systemd unit
│   ├── deploy.sh           # Service installer
│   ├── examples/           # Usage examples
│   └── README.md            # Host-specific docs
├── web-interface/           # Shared web UI (used by gateway & wifi)
│   ├── index.html          # Single-page application
│   └── README.md            # UI documentation
├── pyproject.toml          # Project config (uv/ruff)
├── Makefile                # Development commands
├── README.md               # This file
├── SETUP.md                # Detailed setup guide
└── ARCHITECTURE.md         # Architecture comparison
```

**Note:** Each folder (automation-firmware-serial, automation-firmware-wifi, automation-gateway) is **independent** with its own README. The web-interface folder is shared between gateway and WiFi deployments.

## Deployment Options Comparison

| Aspect | USB Serial + Automation Gateway | WiFi Standalone |
|--------|------------------|-----------------|
| **Gateway required** | Yes (Raspberry Pi) | No |
| **MQTT reliability** | Excellent | Good |
| **Auto-reconnect** | Yes (gateway handles) | Yes (board handles) |
| **Web interface** | Flask (powerful) | MicroPython (basic) |
| **Health monitoring** | REST API | Limited |
| **Logging** | systemd/journald | Serial output |
| **Best for** | Production | Simple setups |

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
