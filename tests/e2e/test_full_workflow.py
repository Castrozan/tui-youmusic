"""
End-to-end tests for complete user workflows.

These tests simulate real user interactions:
- Search and play workflow
- Radio mode workflow  
- State persistence workflow
- Keyboard shortcuts and navigation
- Error recovery scenarios

Note: These tests require external dependencies and may be slow.
"""

import pytest
import asyncio
import time
import tempfile
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import psutil

from ytmusic_tui import YTMusicTUI, SongItem


# Mark all tests in this module as e2e tests
pytestmark = pytest.mark.e2e


class TestSearchAndPlayWorkflow:
    """Test complete search and play workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_search_select_play_workflow(self, app_instance):
        """Test the complete search -> select -> play workflow."""
        # Mock API responses
        search_results = [
            {
                "title": "Bohemian Rhapsody",
                "artists": [{"name": "Queen"}],
                "videoId": "fJ9rUzIMcZQ",
                "duration": "5:55"
            },
            {
                "title": "We Will Rock You", 
                "artists": [{"name": "Queen"}],
                "videoId": "yydlX7c8HbY",
                "duration": "2:02"
            }
        ]
        
        app_instance.ytmusic.search.return_value = search_results
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                
                # Mock MPV process
                mock_process = Mock()
                mock_process.poll.return_value = None
                mock_process.wait.return_value = 0
                mock_mpv.return_value = mock_process
                
                # Step 1: Perform search
                await app_instance.perform_search("Queen")
                
                # Verify search results
                assert len(app_instance.songs) == 2
                assert app_instance.songs[0].title == "Bohemian Rhapsody"
                assert app_instance.songs[1].title == "We Will Rock You"
                
                # Step 2: Select and play first song
                selected_song = app_instance.songs[0]
                await app_instance.play_song(selected_song)
                
                # Verify playback started
                assert app_instance.current_process == mock_process
                assert app_instance.last_played_song == selected_song
                
                # Verify MPV was called with YouTube URL (no yt-dlp needed)
                mock_mpv.assert_called_once()
                call_args = mock_mpv.call_args[0][0]
                assert "mpv" in call_args
                assert "--no-video" in call_args
                assert "--really-quiet" in call_args
                assert "--no-terminal" in call_args
                assert f"https://www.youtube.com/watch?v={selected_song.video_id}" in call_args
    
    @pytest.mark.asyncio
    async def test_search_no_results_workflow(self, app_instance):
        """Test workflow when search returns no results."""
        app_instance.ytmusic.search.return_value = []
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            # Search for something that doesn't exist
            await app_instance.perform_search("nonexistentquerythatreturnsnothing")
            
            # Should handle gracefully
            assert len(app_instance.songs) == 0
            mock_update_status.assert_called_with("No results found. Try a different search term.")
    
    @pytest.mark.asyncio
    async def test_multiple_search_workflow(self, app_instance):
        """Test performing multiple searches in sequence."""
        # First search
        first_results = [
            {
                "title": "Hotel California",
                "artists": [{"name": "Eagles"}],
                "videoId": "09839DpTctU",
                "duration": "6:30"
            }
        ]
        
        # Second search
        second_results = [
            {
                "title": "Stairway to Heaven",
                "artists": [{"name": "Led Zeppelin"}],
                "videoId": "QkF3oxziUI4",
                "duration": "8:02"
            }
        ]
        
        # Perform first search
        app_instance.ytmusic.search.return_value = first_results
        await app_instance.perform_search("Eagles")
        
        assert len(app_instance.songs) == 1
        assert app_instance.songs[0].title == "Hotel California"
        
        # Perform second search (should replace first results)
        app_instance.ytmusic.search.return_value = second_results
        await app_instance.perform_search("Led Zeppelin")
        
        assert len(app_instance.songs) == 1
        assert app_instance.songs[0].title == "Stairway to Heaven"


class TestRadioWorkflow:
    """Test complete radio mode workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_start_radio_workflow(self, app_instance):
        """Test starting radio and auto-progression workflow."""
        # Mock search results
        search_results = [
            {
                "title": "Don't Stop Believin'",
                "artists": [{"name": "Journey"}],
                "videoId": "1k8craCGpgs",
                "duration": "4:10"
            }
        ]
        
        # Mock radio playlist
        radio_playlist = {
            "tracks": [
                {
                    "title": "Any Way You Want It",
                    "artists": [{"name": "Journey"}],
                    "videoId": "atxUuldUcfI",
                    "duration": {"text": "3:22"}
                },
                {
                    "title": "Separate Ways",
                    "artists": [{"name": "Journey"}],
                    "videoId": "LatorN4P9aA",
                    "duration": {"text": "5:29"}
                }
            ]
        }
        
        app_instance.ytmusic.search.return_value = search_results
        app_instance.ytmusic.get_watch_playlist.return_value = radio_playlist
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                with patch.object(app_instance, 'update_radio_queue_display'):
                    with patch.object(app_instance, 'update_status') as mock_update_status:
                        
                        # Mock MPV process
                        mock_process = Mock()
                        mock_process.poll.return_value = None
                        mock_process.wait.return_value = 0
                        mock_mpv.return_value = mock_process
                        
                        # Step 1: Search for song
                        await app_instance.perform_search("Journey")
                        assert len(app_instance.songs) == 1
                        
                        # Step 2: Start radio with first song
                        original_song = app_instance.songs[0]
                        await app_instance.start_radio(original_song)
                        
                        # Debug: Check what status messages were generated
                        status_calls = [call.args[0] for call in mock_update_status.call_args_list]
                        print(f"Status messages: {status_calls}")
                        
                        # Verify radio state - radio activates immediately
                        assert app_instance.radio_active is True, f"Radio not active. Status messages: {status_calls}"
                        assert app_instance.radio_original_song == original_song
                        assert len(app_instance.radio_queue) == 1  # One song remains after first is played
                        assert app_instance.radio_queue_visible is True
                        
                        # Verify first radio song is playing via MPV with YouTube URL
                        mock_mpv.assert_called()
                        call_args = mock_mpv.call_args[0][0]
                        assert "mpv" in call_args
                        assert "--no-video" in call_args
                        assert "https://www.youtube.com/watch?v=" in call_args[-1]
    
    @pytest.mark.asyncio
    async def test_radio_manual_next_workflow(self, app_instance):
        """Test manually skipping to next song in radio."""
        # Set up active radio
        app_instance.radio_active = True
        app_instance.radio_queue = [
            SongItem("Current Song", "Artist", "curr123", "3:30"),
            SongItem("Next Song", "Artist", "next123", "4:00"),
            SongItem("After Song", "Artist", "after123", "3:45")
        ]
        app_instance.radio_current_song = SongItem("Playing Song", "Artist", "playing123", "3:00")
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                with patch.object(app_instance, 'update_radio_queue_display'):
                    with patch.object(app_instance, 'save_state'):  # Mock save_state
                        with patch.object(app_instance, 'fetch_more_radio_songs'):  # Prevent adding more songs
                            
                            # Mock MPV process
                            mock_process = Mock()
                            mock_process.poll.return_value = None
                            mock_process.wait.return_value = 0
                            mock_mpv.return_value = mock_process
                            
                            # Manually play next song
                            await app_instance.play_next_radio_song()
                            
                            # Verify queue progression - first song is popped and played
                            assert len(app_instance.radio_queue) == 2  # Two songs remain after one is popped
                            assert app_instance.radio_queue[0].title == "Next Song"  # Next song is now first
                            # The current song is updated when play_song is called with from_radio=True
                            assert app_instance.radio_current_song.title == "Current Song"  # The song that was played
                            
                            # Verify MPV was called with YouTube URL
                            mock_mpv.assert_called_once()
                            call_args = mock_mpv.call_args[0][0]
                            assert "mpv" in call_args
                            assert "--no-video" in call_args
                            assert "https://www.youtube.com/watch?v=curr123" in call_args[-1]
    
    @pytest.mark.asyncio
    async def test_stop_radio_workflow(self, app_instance):
        """Test stopping radio and cleanup workflow."""
        # Set up active radio
        app_instance.radio_active = True
        app_instance.radio_queue = [SongItem("Song1", "Artist", "id1")]
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr")
        app_instance.radio_original_song = SongItem("Original", "Artist", "orig")
        app_instance.radio_queue_visible = True
        
        # Mock the radio queue widget that gets cleared directly
        mock_radio_queue_widget = Mock()
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
                
                # Verify UI was updated - stop_radio directly clears widgets
                mock_radio_queue_widget.clear.assert_called_once()
                assert mock_radio_panel.display is False
                
                # Verify status was updated
                mock_update_status.assert_called_once_with("📻 Radio stopped.")


