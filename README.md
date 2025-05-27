# 🎵 TUI YouTube Music Player

A beautiful Terminal User Interface (TUI) for playing YouTube Music in your terminal. Built with Python using `textual` for the interface, `ytmusicapi` for YouTube Music access, and `mpv` for high-quality audio playback.

## ✨ Features

### Core Features
- 🔍 **Search YouTube Music** - Find songs, artists, and albums
- 🎵 **Audio-only playback** - High-quality streaming via mpv
- ⌨️ **Keyboard navigation** - Full keyboard control for everything
- 📱 **Clean TUI interface** - Beautiful terminal interface with real-time updates
- 🎭 **No authentication required** - Works without YouTube Music subscription

### 📻 Radio Mode (NEW!)
- **Song-based radio** - Start radio from any song to discover similar music
- **Auto-play queue** - Automatically plays next song when current ends
- **Smart queue management** - Loads 20 songs, fetches more when running low
- **Radio queue panel** - See upcoming songs in a dedicated panel
- **Radio persistence** - Stops when you manually select another song

📖 **[Complete Radio Guide →](RADIO_GUIDE.md)** - Detailed guide with examples and tips

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- mpv media player

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd tui-youmusic
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install mpv:**
```bash
# Ubuntu/Debian
sudo apt install mpv

# Arch Linux
sudo pacman -S mpv

# macOS
brew install mpv
```

4. **Run the application:**
```bash
python ytmusic_tui.py
# OR
./run.sh
```

## 🎹 Controls & Usage

### Basic Navigation
| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate through search results |
| `Enter` | Play selected song |
| `s` | Focus search input |
| `Escape` / `q` / `Ctrl+C` | Quit application |

### Playback Controls
| Key | Action |
|-----|--------|
| `r` | Stop current song |
| `Shift+R` | **Start radio** based on selected song |
| `N` | Next song (radio mode only) |
| `Ctrl+R` | Stop radio mode |

### Radio Queue
| Key | Action |
|-----|--------|
| `Shift+Q` | Toggle radio queue panel visibility |
| `Q` | Show/hide radio queue |

### How to Use

1. **Search for music:** Type in the search box and press Enter
2. **Navigate results:** Use ↑/↓ arrow keys to browse songs
3. **Play a song:** Press Enter on any song
4. **Start radio:** Press `Shift+R` while a song is selected to start radio mode
5. **Enjoy continuous music:** Radio will automatically play similar songs
6. **Control radio:** Use `N` for next song, `Shift+Q` to see queue, `Ctrl+R` to stop

## 📻 Radio Mode Explained

### Starting Radio
- Select any song from search results
- Press `Shift+R` to start radio based on that song
- Radio will immediately start playing similar songs
- The radio queue panel will automatically appear

### How Radio Works
- **Initial Queue:** Loads 20 similar songs based on your selected track
- **Auto-play:** When a song ends, automatically plays the next song in queue
- **Smart Refill:** When queue drops below 5 songs, automatically fetches more
- **Current Song Display:** Shows currently playing song at top of radio queue
- **Status Updates:** Status bar shows radio mode and current song

### Radio Controls
- **Next Song (`N`):** Skip to next song in radio queue
- **Stop Radio (`Ctrl+R`):** Completely stop radio mode
- **Queue Toggle (`Shift+Q`):** Show/hide the radio queue panel
- **Manual Song Selection:** Selecting any song from search stops radio

### Radio Queue Panel
- **Currently Playing:** Shown at top with 🎵 icon
- **Upcoming Songs:** Listed below current song
- **Dynamic Updates:** Queue updates as songs play and new ones are fetched
- **Toggle Visibility:** Can be hidden/shown with `Shift+Q`

## 🛠️ Technical Details

### Dependencies
- **textual** (>=0.44.0) - TUI framework
- **ytmusicapi** (>=1.3.0) - YouTube Music API
- **yt-dlp** (>=2023.11.16) - YouTube URL extraction
- **mpv** - Audio playback engine

### Architecture
- **Async/Await:** Non-blocking UI with async operations
- **Threading:** Background audio playback to avoid UI freezing
- **Process Management:** Proper cleanup of mpv processes
- **Error Handling:** Graceful error handling and user feedback

### Radio Implementation
- **YouTube Music API:** Uses `get_watch_playlist()` for song recommendations
- **Queue Management:** Intelligent queue management with automatic refilling
- **Auto-play Detection:** Monitors mpv process completion for seamless transitions
- **State Management:** Clean radio state with proper cleanup

## 🔧 Configuration

The application works out of the box with no configuration required. However, you can modify:

- **Search limit:** Change the limit in `perform_search()` (default: 20)
- **Radio queue size:** Modify radio queue limits in `start_radio()` (default: 20 initial, 15 refill)
- **Queue refill threshold:** Change when to fetch more songs (default: <5 songs remaining)

## 🐛 Troubleshooting

### Common Issues

**mpv not found:**
```bash
# Install mpv first
sudo apt install mpv  # Ubuntu/Debian
brew install mpv       # macOS
```

**No search results:**
- Check internet connection
- Try different search terms
- Wait a moment and try again

**Radio not working:**
- Ensure you have an active internet connection
- Try starting radio with different songs
- Check that the selected song is valid

**Audio issues:**
- Verify mpv works: `mpv --version`
- Check system audio settings
- Try playing a local file with mpv

## 📊 Example Usage

```bash
# Start the application
python ytmusic_tui.py

# Search for music
> Type: "The Beatles" → Press Enter

# Navigate and play
> Use ↑↓ to browse → Press Enter to play

# Start radio
> Press Shift+R to start Beatles radio

# Control radio
> Press N for next song
> Press Shift+Q to see/hide queue
> Press Ctrl+R to stop radio
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **YouTube Music** for the music catalog
- **Textual** for the amazing TUI framework  
- **ytmusicapi** for YouTube Music API access
- **mpv** for reliable audio playback
- **yt-dlp** for YouTube URL extraction

---

**Made with ❤️ for music lovers who live in the terminal! 🎵** 