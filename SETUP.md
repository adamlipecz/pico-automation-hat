# Pimoroni Automation 2040 W Setup Guide

End-to-end setup for the Pimoroni Automation 2040 W using the automation gateway (Raspberry Pi) or WiFi firmware (MicroPython). See the main [README](README.md) for features and FAQs.

This project provides multiple ways to control the Pimoroni Automation 2040 W board:

1. **USB Serial Control** (via Raspberry Pi automation gateway)
2. **WiFi Direct Control** (standalone, no gateway required)

## Architecture Overview

### USB Serial Setup (Recommended for Raspberry Pi)
```
┌─────────────────────────────────────────────┐
│         Raspberry Pi 5 (Gateway)            │
│  ┌─────────────────────────────────────┐   │
│  │   automation_service.py             │   │
│  │   - Serial → USB to Pico            │   │
│  │   - MQTT Client (pub/sub)           │   │
│  │   - Flask REST API (:8080)          │   │
│  │   - Web Interface                   │   │
│  │   - Systemd Service                 │   │
│  └─────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │ USB Serial
                   ↓
        ┌──────────────────────┐
        │ Automation 2040 W    │
        │ automation-firmware-serial      │
        │ - Command protocol   │
        │ - I/O control        │
        └──────────────────────┘
```

**Benefits:**
- Centralized MQTT handling on powerful Raspberry Pi
- Auto-reconnect and error handling
- Health monitoring API
- Single web interface for control
- Runs as systemd service

### WiFi Direct Setup (Standalone)
```
        ┌──────────────────────┐
        │ Automation 2040 W    │
        │ automation-firmware-wifi        │
        │ - WiFi client        │
        │ - MQTT client        │
        │ - HTTP server        │
        │ - Web interface      │
        └──────────────────────┘
```

**Benefits:**
- No gateway computer needed
- Direct WiFi connectivity
- Standalone operation
- Good for remote/isolated deployments

---

## Setup: USB Serial (Raspberry Pi Automation Gateway)

### Step 1: Flash automation-firmware-serial to Automation 2040 W

1. Connect the Automation 2040 W to your computer via USB
2. Install mpremote:
   ```bash
   pip3 install mpremote
   ```

3. Deploy the firmware:
   ```bash
   cd automation-firmware-serial
   ./deploy.sh
   ```

4. Select your board type (standard or mini) when prompted

### Step 2: Setup Raspberry Pi Automation Gateway Service

1. Clone this repo on your Raspberry Pi 5:
   ```bash
   cd ~
   git clone <repo-url> pico-automation-hat
   cd pico-automation-hat/automation-gateway
   ```

2. Run the deploy script:
   ```bash
   ./deploy.sh
   ```

   This will:
   - Install uv package manager (if not present)
   - Create a Python virtual environment with uv
   - Install dependencies (pyserial, flask, paho-mqtt)
   - Install systemd service
   - Copy `service/config.json.example` to `service/config.json` if missing
   - Optionally enable and start the service

3. Edit configuration if needed (source of truth: `service/config.json.example`):
   ```bash
   nano service/config.json
   ```

   Key settings:
   - `mqtt.broker`: Your MQTT broker address
   - `mqtt.topic_prefix`: MQTT topic prefix (default: "automation")
   - `http.port`: Web interface port (default: 8080)
   - `serial.port`: Serial port (null = auto-detect)

4. Restart the service after config changes:
   ```bash
   sudo systemctl restart automation-service
   ```

### Step 3: Connect the Board

1. Connect Automation 2040 W to Raspberry Pi via USB
2. The service will auto-detect and connect
3. Check the logs:
   ```bash
   sudo journalctl -u automation-service -f
   ```

### Step 4: Access the Interface

- **Web Interface:** http://raspberry-pi-ip:8080
- **Health Check:** http://raspberry-pi-ip:8080/api/health
- **Board Status:** http://raspberry-pi-ip:8080/api/status

### Quick verification (gateway)

```bash
# Health
curl http://raspberry-pi-ip:8080/api/health

# Toggle relay 1
curl -X POST -H "Content-Type: application/json" -d '{"state": true}' \
  http://raspberry-pi-ip:8080/api/relay/1

# MQTT status stream
mosquitto_sub -h <broker-ip> -t automation/status
```

### MQTT Topics (USB Serial Setup)

The automation gateway service publishes and subscribes to these topics:

**Subscribe (commands):**
- `automation/relay/N` - Set relay N (1-3): "ON" or "OFF"
- `automation/output/N` - Set output N (1-3): 0-100 or "ON"/"OFF"
- `automation/command` - Commands: "RESET", "STATUS"

**Publish (status):**
- `automation/status` - JSON with all I/O states (every 1 second)

---

## Setup: WiFi Direct (Standalone)

### Step 1: Configure WiFi Settings

1. Edit the WiFi credentials in [automation-firmware-wifi/main.py](automation-firmware-wifi/main.py):
   ```python
   class config:
       WIFI_SSID = "your-wifi-name"
       WIFI_PASSWORD = "your-wifi-password"
       MQTT_BROKER = "192.168.1.28"
       MQTT_PORT = 1883
       MQTT_TOPIC = "automation"
   ```

   Or create a `config.py` file in the automation-firmware-wifi directory.

### Step 2: Deploy WiFi Firmware

1. Connect the Automation 2040 W via USB
2. Deploy:
   ```bash
   cd automation-firmware-wifi
   ./deploy.sh
   ```

### Step 3: Find the Board

