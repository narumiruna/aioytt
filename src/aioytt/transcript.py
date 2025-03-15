from __future__ import annotations

import json
import re
from collections.abc import Iterable
from functools import cache
from html import unescape
from re import Pattern
from typing import Final
from xml.etree import ElementTree

import httpx
from pydantic import BaseModel

from .caption import Captions
from .caption import CaptionTrack
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
    text: str
    start: float
    duration: float


# var ytInitialPlayerResponse = {"responseContext": ...
def parse_captions(html: str) -> Captions:
    splitted_html = html.split("var ytInitialPlayerResponse =")

    if len(splitted_html) < 2:
        raise ValueError("Could not find ytInitialPlayerResponse")

    response_json = json.loads(splitted_html[1].split("</script>")[0].strip(";"))

    captions_json = response_json.get("captions", {}).get("playerCaptionsTracklistRenderer")
    if not captions_json or "captionTracks" not in captions_json:
        raise ValueError("Could not find captions")

    return Captions.model_validate(captions_json)


async def fetch_video_html(video_id: str) -> str:
    return await fetch_html(WATCH_URL, params={"v": video_id})


async def fetch_html(url: str, params=None) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, params=params)
        response.raise_for_status()
        return response.text


def get_caption_track(caption_tracks: list[CaptionTrack], language_codes: str | Iterable[str]) -> CaptionTrack:
    if len(caption_tracks) == 1:
        return caption_tracks[0]

    if isinstance(language_codes, str):
        language_codes = [language_codes]

    for language_code in language_codes:
        for caption_track in caption_tracks:
            if caption_track.language_code == language_code:
                return caption_track

    return caption_tracks[0]


@cache
def _get_html_regex(preserve_formatting: bool) -> Pattern[str]:
    if preserve_formatting:
        formats_regex = "|".join(_FORMATTING_TAGS)
        formats_regex = r"<\/?(?!\/?(" + formats_regex + r")\b).*?\b>"
        html_regex = re.compile(formats_regex, re.IGNORECASE)
    else:
        html_regex = re.compile(r"<[^>]*>", re.IGNORECASE)
    return html_regex


def parse_transcript(xml: str) -> list[TranscriptSnippet]:
    return [
        TranscriptSnippet(
            text=re.sub(_get_html_regex(preserve_formatting=False), "", unescape(xml_element.text)),
            start=float(xml_element.attrib["start"]),
            duration=float(xml_element.attrib.get("dur", "0.0")),
        )
        for xml_element in ElementTree.fromstring(xml)
        if xml_element.text is not None
    ]


async def get_transcript_from_video_id(
    video_id: str, language_codes: str | Iterable[str] = ("en",)
) -> list[TranscriptSnippet]:
    video_html = await fetch_video_html(video_id)

    captions = parse_captions(video_html)

    caption_track = get_caption_track(captions.caption_tracks, language_codes)

    xml = await fetch_html(caption_track.base_url)
    return parse_transcript(xml)


async def get_transcript_from_url(url: str, language_codes: str | Iterable[str] = ("en",)) -> list[TranscriptSnippet]:
    video_id = parse_video_id(url)
    return await get_transcript_from_video_id(video_id, language_codes)
