#!/bin/bash
#
# Setup script for Automation 2040 W Host Library
# Creates a virtual environment and installs dependencies
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "============================================"
echo "  Automation 2040 W Host Library Setup"
echo "============================================"
echo

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Error: Python 3 is required but not found."
    echo "   Please install Python 3.8 or later."
    exit 1
fi

# Verify Python version
PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PY_VERSION"

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        echo "Creating new virtual environment..."
        $PYTHON -m venv "$VENV_DIR"
    fi
else
    echo "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

echo
echo "============================================"
echo "  ✅ Setup complete!"
echo "============================================"
echo
echo "To activate the environment:"
echo "  source $VENV_DIR/bin/activate"
echo
echo "To test the connection:"
echo "  python -c \"from automation2040w import Automation2040W; print(Automation2040W.find_ports())\""
echo
echo "To run an example:"
echo "  cd examples && python basic_control.py"
echo
echo "To deactivate when done:"
echo "  deactivate"
echo

