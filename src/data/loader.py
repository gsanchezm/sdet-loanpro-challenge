import json
from functools import lru_cache
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parents[2] / "tests" / "data" / "parametrize_data.json"


@lru_cache
def _all_datasets() -> dict:
    return json.loads(_DATA_FILE.read_text(encoding="utf-8"))


def load_dataset(name: str) -> list:
    return _all_datasets()[name]
