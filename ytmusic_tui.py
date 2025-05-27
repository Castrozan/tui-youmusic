from textual.app import App, ComposeResult
from textual.widgets import Input, Static, ListView, ListItem, Header, Footer
from textual.containers import Vertical, Horizontal
from textual import events
from textual.binding import Binding

from ytmusicapi import YTMusic
import subprocess
import threading
import os


class SongItem(ListItem):
    """Custom ListItem for displaying song information."""
    
    def __init__(self, title, artist, video_id, duration=None):
        # Format the display text
        duration_str = f" ({duration})" if duration else ""
        display_text = f"🎵 {title} - {artist}{duration_str}"
        super().__init__(Static(display_text))
        self.title = title
        self.artist = artist
        self.video_id = video_id
        self.duration = duration


class YTMusicTUI(App):
    """A Terminal User Interface for YouTube Music."""
    
    CSS_PATH = None
    TITLE = "🎵 TUI YouTube Music Player"
    SUB_TITLE = "Search and play music from YouTube Music"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit"),
        Binding("enter", "play_selected", "Play Song"),
        Binding("s", "focus_search", "Focus Search"),
        Binding("r", "stop_playback", "Stop Current Song"),
    ]

    def __init__(self):
        super().__init__()
        self.current_process = None
        self.songs = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical(
            Static("🔍 Search YouTube Music:", classes="search-label"),
            Input(placeholder="Enter song name, artist, or album...", id="search-input"),
            Static("", id="status"),
            Static("📋 Results:", classes="results-label"),
            ListView(id="results"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        try:
            # Try to initialize YTMusic (will work without authentication)
            self.ytmusic = YTMusic()
            self.update_status("Ready to search! Type your query and press Enter.")
        except Exception as e:
            self.update_status(f"Error initializing YouTube Music: {str(e)}")
        
        # Focus the search input
        self.query_one("#search-input", Input).focus()

    def update_status(self, message: str) -> None:
        """Update the status message."""
        status_widget = self.query_one("#status", Static)
        status_widget.update(f"📢 {message}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when user submits search query."""
        query = event.value.strip()
        if not query:
            self.update_status("Please enter a search query.")
            return
        
        self.update_status(f"Searching for: {query}...")
        await self.perform_search(query)

    async def perform_search(self, query: str) -> None:
        """Perform YouTube Music search."""
        results_widget = self.query_one("#results", ListView)
        results_widget.clear()
        self.songs = []

        try:
            # Search for songs
            results = self.ytmusic.search(query, filter="songs", limit=20)
            
            if not results:
                self.update_status("No results found. Try a different search term.")
                return

            for song in results:
                title = song.get("title", "Unknown Title")
                artist = "Unknown Artist"
                
                # Get artist name
                if song.get("artists") and len(song["artists"]) > 0:
                    artist = song["artists"][0]["name"]
                
                video_id = song.get("videoId")
                duration = song.get("duration")
                
                if video_id:
                    item = SongItem(title, artist, video_id, duration)
                    results_widget.append(item)
                    self.songs.append(item)

            if self.songs:
                results_widget.index = 0
                self.update_status(f"Found {len(self.songs)} songs. Use ↑↓ to navigate, Enter to play.")
            else:
                self.update_status("No valid songs found in results.")
                
        except Exception as e:
            self.update_status(f"Search error: {str(e)}")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when user selects a song from the list."""
        if event.item and hasattr(event.item, 'video_id'):
            await self.play_song(event.item)

    async def play_song(self, song_item: SongItem) -> None:
        """Play the selected song using mpv."""
        try:
            # Stop current playback if any
            await self.stop_current_playback()
            
            url = f"https://www.youtube.com/watch?v={song_item.video_id}"
            self.update_status(f"🎵 Playing: {song_item.title} - {song_item.artist}")
            
            # Start mpv in a separate thread to avoid blocking the UI
            def play_with_mpv():
                try:
                    # Use mpv with audio-only and no terminal output
                    self.current_process = subprocess.Popen([
                        "mpv", 
                        "--no-video", 
                        "--really-quiet",
                        "--no-terminal",
                        url
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.current_process.wait()
                except Exception as e:
                    self.call_from_thread(self.update_status, f"Playback error: {str(e)}")
            
            # Start playback in background thread
            threading.Thread(target=play_with_mpv, daemon=True).start()
            
        except Exception as e:
            self.update_status(f"Error starting playback: {str(e)}")

    async def stop_current_playback(self) -> None:
        """Stop current mpv playback."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process = None
                self.update_status("⏹️  Playback stopped.")
            except:
                pass

    def action_play_selected(self) -> None:
        """Action to play the currently selected song."""
        results_widget = self.query_one("#results", ListView)
        if results_widget.highlighted_child:
            self.run_action("list_view.select")

    def action_focus_search(self) -> None:
        """Action to focus the search input."""
        self.query_one("#search-input", Input).focus()

    async def action_stop_playback(self) -> None:
        """Action to stop current playback."""
        await self.stop_current_playback()

    def action_quit(self) -> None:
        """Action to quit the application."""
        # Stop any current playback before quitting
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        self.exit()


def main():
    """Main entry point for the application."""
    # Check if mpv is installed
    try:
        subprocess.run(["mpv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: mpv is not installed or not in PATH.")
        print("Please install mpv:")
        print("  Ubuntu/Debian: sudo apt install mpv")
        print("  Arch: sudo pacman -S mpv")
        print("  macOS: brew install mpv")
        exit(1)
    
    app = YTMusicTUI()
    app.run()


if __name__ == "__main__":
    main() 