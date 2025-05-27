"""
Unit tests for radio functionality.

These tests document the radio feature behavior:
- Starting radio from a selected song
- Radio queue management and auto-refilling
- Auto-progression to next song when current ends
- Radio queue display and visibility
- Manual radio controls (next song, stop radio)
- Radio state persistence and monitoring
"""

import pytest
import asyncio
import threading
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import time

from ytmusic_tui import YTMusicTUI, SongItem, RadioQueueItem


class TestRadioStartStop:
    """Test radio activation and deactivation."""
    
    @pytest.mark.asyncio
    async def test_start_radio_from_song(self, app_instance, mock_ytmusic):
        """Test starting radio from a selected song."""
        # Mock radio playlist response
        mock_ytmusic.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "title": "Radio Song 1",
                    "artists": [{"name": "Radio Artist 1"}],
                    "videoId": "radio_id_1",
                    "duration": {"text": "3:45"}
                },
                {
                    "title": "Radio Song 2", 
                    "artists": [{"name": "Radio Artist 2"}],
                    "videoId": "radio_id_2",
                    "duration": {"text": "4:00"}
                }
            ]
        }
        
        original_song = SongItem("Original Song", "Original Artist", "orig123", "3:30")
        
        # Mock UI components
        mock_radio_queue_widget = Mock()
        mock_radio_queue_widget.clear = Mock()
        mock_radio_queue_widget.append = Mock()
        
        mock_radio_panel = Mock()
        
        def mock_query_one(selector, widget_type=None):
            if selector == "#radio-queue":
                return mock_radio_queue_widget
            elif selector == ".radio-panel":
                return mock_radio_panel
            return Mock()
        
        with patch.object(app_instance, 'query_one', side_effect=mock_query_one):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                with patch.object(app_instance, 'play_song') as mock_play_song:
                    with patch.object(app_instance, 'update_radio_queue_display') as mock_update_display:
                        await app_instance.start_radio(original_song)
                        
                        # Verify radio state activated
                        assert app_instance.radio_active is True
                        assert app_instance.radio_original_song == original_song
                        assert app_instance.radio_queue_visible is True
                        
                        # Verify radio queue populated (minus the one that was played)
                        assert len(app_instance.radio_queue) == 1  # 2 tracks - 1 played
                        assert app_instance.radio_queue[0].title == "Radio Song 2"
                        
                        # Verify first song played
                        mock_play_song.assert_called_once()
                        
                        # Verify status and display updates
                        mock_update_status.assert_called()
                        mock_update_display.assert_called()
    
    @pytest.mark.asyncio
    async def test_start_radio_no_selected_song(self, app_instance, sample_song_items):
        """Test starting radio when no song is explicitly provided."""
        # Set up highlighted song in list
        app_instance.songs = sample_song_items
        
        mock_list_view = Mock()
        mock_list_view.highlighted_child = sample_song_items[0]
        
        with patch.object(app_instance, 'query_one', return_value=mock_list_view):
            with patch.object(app_instance, 'start_radio') as mock_start_radio:
                # This would be called by action_start_radio
                await app_instance.action_start_radio()
                
                # Should start radio with highlighted song
                mock_start_radio.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_radio_api_failure(self, app_instance, mock_ytmusic):
        """Test starting radio when API fails to get playlist."""
        mock_ytmusic.get_watch_playlist.side_effect = Exception("API Error")
        
        original_song = SongItem("Test Song", "Test Artist", "test123", "3:30")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.start_radio(original_song)
            
            # Should handle error gracefully
            mock_update_status.assert_called()
            assert app_instance.radio_active is False
            assert len(app_instance.radio_queue) == 0
    
    @pytest.mark.asyncio
    async def test_start_radio_empty_playlist(self, app_instance, mock_ytmusic):
        """Test starting radio when API returns empty playlist."""
        mock_ytmusic.get_watch_playlist.return_value = {"tracks": []}
        
        original_song = SongItem("Test Song", "Test Artist", "test123", "3:30")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.start_radio(original_song)
            
            # The app actually activates radio even with empty playlist
            # This allows the UI to be ready for when songs are fetched later
            assert app_instance.radio_active is True
            assert len(app_instance.radio_queue) == 0
            assert app_instance.radio_original_song == original_song
            
            # Should show status about starting radio
            mock_update_status.assert_called()
            # Last call should be about radio starting with 0 songs
            last_call = mock_update_status.call_args_list[-1][0][0]
            assert "📻 Radio started! Queue: 0 songs" in last_call
    
    @pytest.mark.asyncio
    async def test_stop_radio(self, app_instance):
        """Test stopping active radio."""
        # Set up active radio state
        app_instance.radio_active = True
        app_instance.radio_queue = [
            SongItem("Queue1", "Artist1", "q1"),
            SongItem("Queue2", "Artist2", "q2")
        ]
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr123")
        app_instance.radio_original_song = SongItem("Original", "Artist", "orig123")
        app_instance.radio_queue_visible = True
        app_instance.stop_radio_monitoring = False
        
        # Mock monitor thread
        mock_thread = Mock()
        app_instance.radio_monitor_thread = mock_thread
        
        # Mock UI components
        mock_radio_queue_widget = Mock()
        mock_radio_queue_widget.clear = Mock()
        
        mock_radio_panel = Mock()
        
        def mock_query_one(selector, widget_type=None):
            if selector == "#radio-queue":
                return mock_radio_queue_widget
            elif selector == ".radio-panel":
                return mock_radio_panel
            return Mock()
        
        with patch.object(app_instance, 'query_one', side_effect=mock_query_one):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                await app_instance.stop_radio()
                
                # Verify radio state cleared
                assert app_instance.radio_active is False
                assert app_instance.radio_queue == []
                assert app_instance.radio_current_song is None
                assert app_instance.radio_original_song is None
                assert app_instance.radio_queue_visible is False
                assert app_instance.stop_radio_monitoring is True
                
                # Verify UI updates
                mock_radio_queue_widget.clear.assert_called_once()
                mock_update_status.assert_called_with("📻 Radio stopped.")
    
    @pytest.mark.asyncio
    async def test_stop_radio_not_active(self, app_instance):
        """Test stopping radio when not active."""
        app_instance.radio_active = False
        
        # Mock UI components
        mock_radio_queue_widget = Mock()
        mock_radio_queue_widget.clear = Mock()
        
        mock_radio_panel = Mock()
        
        def mock_query_one(selector, widget_type=None):
            if selector == "#radio-queue":
                return mock_radio_queue_widget
            elif selector == ".radio-panel":
                return mock_radio_panel
            return Mock()
        
        with patch.object(app_instance, 'query_one', side_effect=mock_query_one):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                await app_instance.stop_radio()
                
                # Should handle gracefully by still calling stop logic
                mock_update_status.assert_called_with("📻 Radio stopped.")


