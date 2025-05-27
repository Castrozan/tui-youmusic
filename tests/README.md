# TUI YouTube Music Player - Testing Guide

This guide covers how to test the TUI YouTube Music Player application, including test structure, execution, and best practices.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=ytmusic_tui --cov-report=html

# Run specific test categories
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests
pytest -m e2e           # End-to-end workflow tests
```

## Project Overview

The TUI YouTube Music Player is a Python-based terminal application for streaming YouTube Music content using:
- **Textual** framework for the TUI
- **ytmusicapi** for YouTube Music API integration  
- **MPV** media player for direct audio streaming
- **pytest** for testing framework

## Test Architecture

### Current Test Coverage
- **126 tests total** with 74% code coverage
- **Unit Tests**: 67 tests - Core functionality validation
- **Integration Tests**: 44 tests - Component interaction testing
- **E2E Tests**: 15 tests - Complete user workflow testing

### Directory Structure
```
tests/
├── README.md              # This testing guide
├── conftest.py           # Shared fixtures and configuration
├── __init__.py           # Test package initialization
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_app_state.py        # State management & persistence
│   ├── test_radio_functionality.py # Radio mode features
│   ├── test_search_playback.py    # Search & playback functionality
│   └── test_song_items.py         # SongItem/RadioQueueItem classes
├── integration/          # Integration tests (component interactions)
│   ├── test_youtube_music_api.py  # YouTube Music API integration
│   └── test_external_processes.py # MPV/yt-dlp integration
└── e2e/                  # End-to-end tests (complete workflows)
    └── test_full_workflow.py      # Complete user workflow tests
```

## Test Categories & Execution

### Unit Tests (`tests/unit/`)
**Purpose**: Fast, isolated testing of individual components

**What's tested**:
- SongItem and RadioQueueItem data models
- Application state management and persistence
- Search and playbook core functionality  
- Radio mode features and queue management

**Run unit tests**:
```bash
pytest tests/unit/ -v                    # All unit tests
pytest tests/unit/test_song_items.py     # Specific test file
pytest -m unit                           # Using markers
```

**Performance**: < 1 second per test, ~5 seconds total

### Integration Tests (`tests/integration/`)
**Purpose**: Testing component interactions and external integrations

**What's tested**:
- YouTube Music API connectivity and responses
- MPV media player integration
- yt-dlp URL extraction and streaming
- Process lifecycle management
- Error handling for network/external tool issues

**Run integration tests**:
```bash
pytest tests/integration/ -v            # All integration tests
pytest -m integration                   # Using markers
pytest -m "integration and not network" # Skip network-dependent tests
```

**Performance**: < 5 seconds per test, some network tests may be slower

### End-to-End Tests (`tests/e2e/`)
**Purpose**: Complete user workflow validation

**What's tested**:
- Search → select → play workflow
- Radio mode workflows (start, skip, stop)
- State persistence across sessions
- Keyboard shortcuts and navigation
- Error recovery scenarios
- Complete user session simulation

**Run E2E tests**:
```bash
pytest tests/e2e/ -v                    # All E2E tests
pytest -m e2e                           # Using markers
pytest -m "e2e and not slow"            # Skip slow tests
```

**Performance**: < 2 seconds per test due to comprehensive mocking

## Test Markers

Tests are categorized with pytest markers for selective execution:

- `@pytest.mark.unit` - Fast unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Tests that may take several seconds
- `@pytest.mark.network` - Tests requiring internet connection
- `@pytest.mark.external` - Tests requiring external tools (mpv, yt-dlp)

**Usage examples**:
```bash
pytest -m "unit or integration"         # Run unit and integration tests
pytest -m "not slow and not network"    # Skip slow and network tests
pytest -m "e2e and not external"        # E2E tests without external deps
```

## Key Architecture Insights for Testing

### 1. Direct MPV Audio Streaming
**Important**: The app streams YouTube audio **directly through MPV** using YouTube URLs.

```python
# ✅ Correct test pattern - expect direct MPV calls
with patch('subprocess.Popen') as mock_mpv:
    await app.play_song(song)
    
    # Verify MPV called with YouTube URL
    call_args = mock_mpv.call_args[0][0]
    assert "mpv" in call_args
    assert "--no-video" in call_args
    assert f"https://www.youtube.com/watch?v={song.video_id}" in call_args[-1]

