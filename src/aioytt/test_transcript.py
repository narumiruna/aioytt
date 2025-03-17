from typing import Final
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from .errors import CaptionsNotFoundError
from .transcript import TranscriptSnippet
from .transcript import get_transcript_from_url
from .transcript import get_transcript_from_video_id
from .transcript import parse_transcript

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


@pytest.mark.asyncio
async def test_get_transcript_from_video_id():
    """Test that get_transcript_from_video_id calls all required functions and returns parsed transcript."""

    with (
        patch("aioytt.transcript.fetch_video_html", new_callable=AsyncMock) as mock_fetch_html,
        patch("aioytt.transcript.parse_captions") as mock_parse_captions,
        patch("aioytt.transcript.get_caption_track") as mock_get_caption_track,
        patch("aioytt.transcript.fetch_html", new_callable=AsyncMock) as mock_fetch_xml,
        patch("aioytt.transcript.parse_transcript") as mock_parse_transcript,
    ):
        # Setup mocks
        mock_fetch_html.return_value = "<html>Mock HTML</html>"
        mock_captions = AsyncMock()
        mock_parse_captions.return_value = mock_captions
        mock_caption_track = AsyncMock()
        mock_caption_track.base_url = "https://example.com/captions"
        mock_get_caption_track.return_value = mock_caption_track
        mock_fetch_xml.return_value = "<xml>Mock XML</xml>"
        expected_result = [TranscriptSnippet(text="Test", start=0.0, duration=1.0)]
        mock_parse_transcript.return_value = expected_result

        # Call the function
        result = await get_transcript_from_video_id(VIDEO_ID, ["en", "fr"])

        # Verify calls
        mock_fetch_html.assert_called_once_with(VIDEO_ID)
        mock_parse_captions.assert_called_once_with(mock_fetch_html.return_value)
        mock_get_caption_track.assert_called_once_with(mock_captions.caption_tracks, ["en", "fr"])
        mock_fetch_xml.assert_called_once_with(mock_caption_track.base_url)
        mock_parse_transcript.assert_called_once_with(mock_fetch_xml.return_value)
        assert result == expected_result


@pytest.mark.asyncio
async def test_get_transcript_from_video_id_with_default_language():
    """Test that get_transcript_from_video_id uses default language when not specified."""

    with (
        patch("aioytt.transcript.fetch_video_html", new_callable=AsyncMock) as mock_fetch_html,
        patch("aioytt.transcript.parse_captions") as mock_parse_captions,
        patch("aioytt.transcript.get_caption_track") as mock_get_caption_track,
        patch("aioytt.transcript.fetch_html", new_callable=AsyncMock) as mock_fetch_xml,
        patch("aioytt.transcript.parse_transcript") as mock_parse_transcript,
    ):
        # Setup minimal mocks
        mock_fetch_html.return_value = "<html>Mock HTML</html>"
        mock_captions = AsyncMock()
        mock_parse_captions.return_value = mock_captions
        mock_caption_track = AsyncMock()
        mock_caption_track.base_url = "https://example.com/captions"
        mock_get_caption_track.return_value = mock_caption_track
        mock_fetch_xml.return_value = "<xml>Mock XML</xml>"
        mock_parse_transcript.return_value = []

        # Call the function
        await get_transcript_from_video_id(VIDEO_ID)

        # Verify default language is used
        mock_get_caption_track.assert_called_once_with(mock_captions.caption_tracks, ("en",))


@pytest.mark.asyncio
async def test_get_transcript_from_video_id_no_captions_url():
    """Test that get_transcript_from_video_id raises CaptionsNotFoundError when base_url is empty."""

    with (
        patch("aioytt.transcript.fetch_video_html", new_callable=AsyncMock) as mock_fetch_html,
        patch("aioytt.transcript.parse_captions") as mock_parse_captions,
        patch("aioytt.transcript.get_caption_track") as mock_get_caption_track,
    ):
        # Setup mocks
        mock_fetch_html.return_value = "<html>Mock HTML</html>"
        mock_captions = AsyncMock()
        mock_parse_captions.return_value = mock_captions
        mock_caption_track = AsyncMock()
        mock_caption_track.base_url = None  # No URL available
        mock_get_caption_track.return_value = mock_caption_track

        # Assert error is raised
        with pytest.raises(CaptionsNotFoundError):
            await get_transcript_from_video_id(VIDEO_ID)


def test_parse_transcript_with_valid_xml():
    """Test parse_transcript with valid XML containing caption data."""
    xml = """
    <transcript>
        <text start="0.0" dur="1.0">Hello</text>
        <text start="1.0" dur="2.0">World</text>
        <text start="3.0" dur="1.5">Testing</text>
    </transcript>
    """

    result = parse_transcript(xml)

    assert len(result) == 3
    assert result[0] == TranscriptSnippet(text="Hello", start=0.0, duration=1.0)
    assert result[1] == TranscriptSnippet(text="World", start=1.0, duration=2.0)
    assert result[2] == TranscriptSnippet(text="Testing", start=3.0, duration=1.5)


def test_parse_transcript_with_missing_duration():
    """Test parse_transcript handles XML elements without duration attribute."""
    xml = """
    <transcript>
        <text start="1.5">No duration specified</text>
        <text start="3.0" dur="2.0">With duration</text>
    </transcript>
    """

    result = parse_transcript(xml)

    assert len(result) == 2
    assert result[0] == TranscriptSnippet(text="No duration specified", start=1.5, duration=0.0)
    assert result[1] == TranscriptSnippet(text="With duration", start=3.0, duration=2.0)


def test_parse_transcript_with_empty_elements():
    """Test parse_transcript filters out elements with no text content."""
    xml = """
    <transcript>
        <text start="0.0" dur="1.0">Valid text</text>
        <text start="1.0" dur="1.0"></text>
        <text start="2.0" dur="1.0">Another valid text</text>
    </transcript>
    """

    result = parse_transcript(xml)

    assert len(result) == 2
    assert result[0].text == "Valid text"
    assert result[1].text == "Another valid text"


def test_parse_transcript_with_html_entities():
    """Test parse_transcript correctly unescapes HTML entities."""
    xml = """
    <transcript>
        <text start="0.0" dur="1.0">I &amp; you</text>
        <text start="1.0" dur="1.0">Less &lt; Greater &gt;</text>
        <text start="2.0" dur="1.0">Quote &quot;test&quot;</text>
    </transcript>
    """

    result = parse_transcript(xml)

    assert len(result) == 3
    assert result[0].text == "I & you"
    assert result[1].text == "Less < Greater >"
    assert result[2].text == 'Quote "test"'