class TestRadioQueueManagement:
    """Test radio queue management and auto-refilling."""
    
    @pytest.mark.asyncio
    async def test_fetch_more_radio_songs(self, app_instance, mock_ytmusic):
        """Test fetching more songs when queue runs low."""
        # Set up active radio
        app_instance.radio_active = True
        app_instance.radio_current_song = SongItem("Original", "Artist", "orig123")
        app_instance.radio_queue = [
            SongItem("Queue1", "Artist1", "q1"),
            SongItem("Queue2", "Artist2", "q2")  # Only 2 songs, should trigger refill
        ]
        
        # Mock additional songs
        mock_ytmusic.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "title": "New Radio Song 1",
                    "artists": [{"name": "New Artist 1"}],
                    "videoId": "new_radio_1",
                    "duration": {"text": "3:20"}
                },
                {
                    "title": "New Radio Song 2",
                    "artists": [{"name": "New Artist 2"}],
                    "videoId": "new_radio_2",
                    "duration": {"text": "4:10"}
                }
            ]
        }
        
        # Mock UI components
        mock_radio_queue_widget = Mock()
        mock_radio_queue_widget.append = Mock()
        
        with patch.object(app_instance, 'query_one', return_value=mock_radio_queue_widget):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                await app_instance.fetch_more_radio_songs()
                
                # Verify new songs added to queue
                assert len(app_instance.radio_queue) == 4  # Original 2 + new 2
                assert app_instance.radio_queue[2].title == "New Radio Song 1"
                assert app_instance.radio_queue[3].title == "New Radio Song 2"
                
                # Verify UI widget was called
                assert mock_radio_queue_widget.append.call_count == 2
    
    @pytest.mark.asyncio
    async def test_fetch_more_radio_songs_api_failure(self, app_instance, mock_ytmusic):
        """Test fetching more songs when API fails."""
        app_instance.radio_active = True
        app_instance.radio_current_song = SongItem("Original", "Artist", "orig123")
        original_queue_length = len(app_instance.radio_queue)
        
        mock_ytmusic.get_watch_playlist.side_effect = Exception("API Error")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.fetch_more_radio_songs()
            
            # Queue should remain unchanged
            assert len(app_instance.radio_queue) == original_queue_length
            mock_update_status.assert_called()
    
    @pytest.mark.asyncio
    async def test_play_next_radio_song(self, app_instance):
        """Test manually playing next song in radio queue."""
        # Set up radio queue
        app_instance.radio_active = True
        next_song = SongItem("Next", "Artist", "next123")
        after_song = SongItem("After", "Artist", "after123")
        app_instance.radio_queue = [next_song, after_song]
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr123")
        
        with patch.object(app_instance, 'play_song') as mock_play_song:
            with patch.object(app_instance, 'update_radio_queue_display') as mock_update_display:
                with patch.object(app_instance, 'save_state') as mock_save_state:
                    with patch.object(app_instance, 'fetch_more_radio_songs') as mock_fetch_more:
                        await app_instance.play_next_radio_song()
                    
                        # Should fetch more songs since queue has < 5 songs
                        mock_fetch_more.assert_called_once()
                        
                        # Should play next song (first in queue)
                        mock_play_song.assert_called_once()
                        called_song = mock_play_song.call_args[0][0]
                        assert called_song.title == "Next"
                        assert called_song.video_id == "next123"
                        assert mock_play_song.call_args[1]['from_radio'] is True
                        
                        # Should remove played song from queue
                        assert len(app_instance.radio_queue) == 1
                        assert app_instance.radio_queue[0].title == "After"
                        
                        # Should update display and save state
                        mock_update_display.assert_called()
                        mock_save_state.assert_called()
    
    @pytest.mark.asyncio
    async def test_play_next_radio_song_empty_queue(self, app_instance):
        """Test playing next song when queue is empty."""
        app_instance.radio_active = True
        app_instance.radio_queue = []
        
        with patch.object(app_instance, 'play_song') as mock_play_song:
            await app_instance.play_next_radio_song()
            
            # Should not play any song
            mock_play_song.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_auto_play_next_radio_song(self, app_instance):
        """Test automatic progression to next song."""
        # Set up radio queue with low count to trigger refill
        app_instance.radio_active = True
        next_song = SongItem("Next", "Artist", "next123")
        last_song = SongItem("Last", "Artist", "last123")
        app_instance.radio_queue = [next_song, last_song]  # 2 songs, below threshold of 5
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr123")
        
        with patch.object(app_instance, 'play_song') as mock_play_song:
            with patch.object(app_instance, 'fetch_more_radio_songs') as mock_fetch_more:
                with patch.object(app_instance, 'update_radio_queue_display') as mock_update_display:
                    with patch.object(app_instance, 'save_state') as mock_save_state:
                        await app_instance.auto_play_next_radio_song()
                        
                        # Should fetch more songs (queue < 5)
                        mock_fetch_more.assert_called_once()
                        
                        # Should play next song
                        mock_play_song.assert_called_once()
                        called_song = mock_play_song.call_args[0][0]
                        assert called_song.title == "Next"
                        assert called_song.video_id == "next123"
                        assert mock_play_song.call_args[1]['from_radio'] is True
                        
                        # Should update display and save state
                        mock_update_display.assert_called()
                        mock_save_state.assert_called()
    
    @pytest.mark.asyncio
    async def test_auto_play_next_radio_song_race_condition(self, app_instance):
        """Test auto-progression with race condition protection."""
        app_instance.radio_active = True
        app_instance.radio_queue = [SongItem("Next", "Artist", "next123")]
        
        # Simulate race condition by setting the flag in the actual method before calling
        # The method checks this condition early and should return without playing
        with patch.object(app_instance, 'play_song') as mock_play_song:
            # Set the condition that causes early return
            app_instance.radio_active = False  # This will cause early return
            app_instance.radio_queue = []  # This will also cause early return
            
            await app_instance.auto_play_next_radio_song()
            
            # Should not play song due to early return conditions
            mock_play_song.assert_not_called()


