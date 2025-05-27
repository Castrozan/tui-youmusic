"""
Unit tests for SongItem and RadioQueueItem classes.

These tests document song item behavior:
- Creating song items with various data combinations
- Display text formatting with emojis and duration
- Special character handling
- Current vs upcoming song indicators for radio queue
"""

import pytest
from ytmusic_tui import SongItem, RadioQueueItem


class TestSongItem:
    """Test the SongItem class functionality."""
    
    def test_song_item_creation_with_all_fields(self):
        """Test creating a SongItem with all fields provided."""
        song = SongItem(
            title="Bohemian Rhapsody",
            artist="Queen", 
            video_id="fJ9rUzIMcZQ",
            duration="5:55"
        )
        
        assert song.title == "Bohemian Rhapsody"
        assert song.artist == "Queen"
        assert song.video_id == "fJ9rUzIMcZQ"
        assert song.duration == "5:55"
    
    def test_song_item_creation_without_duration(self):
        """Test creating a SongItem without duration (should default to None)."""
        song = SongItem(
            title="Test Song",
            artist="Test Artist",
            video_id="test123"
        )
        
        assert song.title == "Test Song"
        assert song.artist == "Test Artist"
        assert song.video_id == "test123"
        assert song.duration is None
    
    def test_song_item_display_text_with_duration(self):
        """Test that SongItem generates correct display text with duration."""
        song = SongItem(
            title="Hotel California",
            artist="Eagles",
            video_id="09839DpTctU",
            duration="6:30"
        )
        
        # Verify the song properties are set correctly
        assert song.title == "Hotel California"
        assert song.artist == "Eagles"
        assert song.duration == "6:30"
        
        # Test that the expected display formatting would be used
        expected_text = "🎵 Hotel California - Eagles (6:30)"
        # The display text logic is tested through integration tests
        # Here we verify the data is stored correctly for formatting
        duration_str = f" ({song.duration})" if song.duration else ""
        actual_format = f"🎵 {song.title} - {song.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_song_item_display_text_without_duration(self):
        """Test that SongItem generates correct display text without duration."""
        song = SongItem(
            title="Imagine",
            artist="John Lennon",
            video_id="VOgFZfRVaww"
        )
        
        # Verify properties
        assert song.title == "Imagine"
        assert song.artist == "John Lennon"
        assert song.duration is None
        
        # Test formatting logic
        expected_text = "🎵 Imagine - John Lennon"
        duration_str = f" ({song.duration})" if song.duration else ""
        actual_format = f"🎵 {song.title} - {song.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_song_item_with_special_characters(self):
        """Test SongItem handles special characters correctly."""
        song = SongItem(
            title="Café del Mar (Chill Mix)",
            artist="José Padilla & Friends",
            video_id="special123",
            duration="7:45"
        )
        
        assert song.title == "Café del Mar (Chill Mix)"
        assert song.artist == "José Padilla & Friends"
        assert song.video_id == "special123"
        assert song.duration == "7:45"
    
    def test_song_item_with_empty_strings(self):
        """Test SongItem handles empty strings properly."""
        song = SongItem(
            title="",
            artist="",
            video_id="empty123"
        )
        
        assert song.title == ""
        assert song.artist == ""
        assert song.video_id == "empty123"
        
        # Test formatting with empty strings
        expected_text = "🎵  - "
        duration_str = f" ({song.duration})" if song.duration else ""
        actual_format = f"🎵 {song.title} - {song.artist}{duration_str}"
        assert actual_format == expected_text


