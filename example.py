import asyncio

import click
from rich import print

from aioytt.transcript import get_transcript_from_url


@click.command()
@click.argument("url", type=click.STRING)
async def main(url: str) -> None:
    transcript = await get_transcript_from_url(url)
    for snippet in transcript:
        print(snippet)


if __name__ == "__main__":
    asyncio.run(main())
