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
