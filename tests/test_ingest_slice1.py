"""Slice 1 tests: dispatch, readers, phase 1 and phase 2, and the F1 stop. Run with:

    PYTHONPATH=src python -m unittest discover -s tests
"""

import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from parallelprose2.ingest.check import check_book
from parallelprose2.ingest.errors import IngestError

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "raw")
AUGUSTINE_EPUB = os.path.join(RAW, "The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub")
DEBORD_EPUB = os.path.join(RAW, "The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub")
AUGUSTINE_MANIFEST = os.path.join(REPO, "manifests", "augustine.json")
DEBORD_MANIFEST = os.path.join(REPO, "manifests", "debord.json")
F1_EPUB = os.path.join(REPO, "tests", "fixtures", "ingest", "f1.epub")
F1_MANIFEST = os.path.join(REPO, "tests", "fixtures", "ingest", "f1.manifest.json")


def stop_line(epub, manifest):
    """Return the error line of a stop, or fail the test if the run passes."""
    try:
        check_book(epub, manifest)
    except IngestError as exc:
        return exc.error_line()
    raise AssertionError("expected a stop, the run passed")


class F1Stop(unittest.TestCase):
    def test_body_file_without_chapter_stops_with_its_file_named(self):
        self.assertEqual(stop_line(F1_EPUB, F1_MANIFEST), "E-BODY-NO-CHAPTER file=ch_b.xhtml")

    def test_stop_is_the_same_on_a_second_run(self):
        first = stop_line(F1_EPUB, F1_MANIFEST)
        second = stop_line(F1_EPUB, F1_MANIFEST)
        self.assertEqual(first, second)


class Dispatch(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def _path(self, name):
        return os.path.join(self.dir.name, name)

    def test_four_random_bytes_are_refused_by_content(self):
        path = self._path("book.epub")
        with open(path, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        self.assertEqual(stop_line(path, F1_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")

    def test_zip_without_mimetype_is_refused_by_content(self):
        path = self._path("book.epub")
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("content.opf", "<package/>")
        self.assertEqual(stop_line(path, F1_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")

    def test_zip_with_wrong_mimetype_is_refused(self):
        path = self._path("book.epub")
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("mimetype", "text/plain")
            z.writestr("META-INF/container.xml", "<container/>")
        self.assertEqual(stop_line(path, F1_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")


class RealBooks(unittest.TestCase):
    def test_augustine_passes_phases_one_and_two(self):
        summary = check_book(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        self.assertEqual(summary.spine_count, 18)
        self.assertEqual(summary.class_counts, {"structural": 5, "body": 13})
        self.assertEqual([c.label for c in summary.chapters][:2], ["Book I", "Book II"])
        self.assertEqual(len(summary.chapters), 13)
        self.assertEqual(summary.chapters[-1].label, "Book XIII")

    def test_debord_passes_phases_one_and_two(self):
        summary = check_book(DEBORD_EPUB, DEBORD_MANIFEST)
        self.assertEqual(summary.spine_count, 15)
        self.assertEqual(summary.class_counts, {"structural": 5, "not-the-author": 1, "body": 9})
        self.assertEqual(len(summary.chapters), 9)
        self.assertEqual(summary.chapters[0].label, "1: The Culmination of Separation")
        self.assertEqual(summary.chapters[-1].label, "9: Ideology Materialized")

    def test_second_run_gives_the_same_summary(self):
        self.assertEqual(
            check_book(DEBORD_EPUB, DEBORD_MANIFEST),
            check_book(DEBORD_EPUB, DEBORD_MANIFEST),
        )


class Phase1Symmetry(unittest.TestCase):
    """Each direction of the classification check, on the real Augustine epub with a changed manifest."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        with open(AUGUSTINE_MANIFEST, encoding="utf-8") as f:
            self.base = json.load(f)

    def _manifest(self, spine):
        data = dict(self.base, spine=spine)
        path = os.path.join(self.dir.name, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_spine_item_absent_from_manifest(self):
        spine = [e for e in self.base["spine"] if e["href"] != "54_split_005.html"]
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertEqual(line, "E-SPINE-UNCLASSIFIED file=54_split_005.html")

    def test_manifest_entry_absent_from_spine(self):
        spine = self.base["spine"] + [{"href": "ghost.html", "class": "structural", "reason": "not in the epub"}]
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertEqual(line, "E-MANIFEST-ENTRY-NOT-IN-SPINE file=ghost.html")

    def test_manifest_order_differs_from_spine(self):
        spine = list(self.base["spine"])
        spine[5], spine[6] = spine[6], spine[5]
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertTrue(line.startswith("E-MANIFEST-ORDER-MISMATCH"), line)

    def test_duplicate_entry(self):
        spine = self.base["spine"] + [dict(self.base["spine"][5])]
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertTrue(line.startswith("E-MANIFEST-DUPLICATE-HREF"), line)

    def test_class_outside_the_three(self):
        spine = [dict(e) for e in self.base["spine"]]
        spine[1]["class"] = "unclassified"
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertTrue(line.startswith("E-MANIFEST-CLASS-INVALID"), line)


class NavPointStop(unittest.TestCase):
    """A body chapter whose navPoint is removed from toc.ncx stops in phase 2."""

    def test_chapter_without_navpoint_stops(self):
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "augustine_no_book_two.epub")
            with zipfile.ZipFile(AUGUSTINE_EPUB) as src, zipfile.ZipFile(copy, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename.endswith(".ncx"):
                        data = _drop_navpoint(data, "Book II")
                    dst.writestr(info, data)
            self.assertEqual(
                stop_line(copy, AUGUSTINE_MANIFEST),
                "E-CHAPTER-NO-NAVPOINT file=54_split_005.html chapter=book-02",
            )


def _drop_navpoint(ncx_bytes, label):
    root = ET.fromstring(ncx_bytes)
    nav_map = root.find("{*}navMap")
    for navpoint in list(nav_map.findall("{*}navPoint")):
        if navpoint.find("{*}navLabel/{*}text").text.strip() == label:
            nav_map.remove(navpoint)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    unittest.main()