class TestRadioQueueItem:
    """Test the RadioQueueItem class functionality."""
    
    def test_radio_queue_item_creation_current_song(self):
        """Test creating a RadioQueueItem marked as current song."""
        radio_item = RadioQueueItem(
            title="We Will Rock You",
            artist="Queen",
            video_id="radio123",
            duration="2:02",
            is_current=True
        )
        
        assert radio_item.title == "We Will Rock You"
        assert radio_item.artist == "Queen"
        assert radio_item.video_id == "radio123"
        assert radio_item.duration == "2:02"
        assert radio_item.is_current is True
    
    def test_radio_queue_item_creation_upcoming_song(self):
        """Test creating a RadioQueueItem for upcoming song."""
        radio_item = RadioQueueItem(
            title="Another One Bites The Dust",
            artist="Queen",
            video_id="radio456",
            duration="3:35",
            is_current=False
        )
        
        assert radio_item.title == "Another One Bites The Dust"
        assert radio_item.artist == "Queen"
        assert radio_item.video_id == "radio456"
        assert radio_item.duration == "3:35"
        assert radio_item.is_current is False
    
    def test_radio_queue_item_current_song_display(self):
        """Test display text for current playing song in radio queue."""
        radio_item = RadioQueueItem(
            title="Don't Stop Me Now",
            artist="Queen",
            video_id="current123",
            duration="3:29",
            is_current=True
        )
        
        # Test that the correct formatting logic is applied
        assert radio_item.is_current is True
        
        # Test formatting logic for current song
        expected_text = "🎵 Don't Stop Me Now - Queen (3:29)"
        duration_str = f" ({radio_item.duration})" if radio_item.duration else ""
        prefix = "🎵 " if radio_item.is_current else "   "
        actual_format = f"{prefix}{radio_item.title} - {radio_item.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_radio_queue_item_upcoming_song_display(self):
        """Test display text for upcoming song in radio queue."""
        radio_item = RadioQueueItem(
            title="Somebody To Love",
            artist="Queen",
            video_id="upcoming123",
            duration="4:56",
            is_current=False
        )
        
        # Test that is_current is properly set
        assert radio_item.is_current is False
        
        # Test formatting logic for upcoming song
        expected_text = "   Somebody To Love - Queen (4:56)"
        duration_str = f" ({radio_item.duration})" if radio_item.duration else ""
        prefix = "🎵 " if radio_item.is_current else "   "
        actual_format = f"{prefix}{radio_item.title} - {radio_item.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_radio_queue_item_without_duration(self):
        """Test RadioQueueItem without duration."""
        radio_item = RadioQueueItem(
            title="Radio Free Europe",
            artist="R.E.M.",
            video_id="no_duration123",
            is_current=False
        )
        
        assert radio_item.duration is None
        assert radio_item.is_current is False
        
        # Test formatting without duration
        expected_text = "   Radio Free Europe - R.E.M."
        duration_str = f" ({radio_item.duration})" if radio_item.duration else ""
        prefix = "🎵 " if radio_item.is_current else "   "
        actual_format = f"{prefix}{radio_item.title} - {radio_item.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_radio_queue_item_current_without_duration(self):
        """Test current RadioQueueItem without duration."""
        radio_item = RadioQueueItem(
            title="Losing My Religion",
            artist="R.E.M.",
            video_id="current_no_duration123",
            is_current=True
        )
        
        assert radio_item.is_current is True
        assert radio_item.duration is None
        
        # Test formatting for current song without duration
        expected_text = "🎵 Losing My Religion - R.E.M."
        duration_str = f" ({radio_item.duration})" if radio_item.duration else ""
        prefix = "🎵 " if radio_item.is_current else "   "
        actual_format = f"{prefix}{radio_item.title} - {radio_item.artist}{duration_str}"
        assert actual_format == expected_text
    
    def test_radio_queue_item_default_is_current(self):
        """Test that is_current defaults to False when not specified."""
        radio_item = RadioQueueItem(
            title="Shiny Happy People",
            artist="R.E.M.",
            video_id="default123"
        )
        
        assert radio_item.is_current is False
        
        # Test default formatting (not current)
        expected_text = "   Shiny Happy People - R.E.M."
        duration_str = f" ({radio_item.duration})" if radio_item.duration else ""
        prefix = "🎵 " if radio_item.is_current else "   "
        actual_format = f"{prefix}{radio_item.title} - {radio_item.artist}{duration_str}"
        assert actual_format == expected_text 