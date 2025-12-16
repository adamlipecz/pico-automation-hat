# Automation 2040 W WiFi Firmware

Standalone WiFi firmware with MQTT and HTTP support. No external server needed!

## Features

- **WiFi auto-connect** - Connects on boot
- **MQTT client** - Publish status, receive commands
- **HTTP settings page** - Configure via web browser
- **Status LEDs** - LED A = WiFi, LED B = MQTT

## Installation

1. Flash the **Pimoroni MicroPython firmware** to your board
2. Copy these files to the board using Thonny:
   - `main.py`
   - `config.py`
   - `http_server.py`
3. Edit `config.py` with your WiFi and MQTT settings (or use the web interface later)
4. Reboot the board

## Configuration

Edit `config.py` or use the web interface:

```python
# WiFi
WIFI_SSID = "YourNetwork"
WIFI_PASSWORD = "YourPassword"

# MQTT
MQTT_BROKER = "192.168.1.28"
MQTT_PORT = 1883
MQTT_TOPIC = "automation"
```

## MQTT Topics

### Published by the device

| Topic | Payload | Description |
|-------|---------|-------------|
| `automation/status` | JSON | All I/O states (every 1s) |
| `automation/input/N` | `HIGH`/`LOW` | Input change event |

**Status payload:**
```json
{
  "relays": [false, false, false],
  "outputs": [0, 0, 0],
  "inputs": [false, false, false, false],
  "adcs": [0.0, 0.0, 0.0],
  "ip": "192.168.1.100"
}
```

### Subscribed by the device

| Topic | Payload | Description |
|-------|---------|-------------|
| `automation/relay/1` | `ON`/`OFF` | Control relay 1 |
| `automation/relay/2` | `ON`/`OFF` | Control relay 2 |
| `automation/relay/3` | `ON`/`OFF` | Control relay 3 |
| `automation/output/1` | `0`-`100` | Set output 1 PWM % |
| `automation/output/2` | `0`-`100` | Set output 2 PWM % |
| `automation/output/3` | `0`-`100` | Set output 3 PWM % |
| `automation/command` | `RESET` | Reset all outputs |
| `automation/command` | `STATUS` | Force status publish |

## HTTP Interface

Access the web interface at `http://<device-ip>/`

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Settings page |
| GET | `/api/status` | JSON status |
| POST | `/api/config` | Update settings |
| POST | `/api/reset` | Reset outputs |
| POST | `/api/relay/N` | Control relay |
| POST | `/api/output/N` | Control output |

## LED Indicators

| LED | Blinking | Solid | Off |
|-----|----------|-------|-----|
| A (WiFi) | Connecting | Connected | Disconnected |
| B (MQTT) | Connecting | Connected | Disconnected |

## Home Assistant Integration

Add to your `configuration.yaml`:

```yaml
mqtt:
  switch:
    - name: "Relay 1"
      command_topic: "automation/relay/1"
      state_topic: "automation/status"
      value_template: "{{ 'ON' if value_json.relays[0] else 'OFF' }}"
      payload_on: "ON"
      payload_off: "OFF"

    - name: "Relay 2"
      command_topic: "automation/relay/2"
      state_topic: "automation/status"
      value_template: "{{ 'ON' if value_json.relays[1] else 'OFF' }}"
      payload_on: "ON"
      payload_off: "OFF"

  sensor:
    - name: "ADC 1"
      state_topic: "automation/status"
      value_template: "{{ value_json.adcs[0] }}"
      unit_of_measurement: "V"

  binary_sensor:
    - name: "Input 1"
      state_topic: "automation/input/1"
      payload_on: "HIGH"
      payload_off: "LOW"
```

## Troubleshooting

### WiFi not connecting
- Check SSID and password in `config.py`
- LED A should blink while connecting
- Access USB serial to see debug messages

### MQTT not connecting
- Verify broker address and port
- Check if broker is reachable from the network
- LED B should blink while connecting

### Can't access web interface
- Check the IP address in serial output
- Try `http://automation2040w.local/` if mDNS is supported