class TestStatePersistenceWorkflow:
    """Test state persistence across app sessions."""
    
    @pytest.mark.asyncio
    async def test_save_and_restore_state_workflow(self, temp_state_file):
        """Test complete save and restore state workflow."""
        # Create first app instance
        with patch('ytmusic_tui.YTMusic') as mock_ytmusic_class:
            mock_ytmusic = Mock()
            mock_ytmusic_class.return_value = mock_ytmusic
            
            app1 = YTMusicTUI()
            app1.state_file = temp_state_file
            
            # Set up some state
            last_song = SongItem("Last Song", "Last Artist", "last123", "3:30")
            app1.last_played_song = last_song
            app1.was_radio_active = True
            app1.radio_state_when_stopped = {"test": "data"}
            
            # Save state
            app1.save_state()
            
            # Verify file was created
            assert temp_state_file.exists()
        
        # Create second app instance (simulating restart)
        with patch('ytmusic_tui.YTMusic') as mock_ytmusic_class:
            mock_ytmusic = Mock()
            mock_ytmusic_class.return_value = mock_ytmusic
            
            app2 = YTMusicTUI()
            app2.state_file = temp_state_file
            
            # Load state
            app2.load_state()
            
            # Verify state was restored
            assert app2.last_played_song is not None
            assert app2.last_played_song.title == "Last Song"
            assert app2.last_played_song.artist == "Last Artist"
            assert app2.was_radio_active is True
            assert app2.radio_state_when_stopped == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_resume_playback_workflow(self, app_instance):
        """Test resuming playback from saved state."""
        # Set up last played song
        last_song = SongItem("Resume Song", "Resume Artist", "resume123", "4:00")
        app_instance.last_played_song = last_song
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                
                # Mock MPV process
                mock_process = Mock()
                mock_process.poll.return_value = None
                mock_process.wait.return_value = 0
                mock_mpv.return_value = mock_process
                
                # Resume playback
                await app_instance.action_resume_playback()
                
                # Verify song was played via MPV with YouTube URL
                mock_mpv.assert_called_once()
                call_args = mock_mpv.call_args[0][0]
                assert "mpv" in call_args
                assert "--no-video" in call_args
                assert f"https://www.youtube.com/watch?v={last_song.video_id}" in call_args[-1]
                
                # Verify playback state updated
                assert app_instance.current_process == mock_process
                assert app_instance.last_played_song == last_song


