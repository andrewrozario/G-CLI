#!/bin/bash
set -e

echo "=============================================="
echo "    G CLI - Multi-Brain AI OS Setup (macOS)   "
echo "=============================================="
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3 (https://www.python.org/downloads/mac-osx/)"
    exit 1
fi

echo "🔍 Python 3 detected. Locating project..."

# Get project root (two directories up from Landing_Page/MacOS)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$DIR")")"

cd "$PROJECT_ROOT"

echo "📦 Installing G CLI and dependencies..."
# Use --break-system-packages for newer macOS (12.x+), fallback to standard install
python3 -m pip install . --user --break-system-packages 2>/dev/null || python3 -m pip install . --user

# Detect Python user bin path
PYTHON_BIN="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin"

# Add to PATH based on current shell
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q "$PYTHON_BIN" "$SHELL_RC" 2>/dev/null; then
        echo "export PATH=\"\$PATH:$PYTHON_BIN\"" >> "$SHELL_RC"
        echo "🔧 Updated PATH in $SHELL_RC"
    fi
fi

echo ""
echo "✅ Installation Complete!"
echo "🚀 Close this terminal window, open a new one, and type 'g' or 'G' to start."
echo "=============================================="
