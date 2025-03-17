import pytest

from .errors import NoVideoIDFoundError
from .errors import UnsupportedURLNetlocError
from .errors import UnsupportedURLSchemeError
from .errors import VideoIDError
from .video_id import parse_video_id


class TestParseVideoId:
    def test_standard_youtube_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_nocookie_url(self):
        url = "https://www.youtube-nocookie.com/watch?v=dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_mobile_youtube_url(self):
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_youtube_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=featured"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_vid_plus_url(self):
        url = "https://vid.plus/dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_unsupported_scheme(self):
        url = "ftp://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with pytest.raises(UnsupportedURLSchemeError):
            parse_video_id(url)

    def test_unsupported_netloc(self):
        url = "https://vimeo.com/watch?v=dQw4w9WgXcQ"
        with pytest.raises(UnsupportedURLNetlocError):
            parse_video_id(url)

    def test_no_video_id(self):
        url = "https://www.youtube.com/watch"
        with pytest.raises(NoVideoIDFoundError):
            parse_video_id(url)

    def test_invalid_video_id_length(self):
        url = "https://youtu.be/short"
        with pytest.raises(VideoIDError):
            parse_video_id(url)

    def test_youtube_url_with_additional_path(self):
        url = "https://www.youtube.com/watch/v/dQw4w9WgXcQ"
        video_id = parse_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
