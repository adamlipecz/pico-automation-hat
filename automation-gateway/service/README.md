# Automation 2040 W Host Service

System service for controlling the Automation 2040 W board over USB serial.

## Features

- Serial communication with Automation 2040 W
- MQTT integration with auto-reconnect
- Web interface for control
- REST API for health monitoring
- Automatic reconnection on disconnects
- systemd service integration

## Installation

Run the deployment script:

```bash
cd service
./deploy.sh
```

This will:
- Create a Python virtual environment
- Install dependencies
- Configure the systemd service
- Create a default configuration file

## Configuration

Edit `service/config.json` to customize:

- Serial port and baud rate
- MQTT broker address and credentials
- HTTP server port
- Logging level

## Usage

```bash
# Start the service
sudo systemctl start automation-service

# Stop the service
sudo systemctl stop automation-service

# Restart the service
sudo systemctl restart automation-service

# View service status
sudo systemctl status automation-service

# View logs
sudo journalctl -u automation-service -f
```

## Updating

To update an existing installation:

```bash
cd service
./update.sh
```

## Web Interface

Access the web interface at `http://[host-ip]:8080/`

## API Endpoints

- `GET /api/health` - Service health check
- `GET /api/status` - Board I/O status
- `POST /api/relay/<num>` - Control relay
- `POST /api/output/<num>` - Control output
- `POST /api/reset` - Reset all outputs
