"""The per-book manifest (M23): one JSON file, a spine array in reading order, and an edition object."""

import json
from dataclasses import dataclass

CLASSES = ("body", "structural", "not-the-author")


@dataclass(frozen=True)
class Entry:
    href: str  # relative to content.opf, as written in the manifest
    cls: str
    chapter: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class Manifest:
    edition: dict
    spine: tuple[Entry, ...]


def load_manifest(path: str) -> Manifest:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    try:
        spine = tuple(
            Entry(href=e["href"], cls=e["class"], chapter=e.get("chapter"), reason=e.get("reason"))
            for e in data["spine"]
        )
        return Manifest(edition=data["edition"], spine=spine)
    except (KeyError, TypeError) as exc:
        raise ValueError(f"manifest {path} is malformed: {exc}") from None
