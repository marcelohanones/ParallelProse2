"""The two inputs of a run, read once. Every stage works on this snapshot, so a file that changes during a run cannot
make the artifact internally inconsistent (round 34). Paths are kept only for the error lines."""

from dataclasses import dataclass

from parallelprose2.ingest.errors import IngestError


@dataclass(frozen=True)
class Inputs:
    epub_path: str
    manifest_path: str
    epub: bytes
    manifest: bytes

    @classmethod
    def read(cls, epub_path: str, manifest_path: str) -> "Inputs":
        return cls(epub_path, manifest_path, _read(epub_path), _read(manifest_path))


def _read(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise IngestError("E-INPUT-MISSING", path) from None