1. Check your router's DHCP list for the board's IP
2. Or watch the serial output:
   ```bash
   mpremote repl
   ```

   Look for: "Connected! IP: 192.168.x.x"

### Step 4: Access the Web Interface

- Navigate to: http://board-ip-address/
- The interface shows real-time I/O status
- Click relays/outputs to toggle them

### MQTT Topics (WiFi Direct)

Same as USB Serial setup, but MQTT handled by the board itself.

---

## Useful Commands

### Service Management (USB Serial)
```bash
# Start/stop service
sudo systemctl start automation-service
sudo systemctl stop automation-service
sudo systemctl restart automation-service

# Enable/disable on boot
sudo systemctl enable automation-service
sudo systemctl disable automation-service

# View status
sudo systemctl status automation-service

# View logs
sudo journalctl -u automation-service -f
sudo journalctl -u automation-service --since "1 hour ago"
```

### Board Management
```bash
# View serial output (any firmware)
mpremote repl

# Upload single file
mpremote cp file.py :file.py

# List files on board
mpremote ls

# Reset board
mpremote reset

# Find serial ports
python3 -c "from automation2040w import Automation2040W; print(Automation2040W.find_ports())"
```

### Testing the Automation Gateway Python Library
```bash
# Using make (recommended)
make install  # Install with uv
cd automation-gateway/examples && python3 basic_control.py

# Or manually
cd automation-gateway
source .venv/bin/activate
python3 automation2040w.py
```

### Development Commands
```bash
# Format code
make format

# Lint code
make lint

# Deploy to devices
make deploy-gateway  # Deploy automation gateway service
make deploy-serial   # Deploy serial firmware
make deploy-wifi     # Deploy WiFi firmware
```

---

## Troubleshooting

### USB Serial Issues

**Board not detected:**
- Check USB cable is connected
- Verify automation-firmware-serial is installed: `mpremote ls` should show main.py
- Check permissions: `sudo usermod -a -G dialout $USER` (then log out/in)
- Try specifying port in config: `"serial.port": "/dev/ttyACM0"`

**Service won't start:**
- Check logs: `sudo journalctl -u automation-service -f`
- Verify Python dependencies: `cd automation-gateway && source .venv/bin/activate && pip list`
- Check config syntax: `cat service/config.json | python3 -m json.tool`

**MQTT not connecting:**
- Verify broker address: `ping 192.168.1.28`
- Check MQTT broker is running
- Test with mosquitto: `mosquitto_sub -h 192.168.1.28 -t automation/#`

### WiFi Direct Issues

**Board not connecting to WiFi:**
- Verify SSID and password in automation-firmware-wifi/main.py
- Check WiFi signal strength
- View debug output: `mpremote repl`
- LED A blinks = connecting, solid = connected

**Can't access web interface:**
- Find IP address from router or `mpremote repl`
- Check firewall settings
- Try: `curl http://board-ip/api/status`

**MQTT not working:**
- Check broker address is reachable from board's network
- Verify broker allows connections from board's IP
- Watch debug output: `mpremote repl`

---

## File Structure

```
pico-automation-hat/
├── automation-firmware-serial/          # USB serial control firmware
│   ├── main.py              # Command protocol implementation
│   └── deploy.sh            # Deployment script
│
├── automation-firmware-wifi/           # WiFi standalone firmware
│   ├── main.py             # Main controller with WiFi & MQTT
│   ├── http_server.py      # HTTP server and web interface
│   ├── index.html          # Web UI (also used by automation gateway)
│   └── deploy.sh           # Deployment script
│
├── automation-gateway/                    # Raspberry Pi automation gateway service
│   ├── automation2040w.py  # Python library for serial control
│   ├── automation_service.py  # Main service (MQTT, HTTP, serial)
│   ├── service/config.json    # Configuration file
│   ├── automation-service.service  # Systemd unit file
│   ├── requirements.txt    # Python dependencies
│   ├── deploy.sh          # Service deployment script
│   └── examples/          # Usage examples
│
└── SETUP.md              # This file
```

---

## API Reference

### REST API Endpoints (USB Serial Host)

**Health Check:**
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "board_connected": true,
  "mqtt_connected": true,
  "error_count": 0,
  "last_update": "2024-01-01T12:00:00"
}
```

**Get Status:**
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

**Control Relay:**
```bash
POST /api/relay/1
Content-Type: application/json

{"state": true}
```

**Control Output:**
```bash
POST /api/output/1
Content-Type: application/json

{"value": 75}
```

**Reset All:**
```bash
POST /api/reset
```

---

## Configuration Reference

### service/config.json

```json
{
  "serial": {
    "port": null,              // null = auto-detect, or "/dev/ttyACM0"
    "baudrate": 115200,
    "reconnect_interval": 5    // seconds
  },
  "mqtt": {
    "broker": "192.168.1.28",
    "port": 1883,
    "topic_prefix": "automation",
    "client_id": "automation2040w-gateway",
    "username": "",            // Optional
    "password": "",            // Optional
    "publish_interval": 1,     // seconds
    "reconnect_interval": 15   // seconds
  },
  "http": {
    "host": "0.0.0.0",        // Listen on all interfaces
    "port": 8080
  },
  "logging": {
    "level": "INFO",          // DEBUG, INFO, WARNING, ERROR
    "file": "/var/log/automation-service.log"
  }
}
```

---

## License

MIT License - See individual files for details.

## Support

For issues and questions, please check:
- Project documentation
- Example scripts in automation-gateway/examples/
- Serial output via `mpremote repl`
- Service logs via `journalctl`
