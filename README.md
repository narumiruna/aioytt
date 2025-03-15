# aioytt

```python
import asyncio

from rich import print

from aioytt.transcript import get_transcript_from_url


async def main(url: str) -> None:
    transcript = await get_transcript_from_url(url)
    for snippet in transcript:
        print(snippet)


if __name__ == "__main__":
    asyncio.run(main("url"))

```
