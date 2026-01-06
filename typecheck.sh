#!/bin/bash
#
# Run Astral Ty type checking across all Python projects in the repo
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "  Astral Ty - Type Checking"
echo "============================================"
echo

# Locate Astral Ty binary
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
    if [ "${ALLOW_MISSING_TY:-0}" = "1" ]; then
        echo "⚠️  Astral Ty not found. Skipping type checking."
        echo "   Install with: uv pip install ty"
        exit 0
    else
        echo "❌ Astral Ty is not installed."
        echo "   Install with: uv pip install ty"
        exit 1
    fi
fi

echo "Using Astral Ty: $TY_BIN"
echo

TARGETS=(
    "automation-gateway/lib"
    "automation-gateway/service"
    "automation-firmware-wifi"
    "automation-firmware-serial"
)

for target in "${TARGETS[@]}"; do
    echo "🔍 Type checking $target ..."
    (
        cd "$SCRIPT_DIR"
        "$TY_BIN" check "$target" || true
    )
done

echo
echo "============================================"
echo "  ✅ Type checking finished (errors shown above)"
echo "============================================"
echo
