# aioytt

```python
import asyncio

from rich import print

from aioytt.transcript import get_transcript


async def main(video_id: str) -> None:
    transcript = await get_transcript(video_id)
    for snippet in transcript:
        print(snippet)


if __name__ == "__main__":
    asyncio.run(main("video_id"))

```
