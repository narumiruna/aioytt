from collections.abc import Iterable


class AioyttError(Exception):
    pass


class UnsupportedURLSchemeError(AioyttError):
    def __init__(self, scheme: str) -> None:
        super().__init__(f"unsupported URL scheme: {scheme}")


class UnsupportedURLNetlocError(AioyttError):
    def __init__(self, netloc: str) -> None:
        super().__init__(f"unsupported URL netloc: {netloc}")


class VideoIDError(AioyttError):
    def __init__(self, video_id: str) -> None:
        super().__init__(f"invalid video ID: {video_id}")


class NoVideoIDFoundError(AioyttError):
    def __init__(self, url: str) -> None:
        super().__init__(f"no video found in URL: {url}")


class InitialPlayerResponseNotFoundError(AioyttError):
    def __init__(self) -> None:
        super().__init__("Could not find ytInitialPlayerResponse")


class CaptionsNotFoundError(AioyttError):
    def __init__(self) -> None:
        super().__init__("No captions found in the video")


class LanguageNotFoundError(AioyttError):
    def __init__(self, language_codes: Iterable[str]) -> None:
        codes = ", ".join(language_codes) if isinstance(language_codes, list) else str(language_codes)
        super().__init__(f"Requested language(s) not found: {codes}")
