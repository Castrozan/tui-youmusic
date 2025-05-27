"""
Example configuration file for TUI YouTube Music Player.

This file shows how to customize various aspects of the application.
Copy this file to 'config.py' and modify the values as needed.

Note: This is an advanced feature and is not required for basic usage.
"""

# YouTube Music API Configuration
YTMUSIC_CONFIG = {
    # Optional: Path to authentication headers file for YouTube Music
    # Get this by following: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html
    "headers_auth": None,  # Set to "headers_auth.json" if you have one
    
    # Default search settings
    "default_search_limit": 20,  # Number of results to fetch
    "search_filter": "songs",    # Can be "songs", "videos", "albums", "artists"
}

# MPV Player Configuration
MPV_CONFIG = {
    # MPV command line arguments
    "args": [
        "--no-video",        # Audio only
        "--really-quiet",    # Minimal output
        "--no-terminal",     # Don't interfere with TUI
        "--audio-format=best",  # Use best audio quality
        "--volume=80",       # Default volume (0-100)
    ],
    
    # Alternative: Use yt-dlp for better format selection
    "use_ytdlp": False,  # Set to True to use yt-dlp for stream URLs
}

# TUI Appearance Configuration
UI_CONFIG = {
    # Application title and subtitle
    "title": "🎵 TUI YouTube Music Player",
    "subtitle": "Search and play music from YouTube Music",
    
    # Status messages
    "show_emojis": True,  # Use emojis in status messages
    
    # Search behavior
    "auto_focus_search": True,  # Focus search input on startup
    "clear_results_on_new_search": True,
}

# Keyboard Shortcuts (Advanced)
# Note: Changing these requires modifying the main application
KEYBINDINGS = {
    "quit": ["q", "ctrl+c", "escape"],
    "play": ["enter", "space"],
    "stop": ["r", "s"],
    "focus_search": ["s", "/"],
    "volume_up": ["+", "="],
    "volume_down": ["-", "_"],
}

# Cache and Performance
PERFORMANCE_CONFIG = {
    # Number of search results to keep in memory
    "max_cached_results": 100,
    
    # Timeout for network requests (seconds)
    "network_timeout": 10,
    
    # Enable logging for debugging
    "enable_logging": False,
    "log_file": "tui_youmusic.log",
}

# Example function to load custom configuration
def load_config():
    """
    Load configuration from environment variables or config files.
    This is an example of how you might implement custom configuration loading.
    """
    import os
    
    # Load from environment variables
    config = {}
    
    # YouTube Music configuration
    if os.getenv("YTMUSIC_HEADERS"):
        config["headers_auth"] = os.getenv("YTMUSIC_HEADERS")
    
    if os.getenv("YTMUSIC_SEARCH_LIMIT"):
        config["search_limit"] = int(os.getenv("YTMUSIC_SEARCH_LIMIT"))
    
    # MPV configuration
    if os.getenv("MPV_VOLUME"):
        volume = int(os.getenv("MPV_VOLUME"))
        config["mpv_volume"] = max(0, min(100, volume))  # Clamp to 0-100
    
    return config

# Example usage in main application:
# from config import YTMUSIC_CONFIG, MPV_CONFIG, UI_CONFIG
# 
# # Initialize with custom config
# ytmusic = YTMusic(YTMUSIC_CONFIG.get("headers_auth"))
# 
# # Use custom MPV args
# mpv_cmd = ["mpv"] + MPV_CONFIG["args"] + [url] 