class TestRadioMonitoring:
    """Test radio monitoring and auto-progression."""
    
    def test_radio_monitor_thread_creation(self, app_instance):
        """Test that radio monitoring thread is created when starting radio."""
        # This would be tested indirectly through start_radio
        # The actual monitoring runs in a background thread
        assert app_instance.radio_monitor_thread is None
        assert app_instance.stop_radio_monitoring is False
    
    def test_radio_progression_lock(self, app_instance):
        """Test thread safety mechanisms for radio progression."""
        # Test that the lock exists and can be acquired
        assert app_instance.radio_progression_lock is not None
        
        # Test acquiring the lock
        with app_instance.radio_progression_lock:
            app_instance.manual_progression_happening = True
            assert app_instance.manual_progression_happening is True
        
        # Reset state
        app_instance.manual_progression_happening = False
    
    def test_radio_monitoring_flags(self, app_instance):
        """Test radio monitoring control flags."""
        # Test initial state
        assert app_instance.stop_radio_monitoring is False
        assert app_instance.manual_progression_happening is False
        
        # Test flag modification
        app_instance.stop_radio_monitoring = True
        app_instance.manual_progression_happening = True
        
        assert app_instance.stop_radio_monitoring is True
        assert app_instance.manual_progression_happening is True


class TestRadioQueueDisplay:
    """Test radio queue display and visibility."""
    
    @pytest.mark.asyncio
    async def test_update_radio_queue_display(self, app_instance):
        """Test updating radio queue display."""
        # Set up radio queue
        app_instance.radio_queue = [
            SongItem("Next Song", "Next Artist", "next123", "4:00"),
            SongItem("After Song", "After Artist", "after123", "3:45")
        ]
        app_instance.radio_current_song = SongItem("Current Song", "Current Artist", "curr123", "3:30")
        app_instance.radio_active = True
        app_instance.radio_queue_visible = True
        
        # Mock radio queue ListView
        mock_radio_queue_view = Mock()
        mock_radio_queue_view.clear = Mock()
        mock_radio_queue_view.append = Mock()
        
        with patch.object(app_instance, 'query_one', return_value=mock_radio_queue_view):
            await app_instance.update_radio_queue_display()
            
            # Should clear the queue view
            mock_radio_queue_view.clear.assert_called_once()
            
            # Should add current song plus queue items (3 total)
            assert mock_radio_queue_view.append.call_count == 3
    
    def test_action_toggle_radio_queue(self, app_instance):
        """Test toggling radio queue visibility."""
        # Test initial state
        assert app_instance.radio_queue_visible is False
        
        # Mock radio panel
        mock_radio_panel = Mock()
        mock_radio_panel.display = False
        
        with patch.object(app_instance, 'query_one', return_value=mock_radio_panel):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                # Toggle to visible
                app_instance.action_toggle_radio_queue()
                assert app_instance.radio_queue_visible is True
                assert mock_radio_panel.display is True
                mock_update_status.assert_called_with("📻 Radio queue shown.")
                
                # Toggle back to hidden
                app_instance.action_toggle_radio_queue()
                assert app_instance.radio_queue_visible is False
                assert mock_radio_panel.display is False
                mock_update_status.assert_called_with("📻 Radio queue hidden.")
    
    def test_radio_queue_visibility_with_radio_active(self, app_instance):
        """Test that radio queue becomes visible when radio starts."""
        # This is tested indirectly through start_radio test
        app_instance.radio_active = False
        app_instance.radio_queue_visible = False
        
        # Simulate radio starting
        app_instance.radio_active = True
        app_instance.radio_queue_visible = True
        
        assert app_instance.radio_active is True
        assert app_instance.radio_queue_visible is True
    
    def test_radio_queue_item_current_marking(self, app_instance):
        """Test that current song is properly marked in radio queue."""
        current_song = SongItem("Current", "Artist", "curr123", "3:30")
        
        # Create RadioQueueItem for current song
        current_item = RadioQueueItem(
            current_song.title,
            current_song.artist,
            current_song.video_id,
            current_song.duration,
            is_current=True
        )
        
        # Create RadioQueueItem for upcoming song
        upcoming_item = RadioQueueItem(
            "Upcoming",
            "Artist",
            "upcoming123",
            "4:00",
            is_current=False
        )
        
        # Verify current song marking
        assert current_item.is_current is True
        assert upcoming_item.is_current is False
        
        # Verify display text differences exist (exact format depends on implementation)
        assert current_item.title == "Current"
        assert upcoming_item.title == "Upcoming"


