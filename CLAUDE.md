# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

aioytt is an async Python library for extracting transcripts from YouTube videos. It uses httpx for async HTTP requests and parses the `ytInitialPlayerResponse` JSON data from YouTube pages to retrieve caption track information.

## Common Commands

### Development Setup
```bash
# Install dependencies (including dev dependencies)
uv sync
```

### Code Quality Checks
```bash
# Linting (using ruff)
make lint
# or
uv run ruff check .

# Type checking (using mypy)
make type
# or
uv run mypy --install-types --non-interactive src
```

### Testing
```bash
# Run all tests with coverage
make test
# or
uv run pytest -v -s --cov=src tests

# Run specific test file
uv run pytest -v -s tests/test_transcript.py

# Run specific test function
uv run pytest -v -s tests/test_transcript.py::test_parse_transcript_with_valid_xml
```

### Publishing
```bash
make publish
# or
uv build -f wheel && uv publish
```

### Pre-commit Hooks
The project uses pre-commit for automated checks including ruff, mypy, and uv-lock.

### CI/CD
- **GitHub Actions**: Runs on push/PR to main branch
  - Python 3.12 matrix
  - Steps: lint → type check → test → upload coverage to Codecov
- **Publishing**: Manual workflow using `make publish` (builds wheel and publishes to PyPI)
- **Coverage**: Integrated with Codecov (requires `CODECOV_TOKEN` secret)

## Core Architecture

### Module Structure

- **video_id.py**: Parses YouTube URLs and extracts the 11-character video ID
  - Supports multiple URL formats (youtube.com, youtu.be, m.youtube.com, etc.)
  - Validates URL scheme, netloc, and video ID length
  - Defines allowed URL format constants

- **transcript.py**: Core functionality module handling the transcript extraction flow
  - `get_transcript_from_url()` / `get_transcript_from_video_id()`: Main entry point functions
  - `fetch_video_html()`: Fetches YouTube video page HTML
  - `parse_captions()`: Parses `ytInitialPlayerResponse` JSON data from HTML
  - `get_caption_track()`: Selects appropriate caption track based on language codes
  - `parse_transcript()`: Parses caption XML and converts to `TranscriptSnippet` object list

- **caption.py**: Pydantic data models
  - `Captions`: Contains caption tracks, audio tracks, etc.
  - `CaptionTrack`: Single caption track with base_url, language_code, etc.
  - `AudioTrack`, `TranslationLanguage`: Supporting data structures
  - Uses `validation_alias` to map YouTube API's camelCase fields

- **errors.py**: Custom exception classes
  - All exceptions inherit from `AioyttError`
  - Includes URL validation errors, captions not found errors, etc.

### Data Flow

1. URL → `parse_video_id()` → video ID
2. video ID → `fetch_video_html()` → HTML
3. HTML → `parse_captions()` → `Captions` object
4. `Captions` + language codes → `get_caption_track()` → `CaptionTrack`
5. `CaptionTrack.base_url` → `fetch_html()` → XML
6. XML → `parse_transcript()` → `list[TranscriptSnippet]`

### Key Design Decisions

- **Async Design**: All HTTP requests use `httpx.AsyncClient` for async operations
- **Language Selection Logic**: `get_caption_track()` accepts string or iterable of language codes, matches in order, returns first track if no match
- **Default Language**: Defaults to English (`"en"`), but `DEFAULT_LANGUAGES` in video_id.py defines a Traditional Chinese-first language list (not used in main flow)
- **HTML Entity Handling**: Uses `html.unescape()` to handle HTML entities in caption text
- **XML Parsing**: Uses stdlib `xml.etree.ElementTree`, filters out elements without text content

## Development Guidelines

### Type Annotation Requirements
- **Must use built-in type syntax** (Python 3.12+)
- Use `list[X]` not `List[X]`
- Use `dict[K, V]` not `Dict[K, V]`
- Use `X | Y` not `Union[X, Y]`
- Use `X | None` not `Optional[X]`

### Ruff Configuration
- Line length limit: 120 characters
- Force single-line imports (`force-single-line = true`)
- `__init__.py` allows F401 (unused import) and F403 (star import)

### Testing Conventions
- Uses `pytest` and `pytest-asyncio`
- Async tests require `@pytest.mark.asyncio` decorator
- Heavy use of `unittest.mock.patch` and `AsyncMock` for unit tests
- Coverage reports use `pytest-cov`

### Logging
- Uses `loguru` for logging
- Log level controlled via `LOGURU_LEVEL` environment variable (defaults to INFO)
- Logger initialized in `__init__.py`

## Common Development Patterns

### Adding a New Error Type
1. Define the exception in `errors.py` inheriting from `AioyttError`
2. Provide a descriptive `__init__` with context parameters
3. Raise it at the appropriate location in the flow
4. Add corresponding test cases

### Adding Support for New URL Formats
1. Add the netloc to `ALLOWED_NETLOCS` in `video_id.py`
2. Update parsing logic in `parse_video_id()` if needed
3. Add test cases in `test_video_id.py`

### Extending Language Support
- Current default: English (`"en"`)
- To change: Modify the default in function signatures or use `DEFAULT_LANGUAGES`
- Language matching is case-sensitive and uses YouTube's language codes

## Known Limitations and Gotchas

- `parse_captions()` depends on the `ytInitialPlayerResponse` variable in YouTube's HTML structure; changes to YouTube's structure may break parsing
- Video ID length is fixed at 11 characters; this validation may need adjustment as YouTube's system evolves
- Caption track selection logic: If no matching language is found, automatically falls back to the first available caption track
- No HTTP retry mechanism for network failures
- `DEFAULT_LANGUAGES` constant in video_id.py is defined but not used in the main flow

## Potential Improvements

### High Priority
- **Add docstrings**: Functions lack documentation strings for better IDE support and user guidance
- **Fill pyproject.toml description**: Currently empty, should describe the project
- **Error context**: Enhance error messages with more context (e.g., available languages when requested language not found)

### Medium Priority
- **HTTP retry logic**: Add retry mechanism for transient network failures using tenacity or httpx retry
- **CLI tool**: Add command-line interface to leverage the `rich` dependency (e.g., `aioytt <url>`)
- **Integration tests**: Add end-to-end tests with recorded HTTP responses (consider using vcrpy)
- **Use DEFAULT_LANGUAGES**: Either integrate the language priority list into `get_caption_track()` or remove it

### Low Priority
- **More precise type hints**: Improve type accuracy (e.g., parse_qs returns `dict[str, list[str]]`)
- **Usage examples**: Add more comprehensive examples for multi-language handling, error handling patterns
