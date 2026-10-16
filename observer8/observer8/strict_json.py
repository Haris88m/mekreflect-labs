from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any


class StrictJSONError(ValueError):
    """Raised when a value cannot be represented as finite, standard JSON."""


def _reject_constant(token: str) -> None:
    raise StrictJSONError(f"non-standard JSON numeric token: {token}")


def ensure_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise StrictJSONError(f"non-finite number at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise StrictJSONError(f"non-string object key at {path}")
            ensure_finite(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            ensure_finite(item, f"{path}[{index}]")


def loads(text: str | bytes) -> Any:
    try:
        value = json.loads(text, parse_constant=_reject_constant)
    except StrictJSONError:
        raise
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrictJSONError(str(exc)) from exc
    ensure_finite(value)
    return value


def load(path: Path | str) -> Any:
    return loads(Path(path).read_bytes())


def dumps(value: Any, *, indent: int | None = None, sort_keys: bool = True) -> str:
    ensure_finite(value)
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            indent=indent,
            separators=None if indent is not None else (",", ":"),
            sort_keys=sort_keys,
        )
    except (TypeError, ValueError) as exc:
        raise StrictJSONError(str(exc)) from exc


def canonical_bytes(value: Any) -> bytes:
    return dumps(value, sort_keys=True).encode("utf-8")


def atomic_dump(path: Path | str, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".tmp")
    temp.write_text(dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temp, destination)
