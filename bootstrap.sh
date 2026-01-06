#!/bin/bash
#
# Quick bootstrap for Pimoroni Automation 2040 W gateway + tooling
#
# Creates the automation-gateway virtualenv, installs project deps, and prints next steps.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$ROOT/automation-gateway"
VENV_DIR="$GATEWAY_DIR/.venv"

echo "============================================"
echo "  Bootstrap - Automation 2040 W"
echo "============================================"

if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing (Astral)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH=\"$HOME/.cargo/bin:$PATH\"
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv at $VENV_DIR ..."
    uv venv "$VENV_DIR"
else
    echo "✓ Virtualenv exists at $VENV_DIR"
fi

echo "Installing project dependencies (editable + dev)..."
cd "$GATEWAY_DIR"
uv pip install -e ".[dev]"

echo
echo "Next steps:"
echo "  1) Activate venv: source $VENV_DIR/bin/activate"
echo "  2) Run gateway locally: python automation_service.py"
echo "  3) Deploy on Pi: cd $GATEWAY_DIR && ./deploy.sh"
echo "  4) Quality checks: cd $ROOT && ./lint.sh && ./typecheck.sh"
echo
echo "To verify:"
echo "  curl http://localhost:8080/api/health"
echo
echo "============================================"
echo "  ✅ Bootstrap complete"
echo "============================================"
echo
