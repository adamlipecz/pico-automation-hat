#!/bin/bash
#
# Update script for Automation 2040 W Host Service
# Updates Python code and systemd service for existing installations
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/.venv"
SERVICE_NAME="automation-service"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "============================================"
echo "  Automation 2040 W Host Service Update"
echo "============================================"
echo

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script must run on Linux (Raspberry Pi)"
    exit 1
fi

# Check if service exists
if [ ! -f "$SYSTEMD_DIR/$SERVICE_NAME.service" ]; then
    echo "❌ Error: Service not found. Please run deploy.sh first."
    exit 1
fi

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

echo "✓ Existing installation found"

# Stop the service if running
echo "Stopping service..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
echo "✓ Service stopped"

# Update Python dependencies
echo "Updating Python dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for package management..."
    cd "$PROJECT_ROOT"
    uv pip install --python "$VENV_DIR/bin/python" -e .
else
    echo "Using pip for package management..."
    "$VENV_DIR/bin/pip" install -e "$PROJECT_ROOT"
fi
echo "✓ Dependencies updated"

# Check if service file has changed
CURRENT_USER=$(whoami)
TEMP_SERVICE="/tmp/$SERVICE_NAME.service"

if [ "$CURRENT_USER" != "pi" ]; then
    sed "s|User=pi|User=$CURRENT_USER|g; s|Group=pi|Group=$CURRENT_USER|g; s|/home/pi/|/home/$CURRENT_USER/|g" \
        "$SERVICE_FILE" > "$TEMP_SERVICE"
    SERVICE_FILE="$TEMP_SERVICE"
fi

# Compare and update service file if changed
if ! cmp -s "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"; then
    echo "Service file has changed, updating..."
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
    sudo systemctl daemon-reload
    echo "✓ Service file updated"
else
    echo "✓ Service file unchanged"
fi

# Restart the service
echo "Starting service..."
sudo systemctl start "$SERVICE_NAME"
echo "✓ Service started"

sleep 2

# Show status
echo
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager || true

echo
echo "============================================"
echo "  ✅ Update complete!"
echo "============================================"
echo
echo "Useful commands:"
echo "  View status:     sudo systemctl status $SERVICE_NAME"
echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo
