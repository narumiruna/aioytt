from urllib.parse import parse_qs
from urllib.parse import urlparse

from .errors import NoVideoIDFoundError
from .errors import UnsupportedURLNetlocError
from .errors import UnsupportedURLSchemeError
from .errors import VideoIDError

ALLOWED_SCHEMES = {
    "http",
    "https",
}
ALLOWED_NETLOCS = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}


def parse_video_id(url: str) -> str:
    """Parse and extract the video ID from a YouTube URL.

    Supports various YouTube URL formats including:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube-nocookie.com/watch?v=VIDEO_ID
    - https://vid.plus/VIDEO_ID

    Args:
        url: YouTube video URL.

    Returns:
        11-character video ID.

    Raises:
        UnsupportedURLSchemeError: If URL scheme is not http or https.
        UnsupportedURLNetlocError: If URL domain is not a supported YouTube domain.
        NoVideoIDFoundError: If no video ID parameter found in the URL.
        VideoIDError: If extracted video ID is not exactly 11 characters.

    Example:
        >>> parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> parse_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ALLOWED_SCHEMES:
        raise UnsupportedURLSchemeError(parsed_url.scheme)

    if parsed_url.netloc not in ALLOWED_NETLOCS:
        raise UnsupportedURLNetlocError(parsed_url.netloc)

    path = parsed_url.path

    if path.endswith("/watch"):
        query = parsed_url.query
        parsed_query = parse_qs(query)
        if "v" in parsed_query:
            ids = parsed_query["v"]
            video_id = ids if isinstance(ids, str) else ids[0]
        else:
            raise NoVideoIDFoundError(url)
    else:
        path = parsed_url.path.lstrip("/")
        video_id = path.split("/")[-1]

    if len(video_id) != 11:  # Video IDs are 11 characters long
        raise VideoIDError(video_id)

    return video_id
