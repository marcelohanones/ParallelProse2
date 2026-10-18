"""The artifact (4c): records, report and descriptor, written atomically and verified by recomputation (M5–M22).

Every stage works on one Inputs snapshot (round 34). Build runs every check before anything is written, so a stop leaves
no file. Writing uses temporaries unique to the run (M21) and renames them in a fixed order: records, report, and the
descriptor last, which is the commit point. Verification recomputes every file's sha256 from disk and never trusts the
stored content_hash (M20).
"""

import json
import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from parallelprose2.ingest.check import check_inputs
from parallelprose2.ingest.epub import open_epub, read_package, resolve_href
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.identity import canonical, content_hash, sha256_bytes, version_id_of
from parallelprose2.ingest.inputs import Inputs
from parallelprose2.ingest.manifest import load_manifest
from parallelprose2.ingest.paragraphs import _read_body, extract_inputs

RECORDS = "records.jsonl"
REPORT = "report.txt"
DESCRIPTOR = "descriptor.json"
SKIPPED_TEXT = {"script", "style"}  # M11: script and style text is not words


@dataclass(frozen=True)
class Built:
    version_id: str
    records: bytes
    report: bytes
    descriptor: bytes


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _text(el: ET.Element) -> list[str]:
    """The text nodes of el in document order, without script and style subtrees."""
    if _local(el.tag) in SKIPPED_TEXT:
        return []
    pieces = [el.text or ""]
    for child in el:
        pieces.extend(_text(child))
        pieces.append(child.tail or "")
    return pieces


def word_count(body: ET.Element) -> int:
    """M11: text nodes separated by one space at each element boundary; tokens with a letter or digit."""
    tokens = " ".join(_text(body)).split()
    return sum(1 for token in tokens if any(c.isalnum() for c in token))


def spine_rows_inputs(inp: Inputs) -> tuple:
    """One row per spine item, in spine order: (href, class, word count, chapter id or reason)."""
    manifest = load_manifest(inp.manifest, inp.manifest_path)
    rows = []
    with open_epub(inp.epub, inp.epub_path) as z:
        package = read_package(z)
        by_path = {resolve_href(package.opf_dir, e.href): e for e in manifest.spine}
        for path in package.spine:
            entry = by_path[path]
            label = entry.chapter if entry.cls == "body" else entry.reason
            rows.append((path, entry.cls, word_count(_read_body(z, path)), label))
    return tuple(rows)


def spine_rows(epub_path: str, manifest_path: str) -> tuple:
    return spine_rows_inputs(Inputs.read(epub_path, manifest_path))


def build(epub_path: str, manifest_path: str) -> Built:
    return build_inputs(Inputs.read(epub_path, manifest_path))


