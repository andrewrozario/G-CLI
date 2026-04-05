#!/bin/bash

echo "🚀 Starting G CLI Installation..."

# 1. Install Dependencies
echo "📦 Installing requirements..."
python3 -m pip install -e . --break-system-packages --user

# 2. Add to PATH if needed
BIN_PATH="/Users/dr.andrewrozario/Library/Python/3.14/bin"
if [[ ":$PATH:" != *":$BIN_PATH:"* ]]; then
    echo "Updating PATH..."
    echo "export PATH=\"\$PATH:$BIN_PATH\"" >> ~/.zshrc
    source ~/.zshrc
fi

echo "✨ Installation complete! Type 'g' or 'G' to start."
echo "🏥 Run 'g doctor' to verify your setup."
