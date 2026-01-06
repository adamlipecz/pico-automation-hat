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
elif [ -f "$SCRIPT_DIR/automation-gateway/.venv/bin/ruff" ]; then
    RUFF="$SCRIPT_DIR/automation-gateway/.venv/bin/ruff"
else
    echo "❌ Ruff is not installed."
    echo "   Install with: pip install ruff"
    echo "   Or install project dependencies: cd automation-gateway && ./deploy.sh"
    exit 1
fi

# Find Astral Ty binary
TY_CANDIDATES=(
    "astral-ty"
    "ty"
    "$SCRIPT_DIR/automation-gateway/.venv/bin/astral-ty"
    "$SCRIPT_DIR/automation-gateway/.venv/bin/ty"
    "$HOME/.venv/bin/astral-ty"
    "$HOME/.venv/bin/ty"
)

TY_BIN=""
for cand in "${TY_CANDIDATES[@]}"; do
    if command -v "$cand" &> /dev/null; then
        TY_BIN="$cand"
        break
    elif [ -x "$cand" ]; then
        TY_BIN="$cand"
        break
    fi
done

if [ -z "$TY_BIN" ]; then
    echo "⚠️  Astral Ty not found. Skipping type checking."
    echo "   Install with: uv pip install ty"
fi

echo "Using ruff: $RUFF"
if [ -n "$TY_BIN" ]; then
    echo "Using Astral Ty: $TY_BIN"
fi
echo ""

# Lint automation gateway Python code
echo "📋 Linting automation-gateway/ ..."
$RUFF check automation-gateway/ --exclude automation-gateway/.venv

echo ""
echo "🎨 Checking formatting..."
$RUFF format --check automation-gateway/ --exclude automation-gateway/.venv

# Lint automation-firmware-wifi Python code
echo ""
echo "📋 Linting automation-firmware-wifi/ ..."
$RUFF check automation-firmware-wifi/ --exclude automation-firmware-wifi/umqtt

# Lint automation-firmware-serial Python code
echo ""
echo "📋 Linting automation-firmware-serial/ ..."
$RUFF check automation-firmware-serial/

# Type checking
if [ -n "$TY_BIN" ]; then
    echo ""
    echo "🔍 Type checking with Astral Ty..."
    $TY_BIN check automation-gateway/lib automation-gateway/service || true  # Don't fail on type errors yet
fi

echo ""
echo "============================================"
echo "  ✅ Quality checks complete!"
echo "============================================"
echo
echo "To auto-fix issues, run:"
echo "  $RUFF check --fix automation-gateway/ automation-firmware-wifi/ automation-firmware-serial/"
echo "  $RUFF format automation-gateway/ automation-firmware-wifi/ automation-firmware-serial/"
echo
