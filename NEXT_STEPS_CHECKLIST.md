# E2E Test Fixing Checklist - Next Steps

## Quick Start Commands

```bash
# Check current status
pytest tests/e2e/ --tb=no -v

# Work on specific failing test with full output
pytest tests/e2e/test_full_workflow.py::TestSearchAndPlayWorkflow::test_search_select_play_workflow -v -s

# Run all E2E tests with short output for progress tracking  
pytest tests/e2e/ --tb=line
```

## Priority Order for Fixing (8 remaining failures)

### 🔥 High Priority (Core Functionality) - Fix These First

#### 1. `test_search_select_play_workflow`
**Issue**: `AssertionError: Expected 'run' to have been called once. Called 0 times.`
**Root Cause**: Test expects `subprocess.run` for yt-dlp, but app uses direct MPV calls
**Fix Strategy**:
- Remove `mock_yt_dlp` (subprocess.run) assertions
- Keep only `mock_mpv` (subprocess.Popen) assertions  
- Verify MPV called with YouTube URL directly

#### 2. `test_resume_playback_workflow`  
**Issue**: Same as #1 - expecting yt-dlp call
**Fix Strategy**: Same as #1 - focus on MPV mocking only

#### 3. `test_playback_error_recovery_workflow`
**Issue**: `assert <Popen: returncode: None args: ['mpv'...> is None`
**Root Cause**: Test expects process to be None after error, but it's set
**Fix Strategy**: Check actual app behavior - does it set process on successful recovery?

### 🟡 Medium Priority (Radio Functionality)

#### 4. `test_start_radio_workflow`
**Issue**: `assert False is True` (radio activation)
**Fix Strategy**:
- Check if radio_active assertion is correct
- Verify UI component mocking is complete
- Test may need `update_radio_queue_display` mock

#### 5. `test_radio_manual_next_workflow`
**Issue**: `assert 'Current Song' == 'Next Song'`
**Fix Strategy**:
- Check radio queue progression logic
- Verify `radio_current_song` update in `play_next_radio_song`

#### 6. `test_stop_radio_workflow`
**Issue**: `Expected 'update_radio_queue_display' to have been called`
**Fix Strategy**: Add missing mock for `update_radio_queue_display` method

#### 7. `test_radio_error_recovery_workflow`
**Issue**: `assert False is True` (radio state)
**Fix Strategy**: Check radio activation behavior after API recovery

### 🔴 Low Priority (Complex Integration)

#### 8. `test_full_user_session_workflow`
**Issue**: `textual.app.ScreenStackError: No screens on stack`
**Fix Strategy**: Most complex - requires extensive Textual app mocking
- Consider simplifying test scope
- May need to mock entire Textual application lifecycle

## Key Patterns to Apply

### For yt-dlp Issues (#1, #2)
```python
# REMOVE this pattern:
with patch('subprocess.run') as mock_yt_dlp:
    mock_yt_dlp.assert_called_once()

# KEEP this pattern:
with patch('subprocess.Popen') as mock_mpv:
    mock_mpv.assert_called_once()
    # Verify YouTube URL in call args
```

### For Radio Issues (#4, #5, #6, #7)  
```python
# Add comprehensive UI mocking:
def mock_query_one(selector, widget_type=None):
    if selector == "#radio-queue":
        return mock_radio_queue_widget
    elif selector == ".radio-panel":
        return mock_radio_panel
    return Mock()

# Mock all radio-related methods:
with patch.object(app_instance, 'update_radio_queue_display') as mock_update:
    # Test code here
    mock_update.assert_called()
```

## Testing Strategy

1. **Fix one test at a time** - don't batch fixes
2. **Run individual test** after each fix to verify
3. **Check actual app behavior** if assertions fail - tests might be wrong
4. **Use patterns from working tests** (7 are already passing)
5. **Simplify complex tests** if needed - E2E tests should focus on happy paths

## Reference Working Test Patterns

Look at these passing tests for correct patterns:
- `test_search_no_results_workflow` - Good error handling pattern
- `test_keyboard_navigation_workflow` - Good UI mocking pattern
- `test_api_error_recovery_workflow` - Good error simulation pattern

## Expected Completion Time

- High Priority (3 tests): ~30-45 minutes
- Medium Priority (4 tests): ~60-90 minutes  
- Low Priority (1 test): ~30-60 minutes
- **Total**: ~2-3 hours for complete E2E test suite fix

## Success Criteria

```bash
# Target result:
pytest tests/e2e/ --tb=no -q
# Should show: 15 passed, 0 failed
``` 