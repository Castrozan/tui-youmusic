# 🚀 Quick Start Guide

## TL;DR - Get Running in 30 Seconds

```bash
# 1. Install mpv (if not already installed)
sudo apt install mpv

# 2. Install Python dependencies (already done in this project)
pip install textual ytmusicapi yt-dlp

# 3. Run the application
python3 ytmusic_tui.py
```

## What You'll See

1. **Start Screen**: A clean TUI with a search bar at the top
2. **Search**: Type any song, artist, or album name and press Enter
3. **Results**: Navigate with ↑/↓ arrow keys
4. **Play**: Press Enter on any song to start playing
5. **Controls**: Use keyboard shortcuts (see below)

## Essential Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Type + Enter** | Search for music |
| **↑ ↓** | Navigate results |
| **Enter** | Play selected song |
| **r** | Stop current song |
| **s** | Focus search bar |
| **q** | Quit |

## Quick Test

Run this to test everything works:

```bash
python3 test_search.py
```

If all tests pass, you're ready to go!

## Example Usage

1. Start the app: `python3 ytmusic_tui.py`
2. Type "The Beatles" and press Enter
3. Use arrow keys to browse results
4. Press Enter on "Here Comes The Sun"
5. Enjoy! 🎵

## Troubleshooting

**App won't start?**
- Check if mpv is installed: `mpv --version`
- Check Python packages: `python3 -c "import textual, ytmusicapi"`

**No search results?**
- Check internet connection
- Try different search terms

**No audio?**
- Check system audio is working
- Test mpv directly: `mpv --no-video "https://www.youtube.com/watch?v=xUNqsfFUwhY"`

## Alternative Launch Methods

```bash
# Method 1: Direct Python
python3 ytmusic_tui.py

# Method 2: Shell script (includes checks)
./run.sh

# Method 3: Install as package (future)
pip install -e .
tui-youmusic
```

---

**Need more help?** Check the full [README.md](README.md) for detailed documentation. 