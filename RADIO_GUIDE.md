# 📻 Radio Mode Guide - TUI YouTube Music Player

Welcome to the **Radio Mode** - the newest feature that transforms your TUI YouTube Music Player into a continuous music discovery experience!

## 🎵 What is Radio Mode?

Radio Mode creates a seamless, auto-playing playlist of similar songs based on any track you choose. It's like having your own personal radio station that discovers music you'll love!

## 🚀 Quick Start

### 1. Start the App
```bash
python3 ytmusic_tui.py
```

### 2. Search for Music
- Type any song, artist, or album in the search box
- Press `Enter` to search
- Use `↑` and `↓` to browse results

### 3. Start Radio
- Select any song you like
- Press `Shift+R` to start radio based on that song
- 🎉 Radio will immediately start playing similar music!

## 📻 Radio Features

### Auto-Play Queue
- **20 Songs Initially**: Loads 20 similar songs when radio starts
- **Smart Refilling**: Automatically fetches 15 more songs when queue drops below 5
- **Seamless Playback**: When a song ends, automatically plays the next one
- **No Interruptions**: Continuous music discovery experience

### Radio Queue Panel
- **Dedicated Panel**: Shows upcoming songs in a separate panel on the right
- **Current Song Indicator**: Currently playing song shown at top with 🎵 icon
- **Dynamic Updates**: Queue updates in real-time as songs play
- **Toggle Visibility**: Hide/show with `Shift+Q`

### Intelligent Recommendations
- **YouTube Music Algorithm**: Uses YouTube Music's recommendation engine
- **Song-Based Radio**: Creates playlist based on the specific song you select
- **Quality Curation**: Gets high-quality recommendations similar to your choice

## ⌨️ Radio Controls

| Key | Action | Description |
|-----|--------|-------------|
| `Shift+R` | **Start Radio** | Begin radio mode from selected song |
| `N` | **Next Song** | Skip to next song in radio queue |
| `Ctrl+R` | **Stop Radio** | Completely stop radio mode |
| `Shift+Q` | **Toggle Queue** | Show/hide radio queue panel |
| `r` | **Stop Song** | Stop current song (radio continues) |

## 🎯 Radio Workflow

```
1. Search & Select Song
   ↓
2. Press Shift+R
   ↓
3. Radio Starts Playing Similar Songs
   ↓
4. Queue Panel Shows Upcoming Songs
   ↓
5. Songs Auto-Play Continuously
   ↓
6. Queue Auto-Refills When Low
```

## 📱 Radio Status

### Status Bar Indicators
- **📻 Radio: Song Name** - Shows when radio is active
- **Queue Count** - Number of songs remaining in queue
- **Current Song** - What's currently playing

### Radio Queue Panel
```
📻 Radio Queue:
🎵 Currently Playing Song - Artist (3:42)
    Next Song 1 - Artist (4:15)
    Next Song 2 - Artist (3:28)
    Next Song 3 - Artist (2:59)
    ... (more songs)
```

## 🔄 Radio Behavior

### When Radio Starts
1. Loads 20 similar songs based on your selected track
2. Shows radio queue panel automatically
3. Starts playing the first recommended song
4. Updates status to show radio mode is active

### During Radio Playback
1. Songs play automatically one after another
2. Queue refills when less than 5 songs remain
3. Current song indicator moves through the queue
4. You can skip songs with `N` key

### How Radio Stops
- **Manual Stop**: Press `Ctrl+R` to stop radio mode
- **Song Selection**: Select any song from search results (auto-stops radio)
- **App Quit**: Radio stops when you quit the application

## 💡 Pro Tips

### Getting Better Recommendations
- **Start with specific songs** rather than generic tracks for better radio
- **Try different genres** - each song creates a unique radio experience
- **Use popular songs** as radio seeds for more diverse recommendations

### Managing Your Experience
- **Hide queue panel** with `Shift+Q` if you prefer minimal UI
- **Skip songs** with `N` to explore different directions
- **Restart radio** from any new song to change musical direction

### Troubleshooting Radio
- **No radio playlist?** Try a different, more popular song
- **Radio stops unexpectedly?** Check internet connection
- **Queue not refilling?** Radio will fetch more songs automatically

## 🎼 Example Radio Session

```bash
# Start the app
python3 ytmusic_tui.py

# Search for your favorite song
> Type: "Bohemian Rhapsody Queen" → Press Enter

# Select the song and start radio
> Use ↑↓ to select → Press Shift+R

# Radio starts!
📻 Radio: Bohemian Rhapsody | Queue: 19 songs
🎵 Now Playing: We Will Rock You - Queen
   Next: Another One Bites The Dust - Queen
   Next: Don't Stop Me Now - Queen
   Next: Somebody to Love - Queen
   ...

# Control your radio experience
> Press N to skip songs
> Press Shift+Q to hide/show queue
> Press Ctrl+R to stop radio
```

## 🌟 Why Use Radio Mode?

- **Music Discovery**: Find new songs similar to ones you already love
- **Hands-Free Listening**: Set it and forget it - music plays continuously
- **Mood Matching**: Creates cohesive playlists that match the vibe of your seed song
- **No Interruptions**: No need to constantly search for new music
- **Intelligent Curation**: Leverages YouTube Music's powerful recommendation algorithm

---

## 🎵 Ready to Start Your Radio Journey?

1. **Launch the app**: `python3 ytmusic_tui.py`
2. **Find a song you love**
3. **Press `Shift+R`**
4. **Enjoy continuous music discovery!** 🎉

**Happy listening! 📻🎶** 