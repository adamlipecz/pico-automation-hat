#!/bin/bash
#
# Deploy script for Automation 2040 W Host Service
# Installs and configures the systemd service on Raspberry Pi
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/.venv"
SERVICE_NAME="automation-service"
SERVICE_FILE="$SCRIPT_DIR/service/$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"
LOG_DIR="/var/log"

echo "============================================"
echo "  Automation 2040 W Host Service Deploy"
echo "============================================"
echo

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script must run on Linux (Raspberry Pi)"
    exit 1
fi

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    echo "❌ Error: Python 3 is required but not found."
    echo "   Install with: sudo apt install python3 python3-venv"
    exit 1
fi

PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Found Python $PY_VERSION"

# Check for uv, install if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Astral package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✓ Using uv for package management"

# Create virtual environment with uv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with uv..."
    uv venv "$VENV_DIR"
else
    echo "✓ Virtual environment exists"
fi

# Install dependencies with uv
echo "Installing dependencies with uv..."
cd "$PROJECT_ROOT"
uv pip install --python "$VENV_DIR/bin/python" -e .

echo "✓ Python dependencies installed"

# Update service file paths if user is not 'pi'
CURRENT_USER=$(whoami)
TEMP_SERVICE="/tmp/$SERVICE_NAME.service"

if [ "$CURRENT_USER" != "pi" ]; then
    echo "Updating service file for user '$CURRENT_USER'..."
    sed "s|User=pi|User=$CURRENT_USER|g; s|Group=pi|Group=$CURRENT_USER|g; s|/home/pi/|/home/$CURRENT_USER/|g" \
        "$SERVICE_FILE" > "$TEMP_SERVICE"
    SERVICE_FILE="$TEMP_SERVICE"
fi

# Install systemd service
echo
echo "Installing systemd service..."
if [ -f "$SYSTEMD_DIR/$SERVICE_NAME.service" ]; then
    echo "Service already exists. Stopping it first..."
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
fi

sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
sudo systemctl daemon-reload

echo "✓ Service file installed"

# Create default config if it doesn't exist
CONFIG_FILE="$SCRIPT_DIR/service/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_FILE" <<EOF
{
  "serial": {
    "port": null,
    "baudrate": 115200,
    "reconnect_interval": 5
  },
  "mqtt": {
    "broker": "192.168.1.28",
    "port": 1883,
    "topic_prefix": "automation",
    "client_id": "automation2040w-host",
    "username": "",
    "password": "",
    "publish_interval": 1,
    "reconnect_interval": 15
  },
  "http": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/automation-service.log"
  }
}
EOF
    echo "✓ Default config created at $CONFIG_FILE"
    echo "  Edit this file to customize settings"
fi

# Create log file with correct permissions
LOG_FILE="/var/log/automation-service.log"
sudo touch "$LOG_FILE"
sudo chown "$CURRENT_USER:$CURRENT_USER" "$LOG_FILE"
echo "✓ Log file created at $LOG_FILE"

# Ask if user wants to enable and start the service
echo
read -p "Enable service to start on boot? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable "$SERVICE_NAME"
    echo "✓ Service enabled"
fi

read -p "Start service now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start "$SERVICE_NAME"
    echo "✓ Service started"

    sleep 2

    # Show status
    echo
    echo "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager || true
fi

echo
echo "============================================"
echo "  ✅ Deployment complete!"
echo "============================================"
echo
echo "Useful commands:"
echo "  Start service:   sudo systemctl start $SERVICE_NAME"
echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  View status:     sudo systemctl status $SERVICE_NAME"
echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "  Enable on boot:  sudo systemctl enable $SERVICE_NAME"
echo "  Disable on boot: sudo systemctl disable $SERVICE_NAME"
echo
echo "Configuration file: $CONFIG_FILE"
echo "Web interface:      http://localhost:8080"
echo "Health API:         http://localhost:8080/api/health"
echo
