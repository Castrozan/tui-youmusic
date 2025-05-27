# 🎵 TUI YouTube Music Player

A beautiful Terminal User Interface (TUI) for YouTube Music that lets you search and play music directly from your terminal using `mpv` as the audio backend.

![TUI YouTube Music Player](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🔍 **Search YouTube Music** - Find songs, artists, and albums
- 🎵 **High-quality audio playback** - Uses `mpv` for excellent audio quality
- ⌨️  **Keyboard navigation** - Fully keyboard-driven interface
- 🎨 **Modern TUI** - Beautiful interface built with Textual
- 🚀 **Fast and lightweight** - Minimal resource usage
- 🔄 **Real-time status updates** - See what's playing and search progress
- ⏹️  **Playback control** - Stop current song with hotkeys

## 🛠️ Installation

### 1. System Dependencies

First, install `mpv` (the audio player backend):

```bash
# Ubuntu/Debian
sudo apt install mpv

# Arch Linux
sudo pacman -S mpv

# macOS (with Homebrew)
brew install mpv

# Fedora
sudo dnf install mpv
```

### 2. Python Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install manually:
pip install textual ytmusicapi yt-dlp
```

### 3. Clone and Run

```bash
git clone <repository-url>
cd tui-youmusic
python ytmusic_tui.py
```

## 🎮 Usage

### Starting the Application

```bash
python ytmusic_tui.py
```

### Controls

| Key | Action |
|-----|--------|
| `Type + Enter` | Search for music |
| `Tab` | Togle list selection |
| `↑ ↓` | Navigate search results |
| `Enter` | Play selected song |
| `s` | Focus search bar |
| `r` | Stop current playback |
| `q` / `Esc` / `Ctrl+C` | Quit application |

### How to Use

1. **Search**: Type your search query in the search bar and press `Enter`
2. **Browse**: Use arrow keys to navigate through the results
3. **Play**: Press `Enter` on any song to start playback
4. **Control**: Use `r` to stop current song, `s` to search again

## 🔧 Configuration

The application works out of the box without any configuration. However, you can:

- **Authentication**: For better access, you can set up YouTube Music authentication (optional)
- **Audio Quality**: mpv automatically selects the best available audio quality
- **Custom mpv settings**: Modify the mpv command in the code for custom audio settings

## 🎵 Features in Detail

### Search Functionality
- Search by song title, artist name, or album
- Returns up to 20 relevant results
- Shows song duration when available
- Real-time search status updates

### Audio Playback
- Audio-only playback (no video)
- Background playback (doesn't block the UI)
- Automatic stopping of previous songs when starting new ones
- Silent operation (no mpv terminal output)

### User Interface
- Clean, modern TUI design
- Header with application title
- Footer with keyboard shortcuts
- Status messages for user feedback
- Responsive layout

## 🔍 Troubleshooting

### Common Issues

**mpv not found:**
```bash
# Make sure mpv is installed and in your PATH
which mpv
mpv --version
```

**No search results:**
- Check your internet connection
- Try different search terms
- Make sure ytmusicapi is working: `python -c "from ytmusicapi import YTMusic; print('OK')"`

**Playback issues:**
- Ensure mpv can play YouTube URLs: `mpv --no-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`
- Check audio system is working
- Try running with verbose output (modify the mpv command in code)

**Permission errors:**
- Make sure you have internet access
- Check if any firewall is blocking the connections

## 🔮 Future Enhancements

- [ ] Playlist support
- [ ] Search history
- [ ] Favorite songs
- [ ] Download for offline playback
- [ ] Lyrics display
- [ ] Equalizer controls
- [ ] Theming support
- [ ] Configuration file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Textual](https://github.com/Textualize/textual) - For the amazing TUI framework
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - For YouTube Music API access
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - For video URL extraction
- [mpv](https://mpv.io/) - For high-quality audio playback

---

**Note**: This application uses YouTube Music's public API and respects their terms of service. No authentication is required for basic functionality. 