"""
Unit tests for YTMusicTUI app state management.

These tests document the state management features:
- State persistence to file system
- Radio state tracking and management  
- Cleanup and initialization behavior
- Resume functionality
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import time

from ytmusic_tui import YTMusicTUI, SongItem


class TestAppInitialization:
    """Test app initialization and setup."""
    
    def test_app_initialization_default_state(self, mock_ytmusic, temp_state_file):
        """Test app initializes with correct default state."""
        with patch('ytmusic_tui.YTMusic', return_value=mock_ytmusic):
            app = YTMusicTUI()
            app.state_file = temp_state_file
            
            # Check initial state
            assert app.current_process is None
            assert app.songs == []
            assert app.last_played_song is None
            assert app.was_radio_active is False
            assert app.radio_state_when_stopped is None
            
            # Check radio state
            assert app.radio_active is False
            assert app.radio_queue == []
            assert app.radio_current_song is None
            assert app.radio_original_song is None
            assert app.radio_monitor_thread is None
            assert app.radio_queue_visible is False
            assert app.stop_radio_monitoring is False
            
            # Check thread safety
            assert app.radio_progression_lock is not None
            assert app.manual_progression_happening is False
    
    @patch('ytmusic_tui.YTMusicTUI._register_cleanup_handlers')
    def test_cleanup_handlers_registration(self, mock_register, mock_ytmusic, temp_state_file):
        """Test that cleanup handlers are registered on initialization."""
        # Reset the class flag to ensure registration is attempted
        YTMusicTUI._cleanup_registered = False
        
        with patch('ytmusic_tui.YTMusic', return_value=mock_ytmusic):
            YTMusicTUI()
            
            # Should register cleanup handlers
            mock_register.assert_called_once()
    
    def test_state_file_path_default(self, mock_ytmusic):
        """Test default state file path is set correctly."""
        with patch('ytmusic_tui.YTMusic', return_value=mock_ytmusic):
            app = YTMusicTUI()
            
            expected_path = Path.home() / ".ytmusic_tui_state.json"
            assert app.state_file == expected_path


class TestStatePersistence:
    """Test state persistence functionality."""
    
    def test_save_state_basic(self, app_instance, temp_state_file):
        """Test saving basic app state to file."""
        # Set up app state
        app_instance.last_played_song = SongItem("Test Song", "Test Artist", "test123", "3:30")
        app_instance.was_radio_active = True
        app_instance.radio_state_when_stopped = {"test": "data"}
        
        # Save state
        app_instance.save_state()
        
        # Verify file was created and contains correct data
        assert temp_state_file.exists()
        
        with open(temp_state_file, 'r') as f:
            state_data = json.load(f)
        
        assert "last_played_song" in state_data
        assert "was_radio_active" in state_data
        assert "radio_state_when_stopped" in state_data
        
        assert state_data["was_radio_active"] is True
        assert state_data["radio_state_when_stopped"] == {"test": "data"}
        
        # Check last played song structure
        song_data = state_data["last_played_song"]
        assert song_data["title"] == "Test Song"
        assert song_data["artist"] == "Test Artist"
        assert song_data["video_id"] == "test123"
        assert song_data["duration"] == "3:30"
    
    def test_save_state_no_last_song(self, app_instance, temp_state_file):
        """Test saving state when no last song is set."""
        app_instance.last_played_song = None
        app_instance.was_radio_active = False
        
        app_instance.save_state()
        
        with open(temp_state_file, 'r') as f:
            state_data = json.load(f)
        
        assert state_data["last_played_song"] is None
        assert state_data["was_radio_active"] is False
    
    def test_load_state_existing_file(self, app_instance, temp_state_file):
        """Test loading state from existing file."""
        # Create state file with test data
        state_data = {
            "last_played_song": {
                "title": "Loaded Song",
                "artist": "Loaded Artist", 
                "video_id": "loaded123",
                "duration": "4:20"
            },
            "was_radio_active": True,
            "radio_state_when_stopped": {"loaded": "state"},
            "timestamp": time.time()  # Add current timestamp
        }
        
        with open(temp_state_file, 'w') as f:
            json.dump(state_data, f)
        
        # Load state
        app_instance.load_state()
        
        # Verify state was loaded correctly
        assert app_instance.last_played_song is not None
        assert app_instance.last_played_song.title == "Loaded Song"
        assert app_instance.last_played_song.artist == "Loaded Artist"
        assert app_instance.last_played_song.video_id == "loaded123"
        assert app_instance.last_played_song.duration == "4:20"
        
        assert app_instance.was_radio_active is True
        assert app_instance.radio_state_when_stopped == {"loaded": "state"}
    
    def test_load_state_no_file(self, app_instance, temp_state_file):
        """Test loading state when file doesn't exist."""
        # Ensure file doesn't exist
        if temp_state_file.exists():
            temp_state_file.unlink()
        
        # Load state should not crash
        app_instance.load_state()
        
        # Should maintain default state
        assert app_instance.last_played_song is None
        assert app_instance.was_radio_active is False
        assert app_instance.radio_state_when_stopped is None
    
    def test_load_state_invalid_json(self, app_instance, temp_state_file):
        """Test loading state from corrupted JSON file."""
        # Write invalid JSON
        with open(temp_state_file, 'w') as f:
            f.write("invalid json content {")
        
        # Should handle gracefully
        app_instance.load_state()
        
        # Should maintain default state
        assert app_instance.last_played_song is None
        assert app_instance.was_radio_active is False
    
    def test_load_state_partial_data(self, app_instance, temp_state_file):
        """Test loading state with only partial data in file."""
        # Create file with only some fields
        state_data = {
            "last_played_song": {
                "title": "Partial Song",
                "artist": "Partial Artist",
                "video_id": "partial123"
                # Missing duration
            },
            "timestamp": time.time()  # Add current timestamp
            # Missing other fields
        }
        
        with open(temp_state_file, 'w') as f:
            json.dump(state_data, f)
        
        app_instance.load_state()
        
        # Should load what's available
        assert app_instance.last_played_song is not None
        assert app_instance.last_played_song.title == "Partial Song"
        assert app_instance.last_played_song.duration is None
        
        # Should default missing fields
        assert app_instance.was_radio_active is False
        assert app_instance.radio_state_when_stopped is None


