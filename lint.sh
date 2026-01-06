#!/bin/bash
#
# Lint and type-check all Python code in the project
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "  Code Quality Check"
echo "============================================"
echo

# Find ruff binary
RUFF=""
if command -v ruff &> /dev/null; then
    RUFF="ruff"
elif [ -f "$SCRIPT_DIR/host/.venv/bin/ruff" ]; then
    RUFF="$SCRIPT_DIR/host/.venv/bin/ruff"
else
    echo "❌ Ruff is not installed."
    echo "   Install with: pip install ruff"
    echo "   Or install project dependencies: cd host && ./deploy.sh"
    exit 1
fi

# Find pyright binary
PYRIGHT=""
if command -v pyright &> /dev/null; then
    PYRIGHT="pyright"
elif command -v npx &> /dev/null; then
    PYRIGHT="npx pyright"
else
    echo "⚠️  Pyright not found. Skipping type checking."
    echo "   Install with: npm install -g pyright"
fi

echo "Using ruff: $RUFF"
if [ -n "$PYRIGHT" ]; then
    echo "Using pyright: $PYRIGHT"
fi
echo ""

# Lint host Python code
echo "📋 Linting host/ ..."
$RUFF check host/ --exclude host/.venv

echo ""
echo "🎨 Checking formatting..."
$RUFF format --check host/ --exclude host/.venv

# Lint firmware-wifi Python code
echo ""
echo "📋 Linting firmware-wifi/ ..."
$RUFF check firmware-wifi/ --exclude firmware-wifi/umqtt

# Lint firmware-serial Python code
echo ""
echo "📋 Linting firmware-serial/ ..."
$RUFF check firmware-serial/

# Type checking
if [ -n "$PYRIGHT" ]; then
    echo ""
    echo "🔍 Type checking with pyright..."
    $PYRIGHT host/lib host/service || true  # Don't fail on type errors yet
fi

echo ""
echo "============================================"
echo "  ✅ Quality checks complete!"
echo "============================================"
echo
echo "To auto-fix issues, run:"
echo "  $RUFF check --fix host/ firmware-wifi/ firmware-serial/"
echo "  $RUFF format host/ firmware-wifi/ firmware-serial/"
echo
