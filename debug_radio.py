#!/usr/bin/env python3
"""Debug script to test radio functionality."""

import asyncio
from unittest.mock import Mock, patch
from ytmusic_tui import YTMusicTUI, SongItem

async def debug_radio():
    """Debug radio functionality."""
    print("🔍 Debugging radio functionality...")
    
    # Create app instance
    with patch('ytmusic_tui.YTMusic') as mock_ytmusic_class:
        mock_ytmusic = Mock()
        mock_ytmusic_class.return_value = mock_ytmusic
        
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
        
        mock_ytmusic.get_watch_playlist.return_value = radio_playlist
        
        app = YTMusicTUI()
        app.ytmusic = mock_ytmusic
        
        # Mock UI components
        mock_radio_queue_widget = Mock()
        mock_radio_panel = Mock()
        
        def mock_query_one(selector, widget_type=None):
            if selector == "#radio-queue":
                return mock_radio_queue_widget
            elif selector == ".radio-panel":
                return mock_radio_panel
            return Mock()
        
        app.query_one = Mock(side_effect=mock_query_one)
        
        # Test song
        test_song = SongItem("Test Song", "Test Artist", "test123", "3:30")
        
        print(f"📋 Mock playlist: {radio_playlist}")
        print(f"📋 Mock return value: {mock_ytmusic.get_watch_playlist.return_value}")
        
        # Mock play_song and update methods to avoid UI issues
        app.play_song = Mock()
        app.update_radio_queue_display = Mock()
        
        try:
            # Test start_radio
            await app.start_radio(test_song)
            print(f"✅ Radio started successfully!")
            print(f"📻 Radio active: {app.radio_active}")
            print(f"📻 Radio queue length: {len(app.radio_queue)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_radio()) 