from textual.app import App, ComposeResult
from textual.widgets import Input, Static, ListView, ListItem, Header, Footer
from textual.containers import Vertical, Horizontal
from textual import events
from textual.binding import Binding

from ytmusicapi import YTMusic
import subprocess
import threading
import os
import time
import asyncio
import signal
import atexit
import psutil
import json
from pathlib import Path


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


class RadioQueueItem(ListItem):
    """Custom ListItem for displaying radio queue songs."""
    
    def __init__(self, title, artist, video_id, duration=None, is_current=False):
        # Format the display text with radio indicator
        duration_str = f" ({duration})" if duration else ""
        prefix = "🎵 " if is_current else "   "
        display_text = f"{prefix}{title} - {artist}{duration_str}"
        super().__init__(Static(display_text))
        self.title = title
        self.artist = artist
        self.video_id = video_id
        self.duration = duration
        self.is_current = is_current


class YTMusicTUI(App):
    """A Terminal User Interface for YouTube Music."""
    
    # Class variable to track all mpv processes across instances
    _active_processes = []
    _cleanup_registered = False
    
    CSS = """
    .main-panel {
        width: 70%;
        padding: 1;
    }
    
    .radio-panel {
        width: 30%;
        padding: 1;
        border-left: solid $primary;
    }
    
    .search-label, .results-label, .radio-label {
        text-style: bold;
        color: $accent;
    }
    
    #status {
        color: $warning;
        margin: 1 0;
        text-style: italic;
    }
    
    ListView {
        border: solid $primary;
        height: auto;
    }
    
    #radio-queue {
        min-height: 20;
    }
    
    Input {
        border: solid $primary;
    }
    
    .radio-current {
        background: $primary 20%;
        text-style: bold;
    }
    """
    
    TITLE = "🎵 TUI YouTube Music Player"
    SUB_TITLE = "Search and play music from YouTube Music"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit"),
        Binding("enter", "play_selected", "Play Song"),
        Binding("s", "focus_search", "Focus Search"),
        Binding("ctrl+s", "stop_all_music", "Stop Song"),
        Binding("p", "resume_playback", "Resume Last Song"),
        Binding("R", "start_radio", "Start Radio"),
        Binding("n", "next_song", "Next Song"),
        Binding("ctrl+r", "stop_radio", "Stop Radio"),
        Binding("Q", "toggle_radio_queue", "Toggle Radio Queue"),
    ]

    def __init__(self):
        super().__init__()
        self.current_process = None
        self.songs = []

        # State persistence
        self.state_file = Path.home() / ".ytmusic_tui_state.json"

        # Resume functionality
        self.last_played_song = None
        self.was_radio_active = False
        self.radio_state_when_stopped = None
        
        # Radio functionality
        self.radio_active = False
        self.radio_queue = []
        self.radio_current_song = None
        self.radio_original_song = None
        self.radio_monitor_thread = None
        self.radio_queue_visible = False
        self.stop_radio_monitoring = False
        
        # Race condition prevention
        self.radio_progression_lock = threading.Lock()
        self.manual_progression_happening = False

    @classmethod
    def _register_cleanup_handlers(cls):
        """Register cleanup handlers for graceful shutdown."""
        # Register atexit handler for normal exit
        atexit.register(cls._cleanup_all_processes)
        
        # Register signal handlers for crashes and interrupts
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, cleaning up...")
            cls._cleanup_all_processes()
            exit(0)
        
        # Handle common termination signals
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Normal termination
        try:
            signal.signal(signal.SIGHUP, signal_handler)   # Terminal closed
        except AttributeError:
            # SIGHUP not available on Windows
            pass

    @classmethod
    def _cleanup_all_processes(cls):
        """Kill all mpv processes started by this application."""
        try:
            # Kill processes we're tracking
            for process in cls._active_processes:
                try:
                    if process.poll() is None:  # Process is still running
                        process.terminate()
                        # Give it a moment to terminate gracefully
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            process.kill()  # Force kill if it doesn't terminate
                except:
                    pass
            
            # Clear the process list
            cls._active_processes.clear()
            
            # Also kill any mpv processes that might be running (backup cleanup)
            try:
                # Use psutil to find and kill mpv processes
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'mpv':
                            # Check if it's likely our mpv process (playing youtube)
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            if 'youtube.com' in cmdline or '--no-video' in cmdline:
                                proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except ImportError:
                # Fallback if psutil import fails - use pkill
                try:
                    subprocess.run(['pkill', '-f', 'mpv.*youtube'], 
                                 capture_output=True, timeout=5)
                except:
                    pass
                    
        except Exception as e:
            # Don't let cleanup errors crash the cleanup
            pass

    def save_state(self):
        """Save current radio state to file."""
        try:
            state = {
                'radio_active': self.radio_active,
                'radio_queue_visible': self.radio_queue_visible,
                'radio_queue': [],
                'radio_current_song': None,
                'radio_original_song': None,
                'last_played_song': None,
                'timestamp': time.time()
            }
            
            # Save radio queue
            if self.radio_queue:
                state['radio_queue'] = [
                    {
                        'title': song.title,
                        'artist': song.artist,
                        'video_id': song.video_id,
                        'duration': song.duration
                    }
                    for song in self.radio_queue
                ]
            
            # Save current radio song
            if self.radio_current_song:
                state['radio_current_song'] = {
                    'title': self.radio_current_song.title,
                    'artist': self.radio_current_song.artist,
                    'video_id': self.radio_current_song.video_id,
                    'duration': self.radio_current_song.duration
                }
            
            # Save original radio song
            if self.radio_original_song:
                state['radio_original_song'] = {
                    'title': self.radio_original_song.title,
                    'artist': self.radio_original_song.artist,
                    'video_id': self.radio_original_song.video_id,
                    'duration': self.radio_original_song.duration
                }
            
            # Save last played song
            if self.last_played_song:
                state['last_played_song'] = {
                    'title': self.last_played_song.title,
                    'artist': self.last_played_song.artist,
                    'video_id': self.last_played_song.video_id,
                    'duration': self.last_played_song.duration
                }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            pass  # Don't crash on save errors

    def load_state(self):
        """Load saved state from file."""
        try:
            if not self.state_file.exists():
                return False
                
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Check if state is recent (within last 24 hours)
            if time.time() - state.get('timestamp', 0) > 86400:
                return False
            
            # Restore radio state
            self.radio_active = state.get('radio_active', False)
            self.radio_queue_visible = state.get('radio_queue_visible', False)
            
            # Restore radio queue
            self.radio_queue = []
            for song_data in state.get('radio_queue', []):
                song = SongItem(
                    song_data['title'],
                    song_data['artist'],
                    song_data['video_id'],
                    song_data.get('duration')
                )
                self.radio_queue.append(song)
            
            # Restore current radio song
            if state.get('radio_current_song'):
                song_data = state['radio_current_song']
                self.radio_current_song = SongItem(
                    song_data['title'],
                    song_data['artist'],
                    song_data['video_id'],
                    song_data.get('duration')
                )
            
            # Restore original radio song
            if state.get('radio_original_song'):
                song_data = state['radio_original_song']
                self.radio_original_song = SongItem(
                    song_data['title'],
                    song_data['artist'],
                    song_data['video_id'],
                    song_data.get('duration')
                )
            
            # Restore last played song
            if state.get('last_played_song'):
                song_data = state['last_played_song']
                self.last_played_song = SongItem(
                    song_data['title'],
                    song_data['artist'],
                    song_data['video_id'],
                    song_data.get('duration')
                )
            
            return True
            
        except Exception as e:
            return False

    def check_background_playback(self):
        """Check if mpv is still running in background."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'mpv':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'youtube.com' in cmdline or '--no-video' in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass
        return False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Horizontal(
            Vertical(
                Static("🔍 Search YouTube Music:", classes="search-label"),
                Input(placeholder="Enter song name, artist, or album...", id="search-input"),
                Static("", id="status"),
                Static("📋 Results:", classes="results-label"),
                ListView(id="results"),
                classes="main-panel"
            ),
            Vertical(
                Static("📻 Radio Queue:", classes="radio-label"),
                ListView(id="radio-queue"),
                classes="radio-panel"
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        try:
            # Try to initialize YTMusic (will work without authentication)
            self.ytmusic = YTMusic()
            
            # Check if there's background playback and load state
            background_playback = self.check_background_playback()
            state_loaded = self.load_state()
            
            if background_playback and state_loaded and self.radio_active:
                # Show radio queue if state was restored
                if self.radio_queue_visible:
                    self.query_one(".radio-panel").display = True
                    # Update the radio queue display after mounting is complete
                    self.call_after_refresh(self.update_radio_queue_display)
                
                # Set monitoring flag to allow radio progression
                self.stop_radio_monitoring = False
                
                self.update_status(f"📻 Resumed radio session! Playing in background. Queue: {len(self.radio_queue)} songs")
            elif background_playback:
                self.update_status("🎵 Music playing in background. Use ^s to stop or search for new songs.")
            else:
                self.update_status("Ready to search! Type your query and press Enter.")
                
        except Exception as e:
            self.update_status(f"Error initializing YouTube Music: {str(e)}")
        
        # Focus the search input
        self.query_one("#search-input", Input).focus()
        
        # Hide radio queue initially if no state was loaded
        if not (self.radio_active and self.radio_queue_visible):
            self.query_one(".radio-panel").display = False

    def update_status(self, message: str) -> None:
        """Update the status message."""
        status_widget = self.query_one("#status", Static)
        
        # Add radio status if active
        if self.radio_active and self.radio_current_song:
            radio_msg = f"📻 Radio: {self.radio_current_song.title}"
            message = f"{message} | {radio_msg}"
        
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
                self.update_status(f"Found {len(self.songs)} songs. Use Tab and ↑↓ to navigate, Enter to play.")
            else:
                self.update_status("No valid songs found in results.")
                
        except Exception as e:
            self.update_status(f"Search error: {str(e)}")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when user selects a song from the list."""
        if event.item and hasattr(event.item, 'video_id'):
            # Stop radio if user manually selects a song
            if self.radio_active:
                await self.stop_radio()
            await self.play_song(event.item)

    async def play_song(self, song_item: SongItem, from_radio=False) -> None:
        """Play the selected song using mpv."""
        try:
            # Stop ALL existing music to prevent overlaps
            await self.stop_all_existing_music()
            
            url = f"https://www.youtube.com/watch?v={song_item.video_id}"
            
            # Track the song for resume functionality
            self.last_played_song = song_item
            
            # Update current song reference
            if from_radio:
                self.radio_current_song = song_item
            
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
                    
                    # Track this process for cleanup
                    YTMusicTUI._active_processes.append(self.current_process)
                    
                    # Wait for process and handle radio progression
                    self.current_process.wait()
                    
                    # Remove from tracking when done
                    try:
                        YTMusicTUI._active_processes.remove(self.current_process)
                    except ValueError:
                        pass
                    
                    # Check if radio auto-progression should happen
                    # Use lock to prevent race condition with manual progression
                    with self.radio_progression_lock:
                        should_auto_progress = (
                            self.radio_active and 
                            not self.stop_radio_monitoring and 
                            from_radio and 
                            not self.manual_progression_happening
                        )
                        
                        if should_auto_progress:
                            # Set flag to prevent other threads from progressing
                            self.manual_progression_happening = True
                            
                            # Save state before playing next song
                            self.call_from_thread(self.save_state)
                            # Schedule next song
                            self.call_from_thread(self.auto_play_next_radio_song)
                        
                except Exception as e:
                    self.call_from_thread(self.update_status, f"Playback error: {str(e)}")
            
            # Start playback in background thread
            threading.Thread(target=play_with_mpv, daemon=True).start()
            
            # Save state after starting playback
            self.save_state()
            
        except Exception as e:
            self.update_status(f"Error starting playback: {str(e)}")

    async def stop_current_playback(self) -> None:
        """Disconnect from current playback (let it continue in background)."""
        # Save state before disconnecting
        self.save_state()
        
        if self.current_process:
            try:
                # Remove from tracking list (disconnect, don't kill)
                try:
                    YTMusicTUI._active_processes.remove(self.current_process)
                except ValueError:
                    pass
                
                # Don't terminate the process - let it continue in background
                self.current_process = None
                self.update_status("⏹️  Disconnected from playback. Music continues in background. Press 'p' to resume or ^s to stop.")
            except:
                pass
        

    async def stop_all_existing_music(self) -> None:
        """Stop all existing music to prevent overlaps when starting new music."""
        try:
            # Stop current process if tracked
            if self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process = None
                except:
                    pass
            
            # Kill all mpv processes to prevent overlaps
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'mpv':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'youtube.com' in cmdline or '--no-video' in cmdline:
                            proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass  # Don't let this block new music from starting

    async def start_radio(self, song_item: SongItem = None) -> None:
        """Start radio mode based on current or provided song."""
        try:
            # Use provided song or try to get current playing song
            if not song_item:
                # Get currently selected song from results
                results_widget = self.query_one("#results", ListView)
                if results_widget.highlighted_child:
                    song_item = results_widget.highlighted_child
                else:
                    self.update_status("❌ No song selected to start radio.")
                    return
            
            self.update_status(f"🔄 Starting radio based on: {song_item.title}...")
            
            # Get radio playlist from YouTube Music
            video_id = song_item.video_id
            watch_playlist = self.ytmusic.get_watch_playlist(videoId=video_id, limit=20)
            
            if not watch_playlist or 'tracks' not in watch_playlist:
                self.update_status("❌ Could not get radio playlist.")
                return
            
            # Clear and populate radio queue
            self.radio_queue = []
            radio_queue_widget = self.query_one("#radio-queue", ListView)
            radio_queue_widget.clear()
            
            # Add songs to radio queue
            for track in watch_playlist['tracks'][:20]:
                if track.get('videoId'):
                    title = track.get('title', 'Unknown Title')
                    
                    # Get artist name
                    artist = "Unknown Artist"
                    if track.get('artists') and len(track['artists']) > 0:
                        artist = track['artists'][0]['name']
                    
                    video_id = track['videoId']
                    duration = track.get('duration', {}).get('text', '')
                    
                    radio_song = SongItem(title, artist, video_id, duration)
                    self.radio_queue.append(radio_song)
                    
                    # Add to UI
                    queue_item = RadioQueueItem(title, artist, video_id, duration)
                    radio_queue_widget.append(queue_item)
            
            # Set radio state
            self.radio_active = True
            self.radio_original_song = song_item
            self.radio_current_song = song_item
            self.stop_radio_monitoring = False
            
            # Show radio queue
            self.query_one(".radio-panel").display = True
            self.radio_queue_visible = True
            
            # Start playing the first song in radio
            if self.radio_queue:
                first_song = self.radio_queue.pop(0)
                await self.play_song(first_song, from_radio=True)
                
                # Update queue display
                await self.update_radio_queue_display()
            
            self.update_status(f"📻 Radio started! Queue: {len(self.radio_queue)} songs")
            
        except Exception as e:
            self.update_status(f"❌ Error starting radio: {str(e)}")

    async def stop_radio(self) -> None:
        """Stop radio mode."""
        # Reset progression flag
        with self.radio_progression_lock:
            self.manual_progression_happening = False
            
        self.radio_active = False
        self.radio_queue = []
        self.radio_current_song = None
        self.radio_original_song = None
        self.stop_radio_monitoring = True
        
        # Clear radio queue display
        radio_queue_widget = self.query_one("#radio-queue", ListView)
        radio_queue_widget.clear()
        
        # Hide radio queue panel
        self.query_one(".radio-panel").display = False
        self.radio_queue_visible = False
        
        self.update_status("📻 Radio stopped.")

    async def play_next_radio_song(self) -> None:
        """Play the next song in radio queue (manual progression)."""
        if not self.radio_active or not self.radio_queue:
            return
        
        # Use lock to prevent race condition with automatic progression
        with self.radio_progression_lock:
            if self.manual_progression_happening:
                # Another progression is already happening
                return
            
            # Set flag to prevent automatic progression
            self.manual_progression_happening = True
        
        try:
            # Check if we need to fetch more songs
            if len(self.radio_queue) < 5:
                await self.fetch_more_radio_songs()
            
            # Play next song
            if self.radio_queue:
                next_song = self.radio_queue.pop(0)
                await self.play_song(next_song, from_radio=True)
                await self.update_radio_queue_display()
                # Save state after radio progression
                self.save_state()
        finally:
            # Always clear the flag when done
            with self.radio_progression_lock:
                self.manual_progression_happening = False

    async def auto_play_next_radio_song(self) -> None:
        """Play the next song in radio queue (automatic progression from thread)."""
        if not self.radio_active or not self.radio_queue:
            with self.radio_progression_lock:
                self.manual_progression_happening = False
            return
        
        try:
            # Check if we need to fetch more songs
            if len(self.radio_queue) < 5:
                await self.fetch_more_radio_songs()
            
            # Play next song
            if self.radio_queue:
                next_song = self.radio_queue.pop(0)
                await self.play_song(next_song, from_radio=True)
                await self.update_radio_queue_display()
                # Save state after radio progression
                self.save_state()
        finally:
            # Always clear the flag when done
            with self.radio_progression_lock:
                self.manual_progression_happening = False

    async def fetch_more_radio_songs(self) -> None:
        """Fetch more songs for radio queue when running low."""
        try:
            if not self.radio_current_song:
                return
            
            # Get more songs based on current playing song
            watch_playlist = self.ytmusic.get_watch_playlist(
                videoId=self.radio_current_song.video_id, 
                limit=15
            )
            
            if watch_playlist and 'tracks' in watch_playlist:
                radio_queue_widget = self.query_one("#radio-queue", ListView)
                
                for track in watch_playlist['tracks'][:15]:
                    if track.get('videoId'):
                        title = track.get('title', 'Unknown Title')
                        
                        # Get artist name
                        artist = "Unknown Artist"
                        if track.get('artists') and len(track['artists']) > 0:
                            artist = track['artists'][0]['name']
                        
                        video_id = track['videoId']
                        duration = track.get('duration', {}).get('text', '')
                        
                        # Avoid duplicates
                        if not any(s.video_id == video_id for s in self.radio_queue):
                            radio_song = SongItem(title, artist, video_id, duration)
                            self.radio_queue.append(radio_song)
                            
                            # Add to UI
                            queue_item = RadioQueueItem(title, artist, video_id, duration)
                            radio_queue_widget.append(queue_item)
                
        except Exception as e:
            self.update_status(f"Warning: Could not fetch more radio songs: {str(e)}")

    async def update_radio_queue_display(self) -> None:
        """Update the radio queue display."""
        if not self.radio_queue_visible:
            return
        
        radio_queue_widget = self.query_one("#radio-queue", ListView)
        radio_queue_widget.clear()
        
        # Add current song at top (if radio is active)
        if self.radio_active and self.radio_current_song:
            current_item = RadioQueueItem(
                self.radio_current_song.title,
                self.radio_current_song.artist,
                self.radio_current_song.video_id,
                self.radio_current_song.duration,
                is_current=True
            )
            radio_queue_widget.append(current_item)
        
        # Add queue songs
        for song in self.radio_queue:
            queue_item = RadioQueueItem(song.title, song.artist, song.video_id, song.duration)
            radio_queue_widget.append(queue_item)

    def action_play_selected(self) -> None:
        """Action to play the currently selected song."""
        results_widget = self.query_one("#results", ListView)
        if results_widget.highlighted_child:
            self.run_action("list_view.select")

    def action_focus_search(self) -> None:
        """Action to focus the search input."""
        self.query_one("#search-input", Input).focus()

    async def action_stop_all_music(self) -> None:
        """Action to actually stop all music."""
        try:
            # Reset progression flag first
            with self.radio_progression_lock:
                self.manual_progression_happening = False
                
            # Stop current process if tracked
            if self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process = None
                except:
                    pass
            
            # Kill all mpv processes
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'mpv':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'youtube.com' in cmdline or '--no-video' in cmdline:
                            proc.terminate()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Clear radio state
            self.radio_active = False
            self.radio_queue = []
            self.radio_current_song = None
            self.radio_original_song = None
            self.stop_radio_monitoring = True
            
            # Clear radio queue display
            radio_queue_widget = self.query_one("#radio-queue", ListView)
            radio_queue_widget.clear()
            
            # Hide radio queue panel
            self.query_one(".radio-panel").display = False
            self.radio_queue_visible = False
            
            # Clear saved state since music is stopped
            if self.state_file.exists():
                self.state_file.unlink()
            
            if killed_count > 0:
                self.update_status(f"🛑 Stopped music. {killed_count} process(es) terminated.")
            else:
                self.update_status("🛑 Music stopped.")
                
        except Exception as e:
            self.update_status(f"❌ Error stopping music: {str(e)}")

    async def action_resume_playback(self) -> None:
        """Action to resume the last played song."""
        if not self.last_played_song:
            self.update_status("❌ No song to resume. Play a song first.")
            return
        
        # If radio was active when stopped, restore radio state
        if self.was_radio_active and self.radio_state_when_stopped:
            self.update_status(f"🔄 Resuming radio with: {self.last_played_song.title}...")
            
            # Restore radio state
            self.radio_active = True
            self.radio_queue = self.radio_state_when_stopped['queue']
            self.radio_current_song = self.radio_state_when_stopped['current_song']
            self.radio_original_song = self.radio_state_when_stopped['original_song']
            self.radio_queue_visible = self.radio_state_when_stopped['queue_visible']
            self.stop_radio_monitoring = False
            
            # Show radio queue if it was visible
            if self.radio_queue_visible:
                self.query_one(".radio-panel").display = True
                await self.update_radio_queue_display()
            
            # Resume playing the song
            await self.play_song(self.last_played_song, from_radio=True)
            
        else:
            # Resume regular playback
            self.update_status(f"▶️  Resuming: {self.last_played_song.title} - {self.last_played_song.artist}")
            await self.play_song(self.last_played_song)

    async def action_start_radio(self) -> None:
        """Action to start radio based on current song."""
        if self.radio_active:
            self.update_status("📻 Radio is already active!")
            return
        await self.start_radio()

    async def action_next_song(self) -> None:
        """Action to play next song in radio."""
        if not self.radio_active:
            self.update_status("❌ Radio is not active.")
            return
        await self.play_next_radio_song()

    async def action_stop_radio(self) -> None:
        """Action to stop radio mode."""
        if not self.radio_active:
            self.update_status("❌ Radio is not active.")
            return
        await self.stop_radio()

    def action_toggle_radio_queue(self) -> None:
        """Action to toggle radio queue visibility."""
        radio_panel = self.query_one(".radio-panel")
        if self.radio_queue_visible:
            radio_panel.display = False
            self.radio_queue_visible = False
            self.update_status("📻 Radio queue hidden.")
        else:
            radio_panel.display = True
            self.radio_queue_visible = True
            self.update_status("📻 Radio queue shown.")

    def action_quit(self) -> None:
        """Action to quit the application."""
        # Save state before quitting so music can continue
        self.save_state()
        
        # Don't cleanup processes - let music continue in background
        self.update_status("👋 App closed. Music continues in background.")
        
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