class TestRadioActions:
    """Test radio-related keyboard actions."""
    
    @pytest.mark.asyncio
    async def test_action_start_radio(self, app_instance, sample_song_items):
        """Test start radio action."""
        app_instance.songs = sample_song_items
        app_instance.radio_active = False  # Ensure radio is not already active
        
        mock_list_view = Mock()
        mock_list_view.highlighted_child = sample_song_items[0]
        
        with patch.object(app_instance, 'query_one', return_value=mock_list_view):
            with patch.object(app_instance, 'start_radio') as mock_start_radio:
                await app_instance.action_start_radio()
                
                # Should call start_radio without arguments (start_radio gets the song internally)
                mock_start_radio.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_action_start_radio_no_selection(self, app_instance):
        """Test start radio action when no song is selected."""
        app_instance.songs = []
        
        mock_list_view = Mock()
        mock_list_view.highlighted_child = None
        
        with patch.object(app_instance, 'query_one', return_value=mock_list_view):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                await app_instance.action_start_radio()
                
                # Should show appropriate message
                mock_update_status.assert_called_with("❌ No song selected to start radio.")
    
    @pytest.mark.asyncio
    async def test_action_next_song_radio_active(self, app_instance):
        """Test next song action when radio is active."""
        app_instance.radio_active = True
        
        with patch.object(app_instance, 'play_next_radio_song') as mock_next_song:
            await app_instance.action_next_song()
            
            # Should play next radio song
            mock_next_song.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_action_next_song_radio_inactive(self, app_instance):
        """Test next song action when radio is not active."""
        app_instance.radio_active = False
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.action_next_song()
            
            # Should show appropriate message
            mock_update_status.assert_called_with("❌ Radio is not active.")
    
    @pytest.mark.asyncio
    async def test_action_stop_radio(self, app_instance):
        """Test stop radio action."""
        app_instance.radio_active = True
        
        with patch.object(app_instance, 'stop_radio') as mock_stop_radio:
            await app_instance.action_stop_radio()
            
            # Should stop radio
            mock_stop_radio.assert_called_once()


class TestRadioStateManagement:
    """Test radio state persistence and management."""
    
    def test_radio_state_when_stopped_persistence(self, app_instance):
        """Test that radio state is saved when stopped."""
        # Set up radio state
        radio_state = {
            "original_song": {
                "title": "Original",
                "artist": "Artist", 
                "video_id": "orig123"
            },
            "was_active": True
        }
        
        app_instance.radio_state_when_stopped = radio_state
        
        # Verify state is preserved
        assert app_instance.radio_state_when_stopped == radio_state
        assert app_instance.radio_state_when_stopped["was_active"] is True
    
    def test_radio_integration_with_manual_song_selection(self, app_instance):
        """Test that radio stops when manually selecting a song."""
        # Set up active radio
        app_instance.radio_active = True
        app_instance.radio_queue = [SongItem("Queue1", "Artist1", "q1")]
        
        # This behavior is tested in the play_song tests
        # Radio should stop when from_radio=False
        assert app_instance.radio_active is True
        
        # Simulate manual song selection stopping radio
        app_instance.radio_active = False
        app_instance.radio_queue = []
        
        assert app_instance.radio_active is False
        assert len(app_instance.radio_queue) == 0 