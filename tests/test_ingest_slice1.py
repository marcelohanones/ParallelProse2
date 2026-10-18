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

    def test_epub_renamed_to_pdf_gives_the_same_stop(self):
        path = self._path("book.pdf")
        with open(F1_EPUB, "rb") as src, open(path, "wb") as dst:
            dst.write(src.read())
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-BODY-NO-CHAPTER file=ch_b.xhtml")

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
        self.assertEqual(line, "E-MANIFEST-ORDER-MISMATCH file=54_split_005.html")

    def test_duplicate_entry(self):
        spine = self.base["spine"] + [dict(self.base["spine"][5])]
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertEqual(line, "E-MANIFEST-DUPLICATE-HREF file=54_split_004.html")

    def test_class_outside_the_three(self):
        spine = [dict(e) for e in self.base["spine"]]
        spine[1]["class"] = "unclassified"
        line = stop_line(AUGUSTINE_EPUB, self._manifest(spine))
        self.assertEqual(line, "E-MANIFEST-CLASS-INVALID file=54_split_000.html")


class SpineLength(unittest.TestCase):
    """A spine that repeats an item at the end is longer than the manifest: a stop at the extra item (M23, round 32)."""

    def test_repeated_last_spine_item_stops_at_the_extra_item(self):
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "augustine_repeated.epub")
            with zipfile.ZipFile(AUGUSTINE_EPUB) as src, zipfile.ZipFile(copy, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "content.opf":
                        data = data.replace(b"</spine>", b'<itemref idref="html1"/></spine>')
                    dst.writestr(info, data)
            self.assertEqual(
                stop_line(copy, AUGUSTINE_MANIFEST),
                "E-MANIFEST-ORDER-MISMATCH file=54_split_016.html",
            )


class PercentEncodedHref(unittest.TestCase):
    """An OPF href written with a percent-escape names the same zip member (URI reference, decoded)."""

    def test_encoded_opf_href_passes_like_the_plain_one(self):
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "augustine_encoded.epub")
            with zipfile.ZipFile(AUGUSTINE_EPUB) as src, zipfile.ZipFile(copy, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "content.opf":
                        data = data.replace(b'href="54_split_004.html"', b'href="54%5Fsplit_004.html"')
                    dst.writestr(info, data)
            summary = check_book(copy, AUGUSTINE_MANIFEST)
            self.assertEqual(len(summary.chapters), 13)
            self.assertEqual(summary.spine_count, 18)


class PackageStructure(unittest.TestCase):
    """Missing members and structural gaps in the package stop as E-PACKAGE-MALFORMED (M27, extended in round 32)."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def _copy(self, replace=None, skip=()):
        """Copy the F1 fixture: replace some members with new bytes, and leave out the ones in skip."""
        replace = replace or {}
        path = os.path.join(self.dir.name, "copy.epub")
        with zipfile.ZipFile(F1_EPUB) as src, zipfile.ZipFile(path, "w") as dst:
            for info in src.infolist():
                if info.filename in skip:
                    continue
                dst.writestr(info, replace.get(info.filename, src.read(info.filename)))
        return path

    def test_opf_named_by_container_is_missing(self):
        path = self._copy(skip={"content.opf"})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=content.opf")

    def test_ncx_named_by_opf_is_missing(self):
        path = self._copy(skip={"toc.ncx"})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=toc.ncx")

    def test_container_without_rootfile(self):
        path = self._copy(replace={"META-INF/container.xml": b"<container/>"})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=META-INF/container.xml")

    def test_opf_without_spine(self):
        path = self._copy(replace={"content.opf": b'<package xmlns="http://www.idpf.org/2007/opf"><manifest/></package>'})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=content.opf")

    def test_ncx_without_navmap(self):
        path = self._copy(replace={"toc.ncx": b'<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"/>'})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=toc.ncx")

    def test_navpoint_without_content(self):
        ncx = (b'<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"><navMap>'
               b'<navPoint id="x"><navLabel><text>A</text></navLabel></navPoint></navMap></ncx>')
        path = self._copy(replace={"toc.ncx": ncx})
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=toc.ncx")


class ManifestMalformed(unittest.TestCase):
    """A manifest that is not valid JSON or misses a required field stops as E-MANIFEST-MALFORMED (M28)."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        with open(AUGUSTINE_MANIFEST, encoding="utf-8") as f:
            self.base = json.load(f)

    def _write(self, data):
        path = os.path.join(self.dir.name, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        return path

    def test_not_json(self):
        path = self._write("{")
        self.assertEqual(stop_line(AUGUSTINE_EPUB, path), f"E-MANIFEST-MALFORMED file={path}")

    def test_spine_missing(self):
        path = self._write({"edition": self.base["edition"]})
        self.assertEqual(stop_line(AUGUSTINE_EPUB, path), f"E-MANIFEST-MALFORMED file={path}")

    def test_entry_without_class(self):
        spine = [dict(e) for e in self.base["spine"]]
        del spine[0]["class"]
        path = self._write(dict(self.base, spine=spine))
        self.assertEqual(stop_line(AUGUSTINE_EPUB, path), f"E-MANIFEST-MALFORMED file={path}")

    def test_structural_entry_without_reason(self):
        spine = [dict(e) for e in self.base["spine"]]
        del spine[1]["reason"]
        path = self._write(dict(self.base, spine=spine))
        self.assertEqual(stop_line(AUGUSTINE_EPUB, path), "E-MANIFEST-REASON-MISSING file=54_split_000.html")


F2_EPUB = os.path.join(REPO, "tests", "fixtures", "ingest", "f2.epub")
F2_MANIFEST = os.path.join(REPO, "tests", "fixtures", "ingest", "f2.manifest.json")


class F2Stop(unittest.TestCase):
    """F2 (committed bytes): chapter B has no navPoint, so the run stops in phase 2 with the chapter named."""

    def test_chapter_without_navpoint_stops_with_chapter_and_file_named(self):
        self.assertEqual(stop_line(F2_EPUB, F2_MANIFEST), "E-CHAPTER-NO-NAVPOINT file=ch_b.xhtml chapter=B")

    def test_stop_is_the_same_on_a_second_run(self):
        self.assertEqual(stop_line(F2_EPUB, F2_MANIFEST), stop_line(F2_EPUB, F2_MANIFEST))


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


class UnreadableInput(unittest.TestCase):
    """A missing path, and a container, OPF or NCX that is not well-formed XML (M27)."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def _copy_with(self, member, data):
        """Copy the F1 fixture into the temp dir with one member replaced."""
        path = os.path.join(self.dir.name, "copy.epub")
        with zipfile.ZipFile(F1_EPUB) as src, zipfile.ZipFile(path, "w") as dst:
            for info in src.infolist():
                dst.writestr(info, data if info.filename == member else src.read(info.filename))
        return path

    def test_missing_path(self):
        path = os.path.join(self.dir.name, "absent.epub")
        self.assertEqual(stop_line(path, F1_MANIFEST), f"E-INPUT-MISSING file={path}")

    def test_missing_manifest_path(self):
        path = os.path.join(self.dir.name, "absent.manifest.json")
        self.assertEqual(stop_line(F1_EPUB, path), f"E-INPUT-MISSING file={path}")

    def test_malformed_container(self):
        path = self._copy_with("META-INF/container.xml", b"<container")
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=META-INF/container.xml")

    def test_malformed_opf(self):
        path = self._copy_with("content.opf", b"<package")
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=content.opf")

    def test_malformed_ncx(self):
        path = self._copy_with("toc.ncx", b"<ncx")
        self.assertEqual(stop_line(path, F1_MANIFEST), "E-PACKAGE-MALFORMED file=toc.ncx")


def _drop_navpoint(ncx_bytes, label):
    root = ET.fromstring(ncx_bytes)
    nav_map = root.find("{*}navMap")
    for navpoint in list(nav_map.findall("{*}navPoint")):
        if navpoint.find("{*}navLabel/{*}text").text.strip() == label:
            nav_map.remove(navpoint)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    unittest.main()