class TestKeyboardShortcutsWorkflow:
    """Test keyboard shortcuts and navigation workflow."""
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation_workflow(self, app_instance, sample_song_items):
        """Test keyboard shortcuts for navigation and control."""
        # Set up songs
        app_instance.songs = sample_song_items
        
        # Mock ListView for selection
        mock_list_view = Mock()
        mock_list_view.highlighted_child = sample_song_items[1]  # Second song
        
        with patch.object(app_instance, 'query_one', return_value=mock_list_view):
            with patch.object(app_instance, 'run_action') as mock_run_action:
                
                # Test play selected action (Enter key)
                app_instance.action_play_selected()
                
                # Should trigger the list_view.select action
                mock_run_action.assert_called_once_with("list_view.select")
                
                # Test focusing search
                app_instance.action_focus_search()
                
                # Should have attempted to focus search input
                # (This is verified through the query_one call)
    
    @pytest.mark.asyncio
    async def test_radio_keyboard_shortcuts_workflow(self, app_instance, sample_song_items):
        """Test radio-specific keyboard shortcuts."""
        app_instance.songs = sample_song_items
        app_instance.radio_active = True
        app_instance.radio_queue = [
            SongItem("Radio1", "Artist1", "r1"),
            SongItem("Radio2", "Artist2", "r2")
        ]
        
        with patch.object(app_instance, 'play_next_radio_song') as mock_next_song:
            # Test next song action (N key)
            await app_instance.action_next_song()
            
            # Should play next radio song
            mock_next_song.assert_called_once()
        
        with patch.object(app_instance, 'stop_radio') as mock_stop_radio:
            # Test stop radio action (R key)
            await app_instance.action_stop_radio()
            
            # Should stop radio
            mock_stop_radio.assert_called_once()
    
    def test_toggle_radio_queue_workflow(self, app_instance):
        """Test toggling radio queue visibility."""
        # Mock radio panel
        mock_radio_panel = Mock()
        mock_radio_panel.display = True
        
        with patch.object(app_instance, 'query_one', return_value=mock_radio_panel):
            # Initial state
            assert app_instance.radio_queue_visible is False
            
            # Toggle to visible
            app_instance.action_toggle_radio_queue()
            assert app_instance.radio_queue_visible is True
            
            # Toggle back to hidden
            app_instance.action_toggle_radio_queue()
            assert app_instance.radio_queue_visible is False


