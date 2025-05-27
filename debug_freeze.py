#!/usr/bin/env python3
"""
Debug script to identify what's causing the app freeze when using ctrl+s during radio playback.
"""

import asyncio
import threading
import time
import psutil
from unittest.mock import Mock

from ytmusic_tui import YTMusicTUI, SongItem

def debug_action_stop_all_music():
    """Debug the action_stop_all_music method to see where it might freeze."""
    
    print("🔍 Debugging action_stop_all_music...")
    
    app = YTMusicTUI()
    
    # Mock UI to avoid actual widget access
    mock_widget = Mock()
    app.query_one = Mock(return_value=mock_widget)
    app.update_status = Mock()
    
    # Set up radio state
    app.radio_active = True
    app.radio_queue = [SongItem("Test", "Artist", "test123")]
    app.current_process = None
    app.state_file = Mock()
    app.state_file.exists = Mock(return_value=False)
    
    print("✅ Set up test state")
    
    # Test each part of action_stop_all_music step by step
    print("🔍 Testing radio_progression_lock...")
    try:
        with app.radio_progression_lock:
            app.manual_progression_happening = False
            print("✅ Lock acquired and flag reset")
    except Exception as e:
        print(f"❌ Lock error: {e}")
        return False
    
    print("🔍 Testing process termination logic...")
    try:
        # Simulate killing processes
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'mpv':
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'youtube.com' in cmdline or '--no-video' in cmdline:
                        print(f"Would terminate process: {proc.info['pid']}")
                        killed_count += 1
                        # Don't actually terminate for testing
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        print(f"✅ Process enumeration completed, found {killed_count} mpv processes")
    except Exception as e:
        print(f"❌ Process enumeration error: {e}")
        return False
    
    print("🔍 Testing radio state preservation...")
    try:
        if app.radio_active:
            app.was_radio_active = True
            app.radio_state_when_stopped = {
                'queue': app.radio_queue.copy(),
                'current_song': app.radio_current_song,
                'original_song': app.radio_original_song,
                'queue_visible': app.radio_queue_visible
            }
            app.radio_active = False
            app.stop_radio_monitoring = True
            print("✅ Radio state preserved successfully")
    except Exception as e:
        print(f"❌ Radio state preservation error: {e}")
        return False
    
    print("✅ action_stop_all_music debugging completed - no obvious freeze points found")
    return True

async def debug_auto_play_next_radio_song():
    """Debug the auto_play_next_radio_song method."""
    
    print("\n🔍 Debugging auto_play_next_radio_song...")
    
    app = YTMusicTUI()
    
    # Mock dependencies
    app.query_one = Mock()
    app.update_status = Mock()
    app.save_state = Mock()
    app.call_from_thread = Mock()
    app.play_song = Mock()
    app.update_radio_queue_display = Mock()
    app.fetch_more_radio_songs = Mock()
    
    # Test with radio inactive (should return quickly)
    print("🔍 Testing with radio inactive...")
    app.radio_active = False
    app.radio_queue = []
    
    try:
        await app.auto_play_next_radio_song()
        print("✅ Handled inactive radio correctly")
    except Exception as e:
        print(f"❌ Error with inactive radio: {e}")
        return False
    
    # Test with radio active but stop_radio_monitoring=True
    print("🔍 Testing with radio monitoring stopped...")
    app.radio_active = True
    app.stop_radio_monitoring = True
    app.radio_queue = [SongItem("Test", "Artist", "test123")]
    
    try:
        await app.auto_play_next_radio_song()
        print("✅ Handled stopped monitoring correctly")
    except Exception as e:
        print(f"❌ Error with stopped monitoring: {e}")
        return False
    
    print("✅ auto_play_next_radio_song debugging completed")
    return True

def debug_threading_interactions():
    """Debug potential threading issues."""
    
    print("\n🔍 Debugging threading interactions...")
    
    app = YTMusicTUI()
    
    # Test lock contention
    print("🔍 Testing lock contention...")
    
    def thread1():
        try:
            with app.radio_progression_lock:
                time.sleep(0.1)
                print("Thread 1 completed")
        except Exception as e:
            print(f"Thread 1 error: {e}")
    
    def thread2():
        try:
            time.sleep(0.05)  # Start slightly after thread1
            with app.radio_progression_lock:
                print("Thread 2 completed")
        except Exception as e:
            print(f"Thread 2 error: {e}")
    
    try:
        t1 = threading.Thread(target=thread1)
        t2 = threading.Thread(target=thread2)
        
        start_time = time.time()
        t1.start()
        t2.start()
        
        t1.join(timeout=2)  # 2 second timeout
        t2.join(timeout=2)
        
        end_time = time.time()
        
        if end_time - start_time > 1.5:
            print(f"❌ Threading took too long: {end_time - start_time:.2f}s")
            return False
        else:
            print(f"✅ Threading completed in {end_time - start_time:.2f}s")
            return True
            
    except Exception as e:
        print(f"❌ Threading error: {e}")
        return False

async def main():
    """Run all diagnostic tests."""
    
    print("🔍 Starting freeze diagnosis...\n")
    
    # Test each component
    result1 = debug_action_stop_all_music()
    result2 = await debug_auto_play_next_radio_song()
    result3 = debug_threading_interactions()
    
    print(f"\n📊 Results:")
    print(f"action_stop_all_music: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"auto_play_next_radio_song: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"threading: {'✅ PASS' if result3 else '❌ FAIL'}")
    
    if all([result1, result2, result3]):
        print("\n🤔 All individual components work fine.")
        print("The freeze might be happening during UI operations or actual process termination.")
        print("Try running the actual app and see if the freeze happens consistently.")
    else:
        print("\n❌ Found issues that might be causing the freeze.")

if __name__ == "__main__":
    asyncio.run(main()) 