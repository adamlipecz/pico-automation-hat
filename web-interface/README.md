# Web Interface

Shared web interface for Automation 2040 W control.

## Overview

This single-page application provides real-time control and monitoring of the Automation 2040 W board. It's used by both deployment options:

- **Host Service** (Raspberry Pi) - Served by Flask
- **WiFi Firmware** (Standalone) - Embedded in MicroPython HTTP server

## Features

- **Real-time I/O display**
  - Relays (clickable toggle)
  - Outputs (clickable toggle)
  - Digital inputs (read-only)
  - Analog inputs (read-only voltage)

- **Connection monitoring**
  - Board connection status
  - MQTT connection status

- **Auto-refresh**
  - Updates every 1 second
  - Visual countdown timer

- **Controls**
  - Toggle relays on/off
  - Toggle outputs on/off
  - Reset all outputs button

## Technical Details

### Implementation

- Single HTML file with inline CSS and JavaScript
- No external dependencies
- Responsive design
- Dark theme

### API Endpoints Used

```
GET  /                    - Web interface
GET  /api/health         - Health check (host only)
GET  /api/status         - Get all I/O states
POST /api/relay/:n       - Control relay N
POST /api/output/:n      - Control output N
POST /api/reset          - Reset all outputs
```

### Styling

- Modern dark theme
- Tailwind-inspired utility classes
- Responsive grid layout
- Interactive hover states
- Color-coded status indicators

## Usage

### Host Service (Raspberry Pi)

The Flask server serves this file directly:

```python
# host/automation_service.py
static_dir = Path(__file__).parent.parent / "web-interface"
flask_app = Flask(__name__, static_folder=str(static_dir))
```

Access: `http://raspberry-pi:8080`

### WiFi Firmware (Standalone)

The MicroPython HTTP server embeds this HTML:

```python
# firmware-wifi/http_server.py
SETTINGS_PAGE = """<!DOCTYPE html>..."""
```

Access: `http://board-ip/`

## Customization

To customize the interface:

1. Edit `index.html`
2. For host service: Restart the service
3. For WiFi firmware: Re-deploy with `cd firmware-wifi && ./deploy.sh`

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript required
- Fetch API required
- No IE11 support
