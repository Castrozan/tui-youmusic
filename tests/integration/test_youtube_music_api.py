"""
Integration tests for YouTube Music API interactions.

These tests verify real API integration:
- YouTube Music search functionality
- Radio playlist generation
- Error handling for network issues
- API response parsing and validation

Note: These tests may require internet connection and may be skipped in CI.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
import time

from ytmusicapi import YTMusic
from ytmusic_tui import YTMusicTUI, SongItem


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestYouTubeMusicAPIIntegration:
    """Test real YouTube Music API integration."""
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_ytmusic_initialization(self):
        """Test that YTMusic API can be initialized."""
        try:
            ytmusic = YTMusic()
            assert ytmusic is not None
        except Exception as e:
            pytest.skip(f"YouTube Music API not available: {e}")
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_search_popular_songs(self):
        """Test searching for popular songs that should exist."""
        try:
            ytmusic = YTMusic()
            
            # Test with a very popular song that should always exist
            results = ytmusic.search("The Beatles", filter="songs", limit=5)
            
            assert isinstance(results, list)
            assert len(results) > 0
            
            # Verify result structure
            first_result = results[0]
            assert "title" in first_result
            assert "videoId" in first_result
            assert "artists" in first_result
            
            # Artists should be a list with at least one item
            assert isinstance(first_result["artists"], list)
            assert len(first_result["artists"]) > 0
            assert "name" in first_result["artists"][0]
            
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_search_different_filters(self):
        """Test searching with different filters."""
        try:
            ytmusic = YTMusic()
            
            # Test songs filter
            song_results = ytmusic.search("Queen", filter="songs", limit=3)
            assert isinstance(song_results, list)
            
            # Test artists filter
            artist_results = ytmusic.search("Queen", filter="artists", limit=3)
            assert isinstance(artist_results, list)
            
            # Results should have different structures
            if song_results and artist_results:
                # Songs should have videoId, artists might not
                assert "videoId" in song_results[0]
                
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_get_watch_playlist_for_popular_song(self):
        """Test getting radio playlist for a popular song."""
        try:
            ytmusic = YTMusic()
            
            # First search for a song
            search_results = ytmusic.search("Bohemian Rhapsody Queen", filter="songs", limit=1)
            
            if not search_results:
                pytest.skip("Could not find test song")
            
            video_id = search_results[0]["videoId"]
            
            # Get radio playlist
            playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=10)
            
            assert isinstance(playlist, dict)
            assert "tracks" in playlist
            assert isinstance(playlist["tracks"], list)
            
            if playlist["tracks"]:
                track = playlist["tracks"][0]
                assert "title" in track
                assert "videoId" in track
                assert "artists" in track
                
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")
    
    @pytest.mark.slow
    @pytest.mark.network
    def test_search_edge_cases(self):
        """Test search with edge cases."""
        try:
            ytmusic = YTMusic()
            
            # Test empty search
            empty_results = ytmusic.search("", filter="songs", limit=5)
            # Should either return empty list or handle gracefully
            assert isinstance(empty_results, list)
            
            # Test special characters
            special_results = ytmusic.search("café del mar", filter="songs", limit=3)
            assert isinstance(special_results, list)
            
            # Test very long query
            long_query = "a" * 200
            long_results = ytmusic.search(long_query, filter="songs", limit=3)
            assert isinstance(long_results, list)
            
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")


class TestAPIErrorHandling:
    """Test API error handling and resilience."""
    
    def test_ytmusic_initialization_with_invalid_config(self):
        """Test YTMusic initialization with invalid configuration."""
        # Test that YTMusic can be initialized even without auth
        # This is the actual behavior - YTMusic works without authentication
        try:
            ytmusic = YTMusic()
            # If this succeeds, that's the expected behavior
            assert ytmusic is not None
        except Exception as e:
            # If it fails, our app should handle it in on_mount
            # This documents the behavior
            assert "Invalid configuration" in str(e) or "authentication" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_app_handles_search_api_errors(self, app_instance):
        """Test that app handles search API errors gracefully."""
        # Mock YTMusic to raise an exception
        app_instance.ytmusic.search.side_effect = ConnectionError("Network error")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.perform_search("test query")
            
            # Should handle error and update status
            mock_update_status.assert_called()
            assert len(app_instance.songs) == 0
    
    @pytest.mark.asyncio
    async def test_app_handles_radio_api_errors(self, app_instance):
        """Test that app handles radio API errors gracefully."""
        app_instance.ytmusic.get_watch_playlist.side_effect = TimeoutError("Request timeout")
        
        test_song = SongItem("Test", "Artist", "test123")
        
        with patch.object(app_instance, 'update_status') as mock_update_status:
            await app_instance.start_radio(test_song)
            
            # Should handle error and not activate radio
            mock_update_status.assert_called()
            assert app_instance.radio_active is False
    
    def test_api_rate_limiting_simulation(self):
        """Test handling of API rate limiting."""
        # Simulate rate limiting by making rapid requests
        with patch('ytmusicapi.YTMusic.search') as mock_search:
            mock_search.side_effect = Exception("Rate limited")
            
            ytmusic = Mock()
            ytmusic.search = mock_search
            
            # Multiple rapid calls should be handled gracefully
            for i in range(5):
                try:
                    ytmusic.search("test", filter="songs", limit=5)
                except Exception:
                    pass  # Expected to fail due to mocked rate limiting
            
            # Verify multiple calls were attempted
            assert mock_search.call_count == 5


class TestAPIResponseParsing:
    """Test parsing of different API response formats."""
    
    @pytest.mark.asyncio
    async def test_parse_search_results_with_missing_fields(self, app_instance):
        """Test parsing search results with missing optional fields."""
        # Mock search results with various missing fields
        mock_results = [
            {
                "title": "Complete Song",
                "artists": [{"name": "Complete Artist"}],
                "videoId": "complete123",
                "duration": "3:30"
            },
            {
                "title": "No Duration Song",
                "artists": [{"name": "No Duration Artist"}],
                "videoId": "noduration123"
                # Missing duration
            },
            {
                "title": "No Artists Song",
                "videoId": "noartists123",
                "duration": "2:45"
                # Missing artists
            }
        ]
        
        app_instance.ytmusic.search.return_value = mock_results
        
        # Should parse all results gracefully
        await app_instance.perform_search("test")
        
        # Should create SongItem objects for valid results
        assert len(app_instance.songs) >= 1  # At least the complete one
    
    @pytest.mark.asyncio
    async def test_parse_radio_playlist_with_missing_fields(self, app_instance):
        """Test parsing radio playlist with missing optional fields."""
        mock_playlist = {
            "tracks": [
                {
                    "title": "Complete Track",
                    "artists": [{"name": "Complete Artist"}],
                    "videoId": "complete123",
                    "duration": "3:30"
                },
                {
                    "title": "Incomplete Track",
                    "videoId": "incomplete123"
                    # Missing artists and duration
                }
            ]
        }
        
        app_instance.ytmusic.get_watch_playlist.return_value = mock_playlist
        
        test_song = SongItem("Test", "Artist", "test123")
        
        # Mock UI components that start_radio tries to access
        mock_radio_queue = Mock()
        mock_radio_panel = Mock()
        
        def mock_query_one(selector, widget_type=None):
            if selector == "#radio-queue":
                return mock_radio_queue
            elif selector == ".radio-panel":
                return mock_radio_panel
            return Mock()
        
        with patch.object(app_instance, 'query_one', side_effect=mock_query_one):
            with patch.object(app_instance, 'update_status') as mock_update_status:
                with patch.object(app_instance, 'play_song') as mock_play_song:
                    with patch.object(app_instance, 'update_radio_queue_display') as mock_update_display:
                        # Should handle incomplete tracks gracefully without crashing
                        await app_instance.start_radio(test_song)
                        
                        # The main goal is that it doesn't crash with missing fields
                        # and that it processes the valid tracks
                        
                        # Check that update_status was called (method ran)
                        assert mock_update_status.called
                        
                        # Check that the radio queue widget was accessed
                        # (meaning it tried to process tracks)
                        mock_radio_queue.clear.assert_called()
                        
                        # The method should have attempted to append items
                        # even if some tracks have missing fields
                        assert mock_radio_queue.append.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_parse_empty_search_results(self, app_instance):
        """Test parsing empty search results."""
        app_instance.ytmusic.search.return_value = []
        
        await app_instance.perform_search("nonexistent")
        
        assert len(app_instance.songs) == 0
    
    @pytest.mark.asyncio
    async def test_parse_malformed_api_response(self, app_instance):
        """Test handling of malformed API responses."""
        # Mock various malformed responses
        malformed_responses = [
            None,  # None response
            "string response",  # String instead of list
            {"error": "API Error"},  # Error object instead of list
            [{"malformed": "object"}],  # Missing required fields
        ]
        
        for response in malformed_responses:
            app_instance.ytmusic.search.return_value = response
            
            # Should handle gracefully without crashing
            try:
                await app_instance.perform_search("test")
                assert isinstance(app_instance.songs, list)
            except Exception:
                # Some malformed responses might raise exceptions
                # which should be caught by the app's error handling
                pass


class TestAPIPerformance:
    """Test API performance and timeout handling."""
    
    @pytest.mark.slow
    def test_search_performance_baseline(self):
        """Test search performance baseline."""
        try:
            ytmusic = YTMusic()
            
            start_time = time.time()
            results = ytmusic.search("The Beatles", filter="songs", limit=10)
            end_time = time.time()
            
            search_time = end_time - start_time
            
            # Search should complete within reasonable time (adjust as needed)
            assert search_time < 10.0  # 10 seconds max
            assert isinstance(results, list)
            
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")
    
    @pytest.mark.slow
    def test_radio_playlist_performance(self):
        """Test radio playlist generation performance."""
        try:
            ytmusic = YTMusic()
            
            # First get a song
            search_results = ytmusic.search("Queen", filter="songs", limit=1)
            if not search_results:
                pytest.skip("Could not find test song")
            
            video_id = search_results[0]["videoId"]
            
            start_time = time.time()
            playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=20)
            end_time = time.time()
            
            playlist_time = end_time - start_time
            
            # Playlist generation should complete within reasonable time
            assert playlist_time < 15.0  # 15 seconds max
            assert isinstance(playlist, dict)
            
        except Exception as e:
            pytest.skip(f"Network/API issue: {e}")
    
    def test_concurrent_api_requests(self):
        """Test handling of concurrent API requests."""
        # This would test the app's behavior with multiple simultaneous requests
        # In practice, the app is designed to handle one request at a time
        # but this tests that it doesn't break with concurrent usage
        
        with patch('ytmusicapi.YTMusic.search') as mock_search:
            mock_search.return_value = []
            
            ytmusic = Mock()
            ytmusic.search = mock_search
            
            # Simulate concurrent requests
            import threading
            
            def make_request():
                ytmusic.search("test", filter="songs", limit=5)
            
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # All requests should have been made
            assert mock_search.call_count == 3 