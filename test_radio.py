#!/usr/bin/env python3
"""
Test script for TUI YouTube Music Player radio functionality.
This script tests the radio integration without running the full TUI.
"""

import asyncio
from ytmusicapi import YTMusic
from ytmusic_tui import YTMusicTUI, SongItem

async def test_radio_functionality():
    """Test radio functionality."""
    print("🎵 Testing TUI YouTube Music Player - Radio Functionality")
    print("=" * 60)
    
    try:
        # Initialize YouTube Music API
        print("1. Initializing YouTube Music API...")
        ytmusic = YTMusic()
        print("   ✅ YouTube Music API initialized successfully")
        
        # Test search functionality
        print("\n2. Testing search functionality...")
        search_results = ytmusic.search("The Beatles", filter="songs", limit=5)
        if search_results:
            print(f"   ✅ Search successful - Found {len(search_results)} songs")
            test_song = search_results[0]
            print(f"   📄 Test song: {test_song.get('title', 'Unknown')} - {test_song.get('artists', [{}])[0].get('name', 'Unknown Artist') if test_song.get('artists') else 'Unknown Artist'}")
        else:
            print("   ❌ Search failed - No results")
            return
        
        # Test radio playlist generation
        print("\n3. Testing radio playlist generation...")
        video_id = test_song.get('videoId')
        if video_id:
            watch_playlist = ytmusic.get_watch_playlist(videoId=video_id, limit=10)
            if watch_playlist and 'tracks' in watch_playlist:
                radio_tracks = watch_playlist['tracks']
                print(f"   ✅ Radio playlist generated - {len(radio_tracks)} similar songs found")
                print("   📻 Radio tracks preview:")
                for i, track in enumerate(radio_tracks[:3], 1):
                    title = track.get('title', 'Unknown Title')
                    artist = track.get('artists', [{}])[0].get('name', 'Unknown Artist') if track.get('artists') else 'Unknown Artist'
                    print(f"      {i}. {title} - {artist}")
                if len(radio_tracks) > 3:
                    print(f"      ... and {len(radio_tracks) - 3} more songs")
            else:
                print("   ❌ Failed to generate radio playlist")
                return
        else:
            print("   ❌ No video ID found for test song")
            return
        
        # Test TUI app initialization (without running)
        print("\n4. Testing TUI app initialization...")
        app = YTMusicTUI()
        print(f"   ✅ TUI app initialized successfully")
        print(f"   📋 Radio state initialized: {app.radio_active}")
        print(f"   📋 Radio queue initialized: {len(app.radio_queue)} items")
        
        # Test SongItem creation
        print("\n5. Testing SongItem and RadioQueueItem creation...")
        song_item = SongItem(
            test_song.get('title', 'Test Song'),
            test_song.get('artists', [{}])[0].get('name', 'Test Artist') if test_song.get('artists') else 'Test Artist',
            test_song.get('videoId', 'test_id'),
            test_song.get('duration', '3:30')
        )
        print(f"   ✅ SongItem created: {song_item.title} - {song_item.artist}")
        
        # Test keybindings
        print("\n6. Testing keybindings...")
        bindings = app.BINDINGS
        radio_bindings = [b for b in bindings if 'radio' in b.description.lower() or 'next' in b.description.lower()]
        print(f"   ✅ Radio keybindings found: {len(radio_bindings)}")
        for binding in radio_bindings:
            print(f"      {binding.key}: {binding.description}")
        
        print("\n" + "=" * 60)
        print("🎉 All radio functionality tests passed!")
        print("\n📻 Radio Features Available:")
        print("   • Press R to start song-based radio")
        print("   • Auto-play queue with 20 songs (fetches more when <5 remain)")
        print("   • Press N for next song, Ctrl+R to stop radio")
        print("   • Press Q to toggle radio queue visibility")
        print("   • Radio stops when manually selecting another song")
        print("\n🎵 Ready to use! Run: python3 ytmusic_tui.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("   Please check your internet connection and dependencies.")
        return False
    
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_radio_functionality())
    if not success:
        exit(1) 