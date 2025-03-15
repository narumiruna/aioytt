import os
import sys
from typing import Final

from loguru import logger

from .transcript import get_transcript_from_url
from .transcript import get_transcript_from_video_id

LOGURU_LEVEL: Final[str] = os.getenv("LOGURU_LEVEL", "INFO")
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGURU_LEVEL}])
