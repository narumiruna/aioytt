from __future__ import annotations

import json
from collections.abc import Iterable
from html import unescape
from typing import Final
from xml.etree import ElementTree

import httpx
from loguru import logger
from pydantic import BaseModel
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from .caption import Captions
from .caption import CaptionTrack
from .errors import CaptionsNotFoundError
from .errors import InitialPlayerResponseNotFoundError
from .video_id import parse_video_id

WATCH_URL: Final[str] = "https://www.youtube.com/watch?"

_FORMATTING_TAGS = [
    "strong",  # important
    "em",  # emphasized
    "b",  # bold
    "i",  # italic
    "mark",  # marked
    "small",  # smaller
    "del",  # deleted
    "ins",  # inserted
    "sub",  # subscript
    "sup",  # superscript
]


class TranscriptSnippet(BaseModel):
    """A single snippet of transcript with timing information.

    Attributes:
        text: The transcript text (HTML entities decoded).
        start: Start time in seconds.
        duration: Duration in seconds.
    """

    text: str
    start: float
    duration: float


def parse_captions(html: str) -> Captions:
    """Parse caption data from YouTube video page HTML.

    Extracts the ytInitialPlayerResponse JSON from the HTML and parses
    the caption tracks information.

    Args:
        html: YouTube video page HTML content.

    Returns:
        Captions object containing caption tracks and audio tracks.

    Raises:
        InitialPlayerResponseNotFoundError: If ytInitialPlayerResponse variable not found.
        CaptionsNotFoundError: If no caption tracks found in the response.
    """
    splitted_html = html.split("var ytInitialPlayerResponse =")

    if len(splitted_html) < 2:
        raise InitialPlayerResponseNotFoundError()

    data = splitted_html[1]
    data = data.split("</script>")[0]
    data = data.split(";var head =")[0]
    data = data.strip(";")

    response_json = json.loads(data)

    captions_json = response_json.get("captions", {}).get("playerCaptionsTracklistRenderer")
    if not captions_json or "captionTracks" not in captions_json:
        raise CaptionsNotFoundError()

    return Captions.model_validate(captions_json)


async def fetch_video_html(video_id: str) -> str:
    """Fetch YouTube video page HTML by video ID.

    Args:
        video_id: YouTube video ID (11 characters).

    Returns:
        HTML content of the video page.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    return await fetch_html(WATCH_URL, params={"v": video_id})


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)),
    reraise=True,
)
async def fetch_html(url: str, params=None) -> str:
    """Fetch HTML content from a URL with automatic retry on network errors.

    Automatically retries up to 3 times with exponential backoff (1s, 2s, 4s)
    for network-related errors (ConnectError, TimeoutException, NetworkError).
    HTTP status errors (4xx, 5xx) are not retried.

    Args:
        url: The URL to fetch.
        params: Optional query parameters.

    Returns:
        HTML content as string.

    Raises:
        httpx.HTTPError: If the request fails after retries or encounters HTTP status errors.
    """
    logger.debug(f"Fetching URL: {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, params=params)
        response.raise_for_status()
        return response.text


def get_caption_track(caption_tracks: list[CaptionTrack], language_codes: str | Iterable[str]) -> CaptionTrack:
    """Select a caption track based on language preferences.

    Selects the first available caption track that matches the requested
    language codes (in order of preference). If no match is found, returns
    the first available track.

    Args:
        caption_tracks: List of available caption tracks.
        language_codes: Single language code or iterable of codes in priority order.

    Returns:
        The selected caption track.

    Raises:
        CaptionsNotFoundError: If no caption tracks are available.
    """
    if not caption_tracks:
        raise CaptionsNotFoundError()

    if len(caption_tracks) == 1:
        return caption_tracks[0]

    if isinstance(language_codes, str):
        language_codes = [language_codes]

    for language_code in language_codes:
        for caption_track in caption_tracks:
            if caption_track.language_code == language_code:
                return caption_track

    return caption_tracks[0]


def parse_transcript(xml: str) -> list[TranscriptSnippet]:
    """Parse transcript XML into structured snippets.

    Parses YouTube caption track XML format into TranscriptSnippet objects.
    HTML entities in text are automatically decoded.

    Args:
        xml: Caption track XML content.

    Returns:
        List of transcript snippets with text and timing information.
    """
    transcript_snippets = []
    for xml_element in ElementTree.fromstring(xml):
        text = xml_element.text
        if text is None:
            continue

        transcript_snippets.append(
            TranscriptSnippet(
                text=unescape(text.strip()),
                start=float(xml_element.attrib["start"]),
                duration=float(xml_element.attrib.get("dur", "0.0")),
            )
        )
    return transcript_snippets


async def get_transcript_from_video_id(
    video_id: str, language_codes: str | Iterable[str] = ("en",)
) -> list[TranscriptSnippet]:
    """Extract transcript from a YouTube video by video ID.

    Fetches the video page, extracts caption data, selects the appropriate
    language track, and returns the parsed transcript.

    Args:
        video_id: YouTube video ID (11 characters).
        language_codes: Language code(s) in priority order. Defaults to English ("en").
            Can be a single string or iterable of strings.

    Returns:
        List of transcript snippets with text and timing information.

    Raises:
        CaptionsNotFoundError: If no captions are available or no base URL found.
        httpx.HTTPError: If network requests fail.

    Example:
        >>> transcript = await get_transcript_from_video_id("dQw4w9WgXcQ")
        >>> transcript = await get_transcript_from_video_id("dQw4w9WgXcQ", ["zh-TW", "en"])
    """
    video_html = await fetch_video_html(video_id)

    captions = parse_captions(video_html)

    caption_track = get_caption_track(captions.caption_tracks, language_codes)

    base_url = caption_track.base_url
    if base_url is None:
        raise CaptionsNotFoundError()

    xml = await fetch_html(base_url)
    return parse_transcript(xml)


async def get_transcript_from_url(url: str, language_codes: str | Iterable[str] = ("en",)) -> list[TranscriptSnippet]:
    """Extract transcript from a YouTube video by URL.

    Parses the video ID from the URL and fetches the transcript.
    Supports various YouTube URL formats (youtube.com, youtu.be, etc.).

    Args:
        url: YouTube video URL.
        language_codes: Language code(s) in priority order. Defaults to English ("en").
            Can be a single string or iterable of strings.

    Returns:
        List of transcript snippets with text and timing information.

    Raises:
        VideoIDError: If the URL contains an invalid video ID.
        UnsupportedURLSchemeError: If the URL scheme is not supported.
        UnsupportedURLNetlocError: If the URL domain is not supported.
        NoVideoIDFoundError: If no video ID found in the URL.
        CaptionsNotFoundError: If no captions are available.
        httpx.HTTPError: If network requests fail.

    Example:
        >>> url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        >>> transcript = await get_transcript_from_url(url)
        >>> transcript = await get_transcript_from_url(url, ["zh-TW", "en"])
    """
    video_id = parse_video_id(url)
    return await get_transcript_from_video_id(video_id, language_codes)
