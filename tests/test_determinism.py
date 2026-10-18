"""Item 6 tests: determinism and artifact checks on both real books (the ledger's "Also required" list).

    PYTHONPATH=src python -m unittest discover -s tests
"""

import json
import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from parallelprose2.ingest.artifact import DESCRIPTOR, RECORDS, REPORT, build, verify, write
from parallelprose2.ingest.epub import open_epub, read_package, resolve_href
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.manifest import load_manifest
from parallelprose2.ingest.identity import content_hash, sha256_bytes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "raw")
BOOKS = {
    "augustine": (os.path.join(RAW, "The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub"),
                  os.path.join(REPO, "manifests", "augustine.json")),
    "debord": (os.path.join(RAW, "The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub"),
               os.path.join(REPO, "manifests", "debord.json")),
}


def _local(tag):
    return tag.split("}")[-1]


class TwoRuns(unittest.TestCase):
    def test_both_books_identical_bytes_and_identities_on_two_runs(self):
        for name, (epub, manifest) in BOOKS.items():
            with self.subTest(book=name), tempfile.TemporaryDirectory() as d:
                first, second = os.path.join(d, "a"), os.path.join(d, "b")
                write(build(epub, manifest), first)
                write(build(epub, manifest), second)
                for file in (RECORDS, REPORT, DESCRIPTOR):
                    with open(os.path.join(first, file), "rb") as x, open(os.path.join(second, file), "rb") as y:
                        self.assertEqual(x.read(), y.read(), file)
                with open(os.path.join(first, DESCRIPTOR), encoding="utf-8") as f:
                    a = json.load(f)
                with open(os.path.join(second, DESCRIPTOR), encoding="utf-8") as f:
                    b = json.load(f)
                self.assertEqual((a["version_id"], a["content_hash"]), (b["version_id"], b["content_hash"]))


class Refusals(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_augustine_artifact_against_debord_inputs_is_a_version_mismatch(self):
        (a_epub, a_manifest), (d_epub, d_manifest) = BOOKS["augustine"], BOOKS["debord"]
        out = os.path.join(self.dir.name, "augustine")
        write(build(a_epub, a_manifest), out)
        with self.assertRaises(IngestError) as caught:
            verify(out, d_epub, d_manifest)
        self.assertEqual(caught.exception.rule_id, "E-ARTIFACT-DIFFERENT-INPUT")

    def test_equal_version_id_with_unequal_content_hash_is_refused(self):
        epub, manifest = BOOKS["augustine"]
        out = os.path.join(self.dir.name, "tampered")
        write(build(epub, manifest), out)
        path = os.path.join(out, RECORDS)
        with open(path, "rb") as f:
            lines = f.read().splitlines()
        record = json.loads(lines[0])
        record["text"] = record["text"] + " (changed)"
        lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        with open(path, "wb") as f:
            f.write(b"\n".join(lines) + b"\n")
        with open(os.path.join(out, DESCRIPTOR), encoding="utf-8") as f:
            descriptor = json.load(f)
        for entry in descriptor["files"]:
            if entry["name"] == RECORDS:
                with open(path, "rb") as f:
                    entry["sha256"] = sha256_bytes(f.read())
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        with open(os.path.join(out, DESCRIPTOR), "w", encoding="utf-8") as f:
            json.dump(descriptor, f, sort_keys=True, indent=2, ensure_ascii=False)
            f.write("\n")
        with self.assertRaises(IngestError) as caught:
            verify(out, epub, manifest)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-CONTENT-MISMATCH file={RECORDS} record=1")


class FrontMatterAndHeadings(unittest.TestCase):
    """No text of a non-body spine item, and no heading text of a body file, appears as a record's text."""

    def _texts(self, epub, manifest_path):
        with open(manifest_path, "rb") as f:
            manifest = load_manifest(f.read(), manifest_path)
        front, headings = set(), set()
        with open(epub, "rb") as f:
            epub_bytes = f.read()
        with open_epub(epub_bytes, epub) as z:
            package = read_package(z)
            by_path = {resolve_href(package.opf_dir, e.href): e for e in manifest.spine}
            for path in package.spine:
                root = ET.fromstring(z.read(path))
                body = next(el for el in root.iter() if _local(el.tag) == "body")
                if by_path[path].cls != "body":
                    front.update(t.strip() for t in body.itertext() if t.strip())
                else:
                    for el in body.iter():
                        if _local(el.tag) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                            whole = " ".join("".join(el.itertext()).split())  # the whole heading, inline children included
                            if whole:
                                headings.add(whole)
        return front, headings

    def test_no_record_is_front_matter_or_a_heading(self):
        for name, (epub, manifest) in BOOKS.items():
            with self.subTest(book=name):
                front, headings = self._texts(epub, manifest)
                with tempfile.TemporaryDirectory() as d:
                    write(build(epub, manifest), os.path.join(d, "out"))
                    with open(os.path.join(d, "out", RECORDS), "rb") as f:
                        texts = [json.loads(line)["text"] for line in f.read().splitlines()]
                self.assertFalse(set(texts) & front, "front matter text in the records")
                self.assertFalse(set(texts) & headings, "heading text in the records")


class ReportRows(unittest.TestCase):
    """The report's non-body rows are pinned by href and class, and their reasons are the manifest's reasons."""

    EXPECTED = {
        "augustine": [
            ("titlepage.xhtml", "structural"),
            ("54_split_000.html", "structural"),
            ("54_split_001.html", "structural"),
            ("54_split_002.html", "structural"),
            ("54_split_003.html", "structural"),
        ],
        "debord": [
            ("titlepage.xhtml", "structural"),
            ("half.html", "structural"),
            ("title.html", "structural"),
            ("contents.html", "structural"),
            ("note.html", "not-the-author"),
            ("index.html", "structural"),
        ],
    }

    def test_report_lists_every_non_body_item_with_class_and_reason_and_the_dropped_p(self):
        for name, (epub, manifest) in BOOKS.items():
            with self.subTest(book=name), tempfile.TemporaryDirectory() as d:
                write(build(epub, manifest), os.path.join(d, "out"))
                with open(os.path.join(d, "out", REPORT), encoding="utf-8") as f:
                    lines = f.read().splitlines()
                with open(manifest, encoding="utf-8") as f:
                    reasons = {e["href"]: e.get("reason") for e in json.load(f)["spine"]}
                spine = [line.split("\t") for line in lines if line.startswith("spine\t")]
                non_body = [(row[1], row[2], row[4]) for row in spine if row[2] != "body"]
                self.assertEqual([(href, cls) for href, cls, _ in non_body], self.EXPECTED[name])
                self.assertTrue(all(reason == reasons[href] for href, _, reason in non_body), "a reason differs from the manifest")
                dropped = [line for line in lines if line.startswith("dropped\t")]
                self.assertEqual(len(dropped), 1)


if __name__ == "__main__":
    unittest.main()