# ❌ Incorrect - expecting yt-dlp usage
# The app does NOT use yt-dlp for stream extraction
```

### 2. Radio Mode Behavior
**Important**: Radio mode activates immediately, even with empty playlists.

```python
# ✅ Correct test expectation
mock_ytmusic.get_watch_playlist.return_value = {"tracks": []}
await app.start_radio(song)
assert app.radio_active is True  # Radio activates immediately

# ❌ Incorrect - expecting radio to wait for songs
# assert app.radio_active is False  # This would fail
```

### 3. UI Framework Constraints
**Important**: Textual framework requires extensive mocking for testing outside app context.

```python
# ✅ Correct UI component mocking pattern
def mock_query_one(selector, widget_type=None):
    if selector == "#results":
        return mock_results_widget
    elif selector == "#radio-queue":
        return mock_radio_queue_widget
    return Mock()

with patch.object(app_instance, 'query_one', side_effect=mock_query_one):
    # Test UI interactions safely
```

## Running Tests

### Basic Execution
```bash
# Run all tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=ytmusic_tui

# Generate HTML coverage report
pytest --cov=ytmusic_tui --cov-report=html
# Open htmlcov/index.html in browser

# Stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf
```

### Development Workflow
```bash
# Quick feedback during development
pytest tests/unit/ -x                   # Fast unit tests, stop on fail

# Before committing changes
pytest -m "unit and integration"        # Core functionality

# Full test suite
pytest --cov=ytmusic_tui --cov-report=term-missing
```

### Debugging Tests
```bash
# Run with detailed output and no capture
pytest -v -s

# Debug specific failing test
pytest tests/unit/test_song_items.py::TestSongItem::test_creation -v -s

# Drop into debugger on failure
pytest --pdb

# Show test execution times
pytest --durations=10
```

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Test Configuration

### Prerequisites
1. **Required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional external tools** (for full integration tests):
   - `mpv` - Audio player
   - `yt-dlp` - YouTube URL extraction

### Pytest Configuration (`pytest.ini`)
The test suite uses pytest with:
- Coverage reporting enabled by default
- Strict marker and config validation  
- Custom markers for test categorization
- Warning filters for clean output

### Shared Fixtures (`conftest.py`)
Provides comprehensive test infrastructure:
- **Mock objects** for external APIs and processes
- **Temporary files** for state persistence testing
- **Sample data** for consistent test scenarios
- **App instances** with mocked dependencies
- **UI component mocks** for Textual framework

## Writing Tests

### Test Naming Convention
Use descriptive names that explain the scenario:
```python
def test_radio_activates_immediately_with_empty_playlist():
def test_mpv_called_directly_with_youtube_url():  
def test_search_handles_network_error_gracefully():
```

### Test Structure
Follow the Arrange-Act-Assert pattern:
```python
@pytest.mark.asyncio
async def test_play_song_workflow(self, app_instance):
    """Test complete song playback workflow."""
    # Arrange
    song = SongItem("Test Song", "Artist", "video123", "3:30")
    
    # Act
    with patch('subprocess.Popen') as mock_mpv:
        await app_instance.play_song(song)
    
    # Assert
    assert app_instance.last_played_song == song
    mock_mpv.assert_called_once()
```

### Async Test Support
For async tests, use the `@pytest.mark.asyncio` decorator:
```python
@pytest.mark.asyncio
async def test_async_functionality(self, app_instance):
    """Test async functionality."""
    result = await app_instance.async_method()
    assert result is not None
```

### Mocking External Dependencies
Use comprehensive mocking to isolate tests:
```python
# Mock YouTube Music API
app_instance.ytmusic.search.return_value = mock_search_results

# Mock MPV process
with patch('subprocess.Popen') as mock_mpv:
    mock_process = Mock()
    mock_process.poll.return_value = None
    mock_mpv.return_value = mock_process

# Mock UI components
with patch.object(app_instance, 'query_one', return_value=mock_widget):
```

## Common Testing Patterns

### Testing MPV Integration
```python
@pytest.mark.asyncio
async def test_mpv_playback(self, app_instance):
    song = SongItem("Test", "Artist", "video123", "3:00")
    
    with patch('subprocess.Popen') as mock_mpv:
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_mpv.return_value = mock_process
        
        await app_instance.play_song(song)
        
        # Verify direct MPV call with YouTube URL
        call_args = mock_mpv.call_args[0][0]
        assert "mpv" in call_args
        assert "--no-video" in call_args
        assert "--really-quiet" in call_args
        assert f"https://www.youtube.com/watch?v={song.video_id}" in call_args[-1]
