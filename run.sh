#!/bin/bash

# TUI YouTube Music Player Launcher
# This script sets up the environment and launches the player

echo "🎵 Starting TUI YouTube Music Player..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Check if mpv is available
if ! command -v mpv &> /dev/null; then
    echo "❌ Error: mpv is not installed or not in PATH."
    echo "Please install mpv:"
    echo "  Ubuntu/Debian: sudo apt install mpv"
    echo "  Arch: sudo pacman -S mpv"
    echo "  macOS: brew install mpv"
    exit 1
fi

# Check if required Python packages are installed
python3 -c "import textual, ytmusicapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required Python packages not found."
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
fi

# Launch the application
echo "🚀 Launching TUI YouTube Music Player..."
python3 ytmusic_tui.py 