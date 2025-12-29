"""Async Python library for extracting YouTube video transcripts."""

import os
import sys
from typing import Final

from loguru import logger

from .transcript import TranscriptSnippet
from .transcript import get_transcript_from_url
from .transcript import get_transcript_from_video_id
from .video_id import parse_video_id

__all__ = [
    "get_transcript_from_url",
    "get_transcript_from_video_id",
    "parse_video_id",
    "TranscriptSnippet",
]

LOGURU_LEVEL: Final[str] = os.getenv("LOGURU_LEVEL", "INFO")
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGURU_LEVEL}])  # ty:ignore[invalid-argument-type]
