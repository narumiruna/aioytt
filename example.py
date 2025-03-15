import asyncio

import click
from rich import print

from aioytt.transcript import get_transcript


@click.command()
@click.argument("video_id", type=click.STRING)
async def main(video_id: str) -> None:
    transcript = await get_transcript(video_id)
    for snippet in transcript:
        print(snippet)


if __name__ == "__main__":
    asyncio.run(main())