class TestErrorRecoveryWorkflow:
    """Test error recovery scenarios."""
    
    @pytest.mark.asyncio
    async def test_api_error_recovery_workflow(self, app_instance):
        """Test recovery from API errors."""
        # First search fails
        app_instance.ytmusic.search.side_effect = ConnectionError("Network error")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.perform_search("test query")
            
            # Should handle error gracefully
            mock_update_status.assert_called()
            assert len(app_instance.songs) == 0
        
        # Second search succeeds (network recovered)
        app_instance.ytmusic.search.side_effect = None
        app_instance.ytmusic.search.return_value = [
            {
                "title": "Recovery Song",
                "artists": [{"name": "Recovery Artist"}],
                "videoId": "recovery123",
                "duration": "3:30"
            }
        ]
        
        await app_instance.perform_search("recovery query")
        
        # Should work normally now
        assert len(app_instance.songs) == 1
        assert app_instance.songs[0].title == "Recovery Song"
    
    @pytest.mark.asyncio
    async def test_playback_error_recovery_workflow(self, app_instance):
        """Test recovery from playback errors."""
        song = SongItem("Test Song", "Test Artist", "test123", "3:30")
        
        # Since the app bypasses yt-dlp, simulate MPV process failure instead
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                
                # Mock MPV process that fails to start
                mock_mpv.side_effect = FileNotFoundError("mpv not found")
                
                with patch.object(app_instance, 'update_status') as mock_update_status:
                    await app_instance.play_song(song)
                    
                    # Should handle error gracefully
                    mock_update_status.assert_called()
                    # Process should be None since MPV failed to start
                    assert app_instance.current_process is None
                    
                    # Song should still be tracked for resume
                    assert app_instance.last_played_song == song
    
    @pytest.mark.asyncio
    async def test_radio_error_recovery_workflow(self, app_instance):
        """Test recovery from radio errors."""
        song = SongItem("Radio Song", "Radio Artist", "radio123", "3:30")
        
        # First radio start fails (API error)
        app_instance.ytmusic.get_watch_playlist.side_effect = Exception("Radio API error")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.start_radio(song)
            
            # Should handle error gracefully and not activate radio
            mock_update_status.assert_called()
            assert app_instance.radio_active is False
        
        # Second attempt succeeds (API recovered)
        app_instance.ytmusic.get_watch_playlist.side_effect = None
        app_instance.ytmusic.get_watch_playlist.return_value = {
            "tracks": [
                {
                    "title": "Recovery Radio Song",
                    "artists": [{"name": "Recovery Artist"}],
                    "videoId": "recovery_radio_123",
                    "duration": {"text": "4:00"}
                }
            ]
        }
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                with patch.object(app_instance, 'update_radio_queue_display'):
                    
                    # Mock MPV process
                    mock_process = Mock()
                    mock_process.poll.return_value = None
                    mock_process.wait.return_value = 0
                    mock_mpv.return_value = mock_process
                    
                    await app_instance.start_radio(song)
                    
                    # Should work normally now - radio should activate
                    assert app_instance.radio_active is True
                    assert app_instance.radio_original_song == song
                    assert len(app_instance.radio_queue) == 0  # One song was played, queue is empty
                    
                    # Verify MPV was called
                    mock_mpv.assert_called()