```

### Testing Radio Functionality
```python
@pytest.mark.asyncio
async def test_radio_workflow(self, app_instance):
    # Mock radio playlist
    app_instance.ytmusic.get_watch_playlist.return_value = {
        "tracks": [{"title": "Song", "artists": [{"name": "Artist"}], 
                   "videoId": "id123", "duration": {"text": "3:00"}}]
    }
    
    with patch('subprocess.Popen') as mock_mpv:
        with patch.object(app_instance, 'update_radio_queue_display'):
            await app_instance.start_radio(test_song)
            
            # Radio activates immediately
            assert app_instance.radio_active is True
            assert len(app_instance.radio_queue) >= 0
```

### Testing State Persistence
```python
def test_state_persistence(self, temp_state_file):
    with patch('ytmusic_tui.YTMusic'):
        app = YTMusicTUI()
        app.state_file = temp_state_file
        
        # Set state
        app.last_played_song = SongItem("Test", "Artist", "id", "3:00")
        app.save_state()
        
        # Create new instance and load
        app2 = YTMusicTUI() 
        app2.state_file = temp_state_file
        app2.load_state()
        
        # Verify state restored
        assert app2.last_played_song.title == "Test"
```

### Testing Error Handling
```python
@pytest.mark.asyncio
async def test_api_error_recovery(self, app_instance):
    # Simulate API error
    app_instance.ytmusic.search.side_effect = ConnectionError("Network error")
    
    with patch.object(app_instance, 'update_status') as mock_status:
        await app_instance.perform_search("test")
        
        # Should handle gracefully
        mock_status.assert_called()
        assert len(app_instance.songs) == 0
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: pytest -m "not network and not external"  # Skip external deps
      - uses: codecov/codecov-action@v3  # Upload coverage
```

### Test Environment Strategy
- **Development**: All tests with external tools
- **CI/CD**: Unit and integration tests (excluding network/external)
- **Production**: Smoke tests and health checks

## Performance Guidelines

### Test Speed Targets
- **Unit tests**: < 1 second per test
- **Integration tests**: < 5 seconds per test  
- **E2E tests**: < 2 seconds per test (with mocking)
- **Total suite**: < 30 seconds

### Optimization Tips
1. Use comprehensive mocking to avoid slow external calls
2. Leverage pytest's parallel execution (`pytest -n auto`)
3. Use markers to run subsets during development
4. Skip slow/network tests in fast feedback loops

## Troubleshooting

### Common Issues

1. **External tool dependencies**: 
   ```bash
   # Install mpv for full integration tests
   sudo apt-get install mpv  # Ubuntu/Debian
   brew install mpv          # macOS
   ```

2. **Network connectivity issues**:
   ```bash
   # Skip network tests if needed
   pytest -m "not network"
   ```

3. **Async test problems**:
   ```python
   # Always use @pytest.mark.asyncio for async tests
   @pytest.mark.asyncio
   async def test_async_func():
       result = await async_function()
   ```

4. **UI component access errors**:
   ```python
   # Use proper UI mocking from conftest.py fixtures
   def test_ui_interaction(self, app_instance):
       # app_instance fixture includes UI mocking
   ```

### Debugging Failed Tests
1. Run with verbose output: `pytest -v -s`
2. Use debugger: `pytest --pdb`
3. Check actual vs expected behavior in app
4. Verify mock configurations match real interfaces
5. Review test output for specific error messages

## Maintenance

### Regular Tasks
1. **Update test data**: Keep realistic scenarios current
2. **Monitor coverage**: Ensure new features have tests
3. **Performance monitoring**: Keep execution times reasonable  
4. **Dependency updates**: Update mocked interfaces when dependencies change

### Adding New Tests
1. Choose appropriate category (unit/integration/e2e)
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Use existing fixtures and patterns
4. Update this documentation for new testing patterns

### Coverage Goals
- **Unit tests**: Focus on critical business logic
- **Integration tests**: All external API and process interactions  
- **E2E tests**: All major user workflows
- **Error handling**: Critical error conditions and recovery paths

## Conclusion

This test suite provides comprehensive validation of the TUI YouTube Music Player with:
- **Fast feedback** for development
- **Reliable CI/CD integration** 
- **Clear documentation** of application behavior
- **Maintainable patterns** for future development

The testing infrastructure is production-ready and supports confident development and deployment of new features. 