# TUI YouTube Music Player - Test Documentation

This document describes the comprehensive test suite for the TUI YouTube Music Player, which documents and validates all application features.

## Overview

The test suite is designed to:
- **Document application features** through comprehensive test coverage
- **Validate functionality** across all components and workflows
- **Ensure reliability** with robust error handling tests
- **Support development** with fast feedback loops

## Test Structure

### Directory Layout
```
tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Shared fixtures and test configuration
├── unit/                   # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_song_items.py         # SongItem/RadioQueueItem classes
│   ├── test_app_state.py          # State management & persistence
│   ├── test_search_playback.py    # Search & playback functionality
│   └── test_radio_functionality.py # Radio mode features
├── integration/            # Integration tests (component interactions)
│   ├── __init__.py
│   ├── test_youtube_music_api.py  # YouTube Music API integration
│   └── test_external_processes.py # MPV/yt-dlp integration
└── e2e/                    # End-to-end tests (complete workflows)
    ├── __init__.py
    └── test_full_workflow.py      # Complete user workflows
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests that validate individual components:

- **`test_song_items.py`** - SongItem and RadioQueueItem classes
  - Item creation and property access
  - Display text formatting with emojis
  - Special character handling
  - Current vs upcoming song indicators

- **`test_app_state.py`** - Application state management
  - Initialization and default state
  - State persistence (save/load JSON)
  - Radio state tracking
  - Process cleanup mechanisms

- **`test_search_playback.py`** - Core music functionality
  - YouTube Music search (success/failure scenarios)
  - Song playback via mpv integration
  - Audio URL extraction with yt-dlp
  - Keyboard action handlers

- **`test_radio_functionality.py`** - Radio mode features
  - Radio start/stop workflows
  - Queue management and auto-refilling
  - Manual progression and auto-progression
  - Radio queue display and visibility
  - Thread safety and race condition protection

### Integration Tests (`tests/integration/`)
Tests that validate component interactions:

- **`test_youtube_music_api.py`** - YouTube Music API integration
  - Real API connectivity (with network markers)
  - Search functionality with different filters
  - Radio playlist generation
  - Error handling for network issues
  - API response parsing and validation
  - Performance baselines

- **`test_external_processes.py`** - External tool integration
  - MPV media player integration
  - yt-dlp URL extraction and streaming
  - Process lifecycle management
  - Audio stream handling
  - Error recovery scenarios

### End-to-End Tests (`tests/e2e/`)
Complete workflow tests that simulate real user interactions:

- **`test_full_workflow.py`** - Complete user workflows
  - Search → select → play workflow
  - Radio mode workflow (start, skip, stop)
  - State persistence across sessions
  - Keyboard shortcuts and navigation
  - Error recovery scenarios
  - Complete user session simulation

## Test Markers

Tests are categorized with pytest markers for selective execution:

- `@pytest.mark.unit` - Fast unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Tests that may take several seconds
- `@pytest.mark.network` - Tests requiring internet connection
- `@pytest.mark.external` - Tests requiring external tools (mpv, yt-dlp)

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional external tools** (for integration tests):
   - `mpv` - Audio player
   - `yt-dlp` - YouTube URL extraction

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest -m unit                    # Unit tests only (fast)
pytest -m integration            # Integration tests
pytest -m e2e                    # End-to-end tests

# Run tests excluding slow/network tests
pytest -m "not slow and not network"

# Run specific test files
pytest tests/unit/test_song_items.py
pytest tests/integration/test_youtube_music_api.py
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=ytmusic_tui

# Generate HTML coverage report
pytest --cov=ytmusic_tui --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI)
pytest --cov=ytmusic_tui --cov-report=xml
```

### Advanced Test Options

```bash
# Run tests in parallel (if pytest-xdist installed)
pytest -n auto

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Run tests with specific keyword
pytest -k "radio"              # Tests with "radio" in name
pytest -k "search and not api" # Search tests excluding API tests

# Run with profiling
pytest --profile

# Dry run (collect tests without running)
pytest --collect-only
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

The test suite uses pytest with the following configuration:
- Coverage reporting enabled by default
- Strict marker and config validation
- Custom markers for test categorization
- Warning filters for clean output

### Fixtures (`conftest.py`)

Shared test fixtures provide:
- **Mock objects** for external APIs and processes
- **Temporary files** for state persistence testing
- **Sample data** for consistent test scenarios
- **App instances** with mocked dependencies

## Test Data and Mocking

### Mocking Strategy

Tests use comprehensive mocking to:
- **Isolate components** from external dependencies
- **Control test scenarios** with predictable data
- **Simulate error conditions** for robust testing
- **Ensure fast execution** without network calls

### Test Data

Realistic test data includes:
- Popular songs (Queen, Beatles, etc.)
- Various audio formats and durations
- Edge cases (empty results, missing fields)
- Error scenarios (network failures, invalid data)

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

### Test Environments

- **Development**: All tests with external tools
- **CI/CD**: Unit and integration tests (excluding network/external)
- **Production**: Smoke tests and health checks

## Debugging Tests

### Useful Commands

```bash
# Run with detailed output and no capture
pytest -v -s

# Run specific test with debug output
pytest tests/unit/test_song_items.py::TestSongItem::test_song_item_creation -v -s

# Debug test failures
pytest --pdb              # Drop into debugger on failure
pytest --trace            # Drop into debugger at start of each test

# Show test execution times
pytest --durations=10     # Show 10 slowest tests
```

### Common Issues

1. **External tool dependencies**: Install mpv and yt-dlp for full integration tests
2. **Network connectivity**: Some integration tests require internet access
3. **Async test issues**: Ensure proper event loop handling in async tests
4. **Mock configuration**: Verify mock objects match real API interfaces

## Contributing Tests

### Guidelines

1. **Test naming**: Use descriptive names that explain the scenario
2. **Test structure**: Follow Arrange-Act-Assert pattern
3. **Async support**: Use `@pytest.mark.asyncio` for async tests
4. **Mocking**: Mock external dependencies consistently
5. **Documentation**: Include docstrings explaining test purpose

### Adding New Tests

1. **Choose appropriate category**: Unit, integration, or e2e
2. **Add appropriate markers**: `@pytest.mark.unit`, etc.
3. **Use existing fixtures**: Leverage shared test infrastructure
4. **Update documentation**: Add test descriptions to this document

### Test Coverage Goals

- **Unit tests**: >95% line coverage of core functionality
- **Integration tests**: All external API interactions
- **E2E tests**: All major user workflows
- **Error handling**: All error conditions and recovery paths

## Performance Considerations

### Test Speed

- **Unit tests**: < 1 second per test
- **Integration tests**: < 10 seconds per test
- **E2E tests**: < 30 seconds per test

### Parallel Execution

Tests are designed to run in parallel safely:
- No shared state between tests
- Isolated temporary files
- Independent mock configurations

## Maintenance

### Regular Tasks

1. **Update test data**: Keep realistic test scenarios current
2. **Review coverage**: Ensure new features have adequate tests
3. **Performance monitoring**: Keep test execution times reasonable
4. **Dependency updates**: Update mocked API interfaces when dependencies change

### Test Health Metrics

Monitor these metrics for test suite health:
- Test execution time trends
- Test failure rates
- Coverage percentage changes
- Flaky test identification 