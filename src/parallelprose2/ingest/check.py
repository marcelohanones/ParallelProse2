"""Check phases 1 and 2 for one book (M18). Writes nothing: a stop raises, and a pass returns a summary.

Error ids marked provisional are not in M24; they name the manifest checks that M24 does not cover, and wait for a
decision before the ledger records them.
"""

from dataclasses import dataclass

from parallelprose2.ingest.epub import open_epub, read_package, resolve_href
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.manifest import CLASSES, load_manifest


@dataclass(frozen=True)
class Chapter:
    chapter: str
    label: str
    files: tuple[str, ...]


@dataclass(frozen=True)
class BookSummary:
    spine_count: int
    class_counts: dict
    chapters: tuple[Chapter, ...]


def check_book(epub_path: str, manifest_path: str) -> BookSummary:
    manifest = load_manifest(manifest_path)
    with open_epub(epub_path) as z:
        package = read_package(z)
    manifest_paths = [(resolve_href(package.opf_dir, e.href), e) for e in manifest.spine]
    check_classification(package.spine, manifest_paths)
    return check_chapters(package.spine, package.navpoints, manifest_paths)


def check_classification(spine: tuple[str, ...], manifest_paths: list) -> None:
    """Phase 1: every spine item classified, every entry in the spine, every class valid, in the same order."""
    seen = set()
    for path, entry in manifest_paths:  # provisional: duplicate entry
        if path in seen:
            raise IngestError("E-MANIFEST-DUPLICATE-HREF", path)
        seen.add(path)
    listed = {path for path, _ in manifest_paths}
    for path in spine:
        if path not in listed:
            raise IngestError("E-SPINE-UNCLASSIFIED", path)
    in_spine = set(spine)
    for path, _ in manifest_paths:
        if path not in in_spine:
            raise IngestError("E-MANIFEST-ENTRY-NOT-IN-SPINE", path)
    for path, entry in manifest_paths:  # provisional: class outside the three
        if entry.cls not in CLASSES:
            raise IngestError("E-MANIFEST-CLASS-INVALID", path)
    for position, (path, _) in enumerate(manifest_paths):  # provisional: order differs from the spine
        if path != spine[position]:
            raise IngestError("E-MANIFEST-ORDER-MISMATCH", path)


def check_chapters(spine, navpoints, manifest_paths) -> BookSummary:
    """Phase 2: every body file has a chapter id, then every chapter has a navPoint (M6, M8, M16)."""
    by_path = {path: entry for path, entry in manifest_paths}
    ordered = [(path, by_path[path]) for path in spine]

    for path, entry in ordered:
        if entry.cls == "body" and entry.chapter is None:
            raise IngestError("E-BODY-NO-CHAPTER", path)

    chapters: dict[str, list[str]] = {}
    for path, entry in ordered:
        if entry.cls == "body":
            chapters.setdefault(entry.chapter, []).append(path)

    label_of: dict[str, str] = {}
    for label, target in navpoints:
        label_of.setdefault(target, label)

    result = []
    for chapter_id, files in chapters.items():
        label = next((label_of[f] for f in files if f in label_of), None)
        if label is None:
            raise IngestError("E-CHAPTER-NO-NAVPOINT", files[0], chapter=chapter_id)
        result.append(Chapter(chapter=chapter_id, label=label, files=tuple(files)))

    class_counts: dict[str, int] = {}
    for _, entry in ordered:
        class_counts[entry.cls] = class_counts.get(entry.cls, 0) + 1
    return BookSummary(spine_count=len(spine), class_counts=class_counts, chapters=tuple(result))
