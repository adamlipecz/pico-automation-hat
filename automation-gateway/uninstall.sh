#!/bin/bash
#
# Uninstall automation gateway service (Automation 2040 W) from this system.
# Stops and disables the systemd unit, removes the unit file, log file, venv, and config.
#

set -euo pipefail

SERVICE_NAME="automation-service"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
CONFIG_DIR="$PROJECT_ROOT/service"
LOG_FILE="/var/log/automation-service.log"

echo "============================================"
echo "  Uninstall Automation Gateway"
echo "============================================"

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping service..."
    sudo systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    echo "Disabling service..."
    sudo systemctl disable "$SERVICE_NAME"
fi

if [ -f "$UNIT_PATH" ]; then
    echo "Removing systemd unit at $UNIT_PATH ..."
    sudo rm -f "$UNIT_PATH"
    sudo systemctl daemon-reload
fi

if [ -f "$LOG_FILE" ]; then
    echo "Removing log file $LOG_FILE ..."
    sudo rm -f "$LOG_FILE"
fi

if [ -d "$VENV_DIR" ]; then
    echo "Removing virtual environment $VENV_DIR ..."
    rm -rf "$VENV_DIR"
fi

if [ -d "$CONFIG_DIR" ]; then
    echo "Removing config directory $CONFIG_DIR ..."
    rm -rf "$CONFIG_DIR"
fi

echo "Uninstall complete."
echo "Repository files remain at $PROJECT_ROOT (safe to delete manually if desired)."
echo "============================================"
