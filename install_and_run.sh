#!/bin/bash
# IdeaTracker — Install dependencies and launch
set -e

echo "=== IdeaTracker Setup ==="

# Install system dependency for PDF preview (optional but recommended)
echo "Installing poppler-utils for PDF preview (requires sudo)..."
sudo apt-get install -y poppler-utils 2>/dev/null || echo "  (skipped — install manually with: sudo apt install poppler-utils)"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Launching IdeaTracker ==="
python3 main.py
