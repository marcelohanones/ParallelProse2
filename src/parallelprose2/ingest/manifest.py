"""The per-book manifest (M23): one JSON file, a spine array in reading order, and an edition object."""

import json
from dataclasses import dataclass

from parallelprose2.ingest.errors import IngestError

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


def load_manifest(raw: bytes, path: str) -> Manifest:
    """Parse the manifest bytes. A missing file is the caller's E-INPUT-MISSING; anything else that is not a manifest is
    E-MANIFEST-MALFORMED. `path` is the error locator."""
    try:
        data = json.loads(raw.decode("utf-8"))
    except ValueError:
        raise IngestError("E-MANIFEST-MALFORMED", path) from None
    try:
        spine = tuple(
            Entry(href=e["href"], cls=e["class"], chapter=e.get("chapter"), reason=e.get("reason"))
            for e in data["spine"]
        )
        return Manifest(edition=data["edition"], spine=spine)
    except (KeyError, TypeError):
        raise IngestError("E-MANIFEST-MALFORMED", path) from None
