#!/bin/bash
#
# Deploy script for Automation 2040 W USB Serial Firmware
# Uploads firmware to the Pico board over USB
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOARD_TYPE="standard"  # or "mini"

echo "============================================"
echo "  Automation 2040 W Serial Firmware Deploy"
echo "============================================"
echo

# Check for mpremote
if ! command -v mpremote &> /dev/null; then
    echo "❌ Error: mpremote is not installed"
    echo
    echo "Install with:"
    echo "  pip install mpremote"
    echo "  or"
    echo "  pip3 install mpremote"
    exit 1
fi

echo "✓ mpremote found"

# Detect board
echo
echo "Detecting Pico board..."
DEVICES=$(mpremote connect list 2>/dev/null || true)

if [ -z "$DEVICES" ]; then
    echo "❌ No Pico board detected"
    echo
    echo "Make sure:"
    echo "  1. The Automation 2040 W is connected via USB"
    echo "  2. It's running MicroPython (Pimoroni build recommended)"
    echo "  3. You have permission to access the serial port"
    echo
    echo "On Linux, you may need to add yourself to the dialout group:"
    echo "  sudo usermod -a -G dialout $USER"
    echo "  then log out and back in"
    exit 1
fi

echo "$DEVICES"
echo "✓ Board detected"

# Ask for board type
echo
echo "Select board type:"
echo "  1) Automation 2040 W (standard)"
echo "  2) Automation 2040 W Mini"
read -p "Enter choice [1]: " -r
CHOICE=${REPLY:-1}

if [ "$CHOICE" = "2" ]; then
    BOARD_TYPE="mini"
    echo "Selected: Automation 2040 W Mini"
else
    BOARD_TYPE="standard"
    echo "Selected: Automation 2040 W (standard)"
fi

# Create temporary main.py with correct board type
TEMP_MAIN="/tmp/main_deploy.py"
cp "$SCRIPT_DIR/main.py" "$TEMP_MAIN"

# Update board type in the file
if [ "$BOARD_TYPE" = "mini" ]; then
    sed -i.bak 's/board_type="standard"/board_type="mini"/' "$TEMP_MAIN"
fi

# Upload firmware
echo
echo "Uploading firmware to board..."
echo

mpremote cp "$TEMP_MAIN" :main.py

echo
echo "✓ Firmware uploaded successfully"

# Clean up
rm -f "$TEMP_MAIN" "$TEMP_MAIN.bak"

# Reset board
echo
read -p "Reset board to start firmware? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Resetting board..."
    mpremote reset
    echo "✓ Board reset"
fi

echo
echo "============================================"
echo "  ✅ Deployment complete!"
echo "============================================"
echo
echo "The board is now running USB serial firmware."
echo
echo "Test the connection:"
echo "  python3 -c \"from automation2040w import Automation2040W; print(Automation2040W.find_ports())\""
echo
echo "Or run the quick test:"
echo "  cd ../host && python3 automation2040w.py"
echo
echo "To view serial output:"
echo "  mpremote"
echo
echo "To return to REPL:"
echo "  mpremote repl"
echo