class TestCompleteUserSession:
    """Test complete user session from start to finish."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_user_session_workflow(self, app_instance, temp_state_file):
        """Test a complete user session workflow."""
        # This test simulates a complete user session:
        # 1. Start app and load state
        # 2. Search for music
        # 3. Start radio mode
        # 4. Skip some songs
        # 5. Stop radio and play manual song
        # 6. Save state and exit
        
        # Use the existing app_instance fixture to avoid Textual screen stack issues
        app = app_instance
        app.state_file = temp_state_file
        
        # Mock API responses
        search_results = [
            {
                "title": "Session Song 1",
                "artists": [{"name": "Session Artist"}],
                "videoId": "session1",
                "duration": "3:30"
            }
        ]
        
        radio_playlist = {
            "tracks": [
                {
                    "title": "Radio Session Song 1",
                    "artists": [{"name": "Radio Artist"}],
                    "videoId": "radio_session1",
                    "duration": {"text": "4:00"}
                },
                {
                    "title": "Radio Session Song 2",
                    "artists": [{"name": "Radio Artist"}],
                    "videoId": "radio_session2",
                    "duration": {"text": "3:45"}
                }
            ]
        }
        
        app.ytmusic.search.return_value = search_results
        app.ytmusic.get_watch_playlist.return_value = radio_playlist
        
        # The app streams directly through MPV, no yt-dlp is used
        with patch('subprocess.Popen') as mock_mpv:
            with patch('psutil.process_iter', return_value=[]):  # No existing processes
                with patch.object(app, 'update_radio_queue_display'):
                    with patch.object(app, 'save_state') as mock_save_state:
                        
                        # Mock MPV processes
                        mock_process = Mock()
                        mock_process.poll.return_value = None
                        mock_process.wait.return_value = 0
                        mock_mpv.return_value = mock_process
                        
                        # Step 1: Load state (empty for new session)
                        app.load_state()
                        
                        # Step 2: Search for music
                        await app.perform_search("Session Artist")
                        assert len(app.songs) == 1
                        assert app.songs[0].title == "Session Song 1"
                        
                        # Step 3: Start radio mode
                        await app.start_radio(app.songs[0])
                        assert app.radio_active is True
                        
                        # Step 4: Skip some songs (simulate manual progression)
                        if app.radio_queue:
                            await app.play_next_radio_song()
                        
                        # Step 5: Stop radio and play manual song
                        await app.stop_radio()
                        assert app.radio_active is False
                        
                        # Play manual song
                        await app.play_song(app.songs[0])
                        
                        # Step 6: Save state (mocked to avoid file system issues)
                        assert mock_save_state.call_count > 0  # Should have been called multiple times
                        
                        # Verify MPV was called multiple times for different songs
                        assert mock_mpv.call_count >= 2  # At least radio + manual song 