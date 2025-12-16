#!/bin/bash
#
# Deploy firmware to Automation 2040 W
# Copies all Python files and resets the board
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "  Deploying to Automation 2040 W"
echo "============================================"
echo

# Check for mpremote
if ! command -v mpremote &> /dev/null; then
    echo "❌ mpremote not found. Installing..."
    pip install mpremote
fi

# Check if device is connected
echo "🔍 Looking for device..."
if ! mpremote connect list 2>/dev/null | grep -q .; then
    echo "❌ No device found. Make sure the board is connected via USB."
    exit 1
fi

cd "$SCRIPT_DIR"

echo "📦 Copying files..."

# Create umqtt directory on device
echo "   Creating umqtt package..."
mpremote mkdir :umqtt 2>/dev/null || true

# Copy MQTT library
echo "   umqtt/simple.py"
mpremote cp umqtt/__init__.py :umqtt/__init__.py
mpremote cp umqtt/simple.py :umqtt/simple.py

# Copy main files
echo "   main.py"
mpremote cp main.py :main.py

echo "   config.py"
mpremote cp config.py :config.py

echo "   http_server.py"
mpremote cp http_server.py :http_server.py

echo
echo "🔄 Resetting device..."
mpremote reset

echo
echo "============================================"
echo "  ✅ Deployment complete!"
echo "============================================"
echo
echo "The device will now:"
echo "  1. Connect to WiFi: Check LED A"
echo "  2. Connect to MQTT: Check LED B"
echo "  3. Start HTTP server"
echo
echo "To see debug output:"
echo "  mpremote repl"
echo

