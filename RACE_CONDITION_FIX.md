# Race Condition Fix: Ctrl+S During Radio Playback

## Problem Identified

The app was breaking when users pressed `Ctrl+S` (stop all music) while radio was playing. This was due to a race condition between:

1. **Background thread**: The `play_with_mpv()` function runs in a background thread and tries to auto-progress to the next radio song when the current song finishes
2. **Main thread**: When user presses `Ctrl+S`, the `action_stop_all_music()` function completely destroys the radio state
3. **Race condition**: If the background thread tries to access radio state after it's been destroyed, the app crashes

## Root Cause

The original `action_stop_all_music()` method was too aggressive - it **completely destroyed** all radio state:
- Set `radio_active = False`
- Cleared `radio_queue = []`
- Set `radio_current_song = None`
- Cleared UI widgets
- Deleted saved state file

When background threads tried to access this cleared state, they would encounter `None` values or empty lists, causing crashes in methods like:
- `auto_play_next_radio_song()`
- `fetch_more_radio_songs()`
- `update_radio_queue_display()`

## Solution Implemented

### 1. Preserve Radio State Instead of Destroying It

Modified `action_stop_all_music()` to **pause** radio instead of destroying it:
- Save current radio state to `radio_state_when_stopped`
- Set `was_radio_active = True` for later resume
- Only set `radio_active = False` and `stop_radio_monitoring = True` (pause, don't destroy)
- Keep radio queue and current song intact

### 2. Enhanced Background Thread Robustness

Added multiple safety checks in `auto_play_next_radio_song()`:
- Check `stop_radio_monitoring` flag before proceeding
- Double-check radio state hasn't changed during execution
- Add comprehensive error handling to prevent crashes
- Graceful early returns when radio is paused

### 3. Improved Other Radio Functions

Enhanced `fetch_more_radio_songs()` and `update_radio_queue_display()`:
- Check if radio is still active before accessing state
- Handle UI widget access errors gracefully
- Skip operations when radio is in transitional states
- Better error messaging

### 4. Better Resume Functionality

Improved `action_resume_playback()`:
- Properly restore all radio state when resuming
- Clear pause flags after successful resume
- Handle resume errors gracefully
- Maintain UI consistency

## Key Benefits

1. **No More Crashes**: Background threads can't crash when accessing cleared state
2. **Better UX**: Users can resume radio exactly where they left off
3. **Intuitive Behavior**: "Stop music" doesn't permanently destroy radio queue
4. **Thread Safety**: Improved coordination between main and background threads
5. **Graceful Error Handling**: Edge cases are handled without crashing

## Files Modified

- `ytmusic_tui.py`: Core implementation changes
  - `action_stop_all_music()`: Now preserves radio state
  - `auto_play_next_radio_song()`: Added robustness checks
  - `fetch_more_radio_songs()`: Enhanced error handling  
  - `update_radio_queue_display()`: Better state checking
  - `action_resume_playback()`: Improved resume logic

## Testing

Created comprehensive tests that simulate the race condition scenario:
- ✅ Background auto-progression after Ctrl+S doesn't crash
- ✅ Radio state is properly preserved and restored
- ✅ Concurrent operations are handled safely
- ✅ All radio functions handle paused state gracefully

The fix has been verified to work correctly and should prevent the app from breaking when using `Ctrl+S` during radio playback. 