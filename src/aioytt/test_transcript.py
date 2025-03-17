from typing import Final
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from .transcript import TranscriptSnippet
from .transcript import get_transcript_from_url

VIDEO_ID: Final[str] = "dQw4w9WgXcQ"
YOUTUBE_URL: Final[str] = f"https://www.youtube.com/watch?v={VIDEO_ID}"


@pytest.mark.asyncio
async def test_get_transcript_from_url_calls_parse_video_id():
    """Test that get_transcript_from_url calls parse_video_id with the correct URL."""

    with (
        patch("aioytt.transcript.parse_video_id") as mock_parse_video_id,
        patch("aioytt.transcript.get_transcript_from_video_id", new_callable=AsyncMock) as mock_get_transcript,
    ):
        mock_parse_video_id.return_value = VIDEO_ID
        mock_get_transcript.return_value = []

        await get_transcript_from_url(YOUTUBE_URL)

        mock_parse_video_id.assert_called_once_with(YOUTUBE_URL)


@pytest.mark.asyncio
async def test_get_transcript_from_url_calls_get_transcript_from_video_id():
    """Test that get_transcript_from_url calls get_transcript_from_video_id with the correct parameters."""
    language_codes = ["en", "fr"]

    with (
        patch("aioytt.transcript.parse_video_id") as mock_parse_video_id,
        patch("aioytt.transcript.get_transcript_from_video_id", new_callable=AsyncMock) as mock_get_transcript,
    ):
        mock_parse_video_id.return_value = VIDEO_ID
        expected_result = [
            TranscriptSnippet(text="Hello", start=0.0, duration=1.0),
            TranscriptSnippet(text="World", start=1.0, duration=1.0),
        ]
        mock_get_transcript.return_value = expected_result

        result = await get_transcript_from_url(YOUTUBE_URL, language_codes)

        mock_get_transcript.assert_called_once_with(VIDEO_ID, language_codes)
        assert result == expected_result


@pytest.mark.asyncio
async def test_get_transcript_from_url_with_default_language():
    """Test that get_transcript_from_url uses the default language ('en') when not specified."""

    with (
        patch("aioytt.transcript.parse_video_id") as mock_parse_video_id,
        patch("aioytt.transcript.get_transcript_from_video_id", new_callable=AsyncMock) as mock_get_transcript,
    ):
        mock_parse_video_id.return_value = VIDEO_ID
        mock_get_transcript.return_value = []

        await get_transcript_from_url(YOUTUBE_URL)

        mock_get_transcript.assert_called_once_with(VIDEO_ID, ("en",))