class TestRadioState:
    """Test radio state management."""
    
    def test_radio_state_initialization(self, app_instance):
        """Test radio state is properly initialized."""
        assert app_instance.radio_active is False
        assert app_instance.radio_queue == []
        assert app_instance.radio_current_song is None
        assert app_instance.radio_original_song is None
        assert app_instance.radio_monitor_thread is None
        assert app_instance.radio_queue_visible is False
        assert app_instance.stop_radio_monitoring is False
    
    def test_radio_activation(self, app_instance):
        """Test radio state when activated."""
        # Simulate radio activation
        app_instance.radio_active = True
        app_instance.radio_original_song = SongItem("Original", "Artist", "orig123")
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr123")
        app_instance.radio_queue = [
            SongItem("Queue1", "Artist1", "q1"),
            SongItem("Queue2", "Artist2", "q2")
        ]
        
        assert app_instance.radio_active is True
        assert app_instance.radio_original_song.title == "Original"
        assert app_instance.radio_current_song.title == "Current"
        assert len(app_instance.radio_queue) == 2
    
    def test_radio_deactivation(self, app_instance):
        """Test radio state when deactivated."""
        # Set up active radio state
        app_instance.radio_active = True
        app_instance.radio_queue = [SongItem("Test", "Artist", "test123")]
        app_instance.radio_current_song = SongItem("Current", "Artist", "curr123")
        
        # Simulate deactivation
        app_instance.radio_active = False
        app_instance.radio_queue = []
        app_instance.radio_current_song = None
        app_instance.radio_original_song = None
        
        assert app_instance.radio_active is False
        assert app_instance.radio_queue == []
        assert app_instance.radio_current_song is None
        assert app_instance.radio_original_song is None
    
    def test_radio_queue_visibility_toggle(self, app_instance):
        """Test radio queue visibility toggling."""
        assert app_instance.radio_queue_visible is False
        
        # Toggle visibility
        app_instance.radio_queue_visible = True
        assert app_instance.radio_queue_visible is True
        
        # Toggle back
        app_instance.radio_queue_visible = False
        assert app_instance.radio_queue_visible is False
    
    def test_radio_monitoring_flags(self, app_instance):
        """Test radio monitoring control flags."""
        assert app_instance.stop_radio_monitoring is False
        assert app_instance.manual_progression_happening is False
        
        # Test setting monitoring flags
        app_instance.stop_radio_monitoring = True
        app_instance.manual_progression_happening = True
        
        assert app_instance.stop_radio_monitoring is True
        assert app_instance.manual_progression_happening is True


class TestProcessManagement:
    """Test process management and cleanup."""
    
    def test_active_processes_tracking(self, app_instance):
        """Test that active processes are tracked at class level."""
        # Access class variable
        assert hasattr(YTMusicTUI, '_active_processes')
        assert isinstance(YTMusicTUI._active_processes, list)
        
        # Should start empty
        assert len(YTMusicTUI._active_processes) == 0
    
    def test_cleanup_registered_flag(self, app_instance):
        """Test cleanup registration tracking."""
        assert hasattr(YTMusicTUI, '_cleanup_registered')
        assert isinstance(YTMusicTUI._cleanup_registered, bool)
    
    @patch('subprocess.Popen')
    def test_process_tracking(self, mock_popen, app_instance):
        """Test that new processes are added to tracking list."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        # Simulate adding process to tracking
        YTMusicTUI._active_processes.append(mock_process)
        
        assert len(YTMusicTUI._active_processes) == 1
        assert YTMusicTUI._active_processes[0] == mock_process
    
    @patch('psutil.process_iter')
    def test_cleanup_all_processes(self, mock_process_iter, app_instance):
        """Test cleanup of all tracked processes."""
        # Create mock processes
        mock_process1 = Mock()
        mock_process1.poll.return_value = None  # Still running
        mock_process1.terminate.return_value = None
        mock_process1.wait.return_value = 0
        
        mock_process2 = Mock()
        mock_process2.poll.return_value = 1  # Already terminated
        
        # Add to tracking
        YTMusicTUI._active_processes = [mock_process1, mock_process2]
        
        # Mock psutil process
        mock_psutil_process = Mock()
        mock_psutil_process.info = {
            'pid': 12345,
            'name': 'mpv',
            'cmdline': ['mpv', '--no-video', 'https://youtube.com/test']
        }
        mock_process_iter.return_value = [mock_psutil_process]
        
        # Run cleanup
        YTMusicTUI._cleanup_all_processes()
        
        # Verify cleanup actions
        mock_process1.terminate.assert_called_once()
        mock_process1.wait.assert_called_once()
        
        # Process list should be cleared
        assert len(YTMusicTUI._active_processes) == 0
    
    def test_current_process_tracking(self, app_instance):
        """Test current process tracking on app instance."""
        assert app_instance.current_process is None
        
        # Simulate setting current process
        mock_process = Mock()
        app_instance.current_process = mock_process
        
        assert app_instance.current_process == mock_process 