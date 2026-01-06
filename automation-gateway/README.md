# Automation Gateway Service (Pimoroni Automation 2040 W)

Raspberry Pi automation gateway for the Pimoroni Automation 2040 W: USB serial to MQTT/REST/web UI bridge with systemd integration.

## Overview

This Python service runs on a Raspberry Pi and provides:
- USB serial communication with the board
- MQTT client integration
- REST API
- Web interface hosting
- systemd integration
- Health monitoring

See main project [README](../README.md) and [SETUP](../SETUP.md) for end-to-end guides and FAQs.

## Architecture

```
┌─────────────────────────────────────┐
│    Raspberry Pi 5 (Gateway)         │
│  ┌───────────────────────────────┐  │
│  │  automation_service.py        │  │
│  │  ├─ Flask (:8080)             │  │
│  │  ├─ MQTT Client               │  │
│  │  └─ Serial (USB)              │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ USB Serial
               ↓
    ┌──────────────────────┐
    │ Automation 2040 W    │
    │ (automation-firmware-serial)    │
    └──────────────────────┘
```

## Files

- `automation2040w.py` - Serial communication library
- `automation_service.py` - Main service (MQTT + HTTP + systemd)
- `automation-service.service` - systemd unit file
- `service/config.json` - Configuration (created on first run)
- `deploy.sh` - Installation script
- `requirements.txt` - Python dependencies
- `examples/` - Usage examples

## Quick Start

### Installation

```bash
# On Raspberry Pi
cd automation-gateway
./deploy.sh
```

This will:
1. Install uv package manager
2. Create virtual environment
3. Install dependencies
4. Configure systemd service
5. Copy `service/config.json.example` to `service/config.json` if missing

### Configuration

Edit `service/config.json` (template in `service/config.json.example`):

```json
{
  "serial": {
    "port": null,              // null = auto-detect
    "baudrate": 115200,
    "reconnect_interval": 5
  },
  "mqtt": {
    "broker": "192.168.1.28",
    "port": 1883,
    "topic_prefix": "automation",
    "username": "",
    "password": ""
  },
  "http": {
    "host": "0.0.0.0",
    "port": 8080
  }
}
```

### Service Management

```bash
# Start/stop
sudo systemctl start automation-service
sudo systemctl stop automation-service

# Enable/disable on boot
sudo systemctl enable automation-service
sudo systemctl disable automation-service

# View logs
sudo journalctl -u automation-service -f

# Status
sudo systemctl status automation-service
```

### Quick verification

```bash
# Health
curl http://localhost:8080/api/health

# Toggle relay 1
curl -X POST -H "Content-Type: application/json" -d '{"state": true}' \
  http://localhost:8080/api/relay/1

# Watch MQTT status
mosquitto_sub -h <broker-ip> -t automation/status
```

## REST API

### Health Check
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "board_connected": true,
  "mqtt_connected": true,
  "error_count": 0
}
```

### Get Status
```bash
GET /api/status

Response:
{
  "relays": [false, false, false],
  "outputs": [0, 50, 100],
  "inputs": [true, false, true, false],
  "adcs": [2.4, 12.3, 0.0],
  "buttons": {"a": false, "b": false}
}
```

### Control Relay
```bash
POST /api/relay/1
Content-Type: application/json

{"state": true}
```

### Control Output
```bash
POST /api/output/1
Content-Type: application/json

{"value": 75}
```

### Reset All
```bash
POST /api/reset
```

## MQTT Topics

### Subscribe (commands)
- `automation/relay/N` - Set relay (1-3): "ON" or "OFF"
- `automation/output/N` - Set output (1-3): 0-100 or "ON"/"OFF"
- `automation/command` - Commands: "RESET", "STATUS"

### Publish (status)
- `automation/status` - JSON with all I/O states (every 1 second)

## Python Library Usage

```python
from automation2040w import Automation2040W

# Auto-detect and connect
with Automation2040W() as board:
    print(f"Firmware: {board.version}")

    # Control
    board.relay(1, True)
    board.output(1, 50)

    # Read
    if board.input(1):
        print("Input 1 is HIGH")

    voltage = board.adc(1)
    print(f"ADC 1: {voltage:.2f}V")

    # Get all states
    status = board.status()
    print(status)
```

## Troubleshooting

### Board not detected
```bash
# Find ports
python3 -c "from automation2040w import Automation2040W; print(Automation2040W.find_ports())"

# Check permissions
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Service won't start
```bash
# Check logs
sudo journalctl -u automation-service -xe

# Verify config
cat service/config.json | python3 -m json.tool

# Test manually
cd automation-gateway
source .venv/bin/activate
python3 automation_service.py
```

### MQTT issues
```bash
# Test broker
ping 192.168.1.28

# Subscribe to topics
mosquitto_sub -h 192.168.1.28 -t automation/#
```

## Development

```bash
# Install for development
cd ..
make install

# Lint
make lint

# Format
make format

# Run directly
cd automation-gateway
source .venv/bin/activate
python3 automation_service.py
```

## Dependencies

- Python 3.9+
- pyserial - Serial communication
- flask - HTTP server
- paho-mqtt - MQTT client

Managed with `uv` package manager for fast, reliable installs.
