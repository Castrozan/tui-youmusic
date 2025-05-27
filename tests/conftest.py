"""
Pytest configuration and shared fixtures for TUI YouTube Music Player tests.
"""

import pytest
import asyncio
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import json

from ytmusic_tui import YTMusicTUI, SongItem, RadioQueueItem


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ytmusic():
    """Mock YTMusic API for testing."""
    mock = Mock()
    
    # Mock search results
    mock.search.return_value = [
        {
            "title": "Test Song 1",
            "artists": [{"name": "Test Artist 1"}],
            "videoId": "test_id_1",
            "duration": "3:30"
        },
        {
            "title": "Test Song 2", 
            "artists": [{"name": "Test Artist 2"}],
            "videoId": "test_id_2",
            "duration": "4:15"
        }
    ]
    
    # Mock radio playlist
    mock.get_watch_playlist.return_value = {
        "tracks": [
            {
                "title": "Radio Song 1",
                "artists": [{"name": "Radio Artist 1"}],
                "videoId": "radio_id_1",
                "duration": "3:45"
            },
            {
                "title": "Radio Song 2",
                "artists": [{"name": "Radio Artist 2"}],
                "videoId": "radio_id_2", 
                "duration": "4:00"
            }
        ]
    }
    
    return mock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch('subprocess.Popen') as mock_popen:
        # Mock process object
        mock_process = Mock()
        mock_process.poll.return_value = None  # Running
        mock_process.terminate.return_value = None
        mock_process.kill.return_value = None
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_yt_dlp():
    """Mock yt-dlp for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = json.dumps({
            "url": "https://mock-stream-url.com/audio.m4a",
            "title": "Test Song",
            "duration": 210
        })
        mock_run.return_value.returncode = 0
        yield mock_run


@pytest.fixture
def temp_state_file():
    """Create a temporary state file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


@pytest.fixture
def sample_song_items():
    """Create sample SongItem objects for testing."""
    return [
        SongItem("Test Song 1", "Test Artist 1", "test_id_1", "3:30"),
        SongItem("Test Song 2", "Test Artist 2", "test_id_2", "4:15"),
        SongItem("Test Song 3", "Test Artist 3", "test_id_3", "2:45")
    ]


@pytest.fixture
def sample_radio_queue_items():
    """Create sample RadioQueueItem objects for testing."""
    return [
        RadioQueueItem("Radio Song 1", "Radio Artist 1", "radio_id_1", "3:45", is_current=True),
        RadioQueueItem("Radio Song 2", "Radio Artist 2", "radio_id_2", "4:00", is_current=False),
        RadioQueueItem("Radio Song 3", "Radio Artist 3", "radio_id_3", "3:15", is_current=False)
    ]


@pytest.fixture
def app_instance(mock_ytmusic, temp_state_file):
    """Create a YTMusicTUI app instance for testing."""
    with patch('ytmusic_tui.YTMusic', return_value=mock_ytmusic):
        app = YTMusicTUI()
        app.state_file = temp_state_file
        # Set the ytmusic attribute directly for testing
        app.ytmusic = mock_ytmusic
        return app


@pytest.fixture
def mock_psutil():
    """Mock psutil for process management testing."""
    with patch('psutil.process_iter') as mock_iter:
        mock_process = Mock()
        mock_process.info = {
            'pid': 12345,
            'name': 'mpv',
            'cmdline': ['mpv', '--no-video', 'https://youtube.com/watch?v=test']
        }
        mock_process.terminate.return_value = None
        mock_iter.return_value = [mock_process]
        yield mock_iter


class MockTextualApp:
    """Mock Textual app for testing UI interactions."""
    
    def __init__(self):
        self.status_messages = []
        self.search_queries = []
        self.playing_songs = []
        
    def update_status(self, message):
        self.status_messages.append(message)
        
    async def perform_search(self, query):
        self.search_queries.append(query)
        
    async def play_song(self, song_item, from_radio=False):
        self.playing_songs.append((song_item, from_radio))


@pytest.fixture
def mock_textual_app():
    """Mock Textual app for UI testing."""
    return MockTextualApp()


# Test data constants
TEST_SEARCH_RESULTS = [
    {
        "title": "Bohemian Rhapsody",
        "artists": [{"name": "Queen"}],
        "videoId": "fJ9rUzIMcZQ",
        "duration": "5:55"
    },
    {
        "title": "Imagine",
        "artists": [{"name": "John Lennon"}],
        "videoId": "VOgFZfRVaww", 
        "duration": "3:03"
    },
    {
        "title": "Hotel California",
        "artists": [{"name": "Eagles"}],
        "videoId": "09839DpTctU",
        "duration": "6:30"
    }
]

TEST_RADIO_TRACKS = [
    {
        "title": "We Will Rock You",
        "artists": [{"name": "Queen"}],
        "videoId": "yydlX7c8HbY",
        "duration": "2:02"
    },
    {
        "title": "Another One Bites The Dust",
        "artists": [{"name": "Queen"}],
        "videoId": "fJ9rUzIMcZQ",
        "duration": "3:35"
    },
    {
        "title": "Don't Stop Me Now",
        "artists": [{"name": "Queen"}],
        "videoId": "HgzGwKwLmgM",
        "duration": "3:29"
    }
] 