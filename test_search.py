#!/usr/bin/env python3
"""
Test script for YouTube Music search functionality.
This script tests the search feature without running the full TUI.
"""

from ytmusicapi import YTMusic
import sys

def test_search():
    """Test YouTube Music search functionality."""
    print("🔍 Testing YouTube Music search functionality...")
    
    try:
        # Initialize YTMusic
        ytmusic = YTMusic()
        print("✅ YouTube Music API initialized successfully!")
        
        # Test search with a simple query
        test_query = "The Beatles"
        print(f"🎵 Searching for: {test_query}")
        
        results = ytmusic.search(test_query, filter="songs", limit=5)
        
        if results:
            print(f"✅ Found {len(results)} results!")
            print("\n📋 Sample results:")
            
            for i, song in enumerate(results[:3], 1):
                title = song.get("title", "Unknown Title")
                artist = "Unknown Artist"
                if song.get("artists") and len(song["artists"]) > 0:
                    artist = song["artists"][0]["name"]
                duration = song.get("duration", "Unknown")
                video_id = song.get("videoId", "N/A")
                
                print(f"  {i}. {title} - {artist} ({duration}) [ID: {video_id}]")
            
            print("\n✅ Search functionality is working correctly!")
            return True
        else:
            print("❌ No results found for the test query.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing search functionality: {str(e)}")
        return False

def test_mpv():
    """Test if mpv is working correctly."""
    print("\n🎵 Testing mpv installation...")
    
    try:
        import subprocess
        result = subprocess.run(["mpv", "--version"], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ mpv is installed: {version_line}")
            return True
        else:
            print("❌ mpv is not working correctly.")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ mpv command timed out.")
        return False
    except FileNotFoundError:
        print("❌ mpv is not installed or not in PATH.")
        return False
    except Exception as e:
        print(f"❌ Error testing mpv: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 TUI YouTube Music Player - System Test")
    print("=" * 50)
    
    success = True
    
    # Test search functionality
    if not test_search():
        success = False
    
    # Test mpv
    if not test_mpv():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo start the application, run:")
        print("  python3 ytmusic_tui.py")
        print("  or")
        print("  ./run.sh")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 