# aioytt

Async Python library for extracting YouTube video transcripts.

## Features

- 🚀 **Async/Await Support**: Built with `httpx` for efficient async operations
- 🔄 **Auto Retry**: Automatic retry with exponential backoff for network failures
- 🌍 **Multi-Language**: Support for multiple caption languages with priority fallback
- 📝 **Type Safe**: Full type hints with Pydantic models
- ✅ **Well Tested**: Comprehensive test coverage

## Installation

```bash
pip install aioytt
```

Or with uv:

```bash
uv add aioytt
```

## Quick Start

```python
import asyncio

from aioytt import get_transcript_from_url

async def main():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript = await get_transcript_from_url(url)

    for snippet in transcript:
        print(f"[{snippet.start:.2f}s] {snippet.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Examples

### Get Transcript by Video ID

```python
from aioytt import get_transcript_from_video_id

async def get_by_id():
    video_id = "dQw4w9WgXcQ"
    transcript = await get_transcript_from_video_id(video_id)
    return transcript
```

### Multi-Language Support

```python
from aioytt import get_transcript_from_url

async def get_chinese_transcript():
    url = "https://www.youtube.com/watch?v=example"

    # Try to get Traditional Chinese first, then fallback to English
    transcript = await get_transcript_from_url(url, language_codes=["zh-TW", "en"])
    return transcript
```

### Error Handling

```python
from aioytt import get_transcript_from_url
from aioytt.errors import (
    CaptionsNotFoundError,
    VideoIDError,
    UnsupportedURLSchemeError,
)

async def safe_get_transcript(url: str):
    try:
        transcript = await get_transcript_from_url(url)
        return transcript
    except CaptionsNotFoundError:
        print("No captions available for this video")
    except VideoIDError as e:
        print(f"Invalid video ID: {e}")
    except UnsupportedURLSchemeError as e:
        print(f"Unsupported URL format: {e}")
```

### Parse Video ID

```python
from aioytt import parse_video_id

# Supports various URL formats
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
]

for url in urls:
    video_id = parse_video_id(url)
    print(video_id)  # dQw4w9WgXcQ
```

## API Reference

### Functions

#### `get_transcript_from_url(url, language_codes=("en",))`

Extract transcript from a YouTube URL.

- **Parameters:**
  - `url` (str): YouTube video URL
  - `language_codes` (str | Iterable[str]): Language code(s) in priority order
- **Returns:** `list[TranscriptSnippet]`
- **Raises:** `VideoIDError`, `CaptionsNotFoundError`, `httpx.HTTPError`

#### `get_transcript_from_video_id(video_id, language_codes=("en",))`

Extract transcript using video ID.

- **Parameters:**
  - `video_id` (str): 11-character YouTube video ID
  - `language_codes` (str | Iterable[str]): Language code(s) in priority order
- **Returns:** `list[TranscriptSnippet]`
- **Raises:** `CaptionsNotFoundError`, `httpx.HTTPError`

#### `parse_video_id(url)`

Parse and validate a YouTube URL to extract the video ID.

- **Parameters:**
  - `url` (str): YouTube video URL
- **Returns:** `str` - 11-character video ID
- **Raises:** `UnsupportedURLSchemeError`, `UnsupportedURLNetlocError`, `VideoIDError`, `NoVideoIDFoundError`

### Models

#### `TranscriptSnippet`

```python
class TranscriptSnippet(BaseModel):
    text: str          # Caption text (HTML entities decoded)
    start: float       # Start time in seconds
    duration: float    # Duration in seconds
```

## Retry Mechanism

The library automatically retries failed HTTP requests with exponential backoff:

- **Max Attempts:** 3
- **Backoff Strategy:** Exponential (1s → 2s → 4s, max 10s)
- **Retryable Errors:** `ConnectError`, `TimeoutException`, `NetworkError`
- **Non-Retryable:** HTTP status errors (404, 500, etc.)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/narumiruna/aioytt.git
cd aioytt

# Install dependencies
uv sync

# Run tests
make test

# Run linter
make lint

# Type check
make type
```

### Running Tests

```bash
# All tests
uv run pytest -v

# Specific test file
uv run pytest tests/test_transcript.py -v

# With coverage
uv run pytest --cov=src tests
```

## Requirements

- Python >= 3.12
- httpx >= 0.28.1
- loguru >= 0.7.3
- pydantic >= 2.10.6
- tenacity >= 9.0.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