def build_inputs(inp: Inputs) -> Built:
    """Run every check and produce the three files in memory. Writes nothing."""
    extraction = extract_inputs(inp)  # runs phases 1–2 first
    vid = version_id_of(inp.epub, inp.manifest)
    records = b"".join(
        canonical({
            "chapter": p.chapter,
            "chapter_seq": p.chapter_seq,
            "index": p.index,
            "printed_no": None,
            "quoted": p.quoted,
            "source": p.source,
            "text": p.text,
            "version_id": vid,
        }) + b"\n"
        for p in extraction.paragraphs
    )
    lines = [
        f"manifest-sha256\t{sha256_bytes(inp.manifest)}",
        f"version-id\t{vid}",
        f"paragraphs\t{len(extraction.paragraphs)}",
    ]
    lines += [f"spine\t{href}\t{cls}\t{words}\t{label or '-'}" for href, cls, words, label in spine_rows_inputs(inp)]
    lines += [f"dropped\t{d.href}\t{d.position}" for d in extraction.dropped]
    report = ("\n".join(lines) + "\n").encode("utf-8")
    files = {RECORDS: sha256_bytes(records), REPORT: sha256_bytes(report)}
    descriptor = {
        "version_id": vid,
        "files": [{"name": name, "sha256": files[name]} for name in sorted(files)],
        "content_hash": content_hash(files),
    }
    return Built(
        version_id=vid,
        records=records,
        report=report,
        descriptor=(json.dumps(descriptor, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    )


def write(built: Built, out_dir: str) -> None:
    """Write the three files: temporaries first, then renames, the descriptor last (M15, M21)."""
    os.makedirs(out_dir, exist_ok=True)
    temporaries = {}
    for name, data in ((RECORDS, built.records), (REPORT, built.report), (DESCRIPTOR, built.descriptor)):
        fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=f".{name}.", suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        temporaries[name] = tmp
    for name in (RECORDS, REPORT, DESCRIPTOR):
        os.replace(temporaries[name], os.path.join(out_dir, name))


def _read_file(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise IngestError("E-ARTIFACT-INCOMPLETE", path) from None  # M32


def verify(artifact_dir: str, epub_path: str, manifest_path: str) -> str:
    """Refuse unless the artifact is what the inputs produce. Returns the version_id on success."""
    inp = Inputs.read(epub_path, manifest_path)
    descriptor_path = os.path.join(artifact_dir, DESCRIPTOR)
    raw_descriptor = _read_file(descriptor_path)
    try:
        descriptor = json.loads(raw_descriptor.decode("utf-8"))
        vid = descriptor["version_id"]
        stored = {entry["name"]: entry["sha256"] for entry in descriptor["files"]}
        stored_content_hash = descriptor["content_hash"]
    except (ValueError, KeyError, TypeError):
        raise IngestError("E-ARTIFACT-MALFORMED", descriptor_path) from None  # M32
    if len(descriptor["files"]) != 2 or set(stored) != {RECORDS, REPORT}:  # M35
        raise IngestError("E-ARTIFACT-MALFORMED", descriptor_path)

    records_path = os.path.join(artifact_dir, RECORDS)
    report_path = os.path.join(artifact_dir, REPORT)
    # Each artifact file is read once; the bytes read here are the ones hashed and parsed.
    files = {}
    for name in sorted(set(stored) | {RECORDS, REPORT}):
        files[name] = _read_file(os.path.join(artifact_dir, name))
    stored_records = files[RECORDS]
    stored_report = files[REPORT]
    recomputed = {name: sha256_bytes(data) for name, data in files.items()}

    if version_id_of(inp.epub, inp.manifest) != vid:
        raise IngestError("E-ARTIFACT-DIFFERENT-INPUT", artifact_dir)
    for number, line in enumerate(stored_records.splitlines(), start=1):
        try:
            record_vid = json.loads(line)["version_id"]
        except (ValueError, KeyError, TypeError):
            raise IngestError("E-ARTIFACT-MALFORMED", RECORDS, record=number) from None  # M32
        if record_vid != vid:
            raise IngestError("E-ARTIFACT-IDENTITY-MISMATCH", RECORDS, record=number)
    try:
        report_text = stored_report.decode("utf-8")
    except UnicodeDecodeError:
        raise IngestError("E-ARTIFACT-MALFORMED", report_path) from None
    report_vids = [line.split("\t", 1)[1] for line in report_text.splitlines() if line.startswith("version-id\t")]
    if report_vids != [vid]:
        raise IngestError("E-ARTIFACT-IDENTITY-MISMATCH", REPORT)

    # M34: always rebuild from the inputs and compare every byte; a consistent edit of any file is then a mismatch.
    fresh = build_inputs(inp)
    fresh_records = fresh.records.splitlines()
    stored_lines = stored_records.splitlines()
    for number, (old, new) in enumerate(zip(stored_lines, fresh_records), start=1):
        if old != new:
            raise IngestError("E-ARTIFACT-CONTENT-MISMATCH", RECORDS, record=number)
    if len(stored_lines) != len(fresh_records):
        raise IngestError("E-ARTIFACT-CONTENT-MISMATCH", RECORDS, record=min(len(stored_lines), len(fresh_records)) + 1)
    if stored_report != fresh.report:
        raise IngestError("E-ARTIFACT-CONTENT-MISMATCH", REPORT)
    if recomputed != stored or content_hash(recomputed) != stored_content_hash:
        raise IngestError("E-ARTIFACT-CONTENT-MISMATCH", descriptor_path)
    return vid
