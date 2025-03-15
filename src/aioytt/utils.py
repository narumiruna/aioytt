import json
from pathlib import Path
from typing import Any


def save_json(obj: Any, f: str | Path) -> None:
    with Path(f).open("w") as fp:
        json.dump(obj, fp, indent=4, ensure_ascii=False)
