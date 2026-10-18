"""Slice 4d tests: the Augustine fixture set (F5 B and C as bytes; F5 A as the F3 rename; F6, F6b, F11 as bytes), and the
twice rule (M17) for every committed fixture. Run with:

    PYTHONPATH=src python -m unittest discover -s tests
"""

import os
import shutil
import tempfile
import unittest

from parallelprose2.ingest.artifact import DESCRIPTOR, RECORDS, REPORT, build, verify, write
from parallelprose2.ingest.check import check_book
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.paragraphs import extract

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(REPO, "tests", "fixtures", "ingest")
MANIFESTS = os.path.join(REPO, "manifests")


def fx(name):
    return os.path.join(FIXTURES, name)


F3_EPUB, F3_MANIFEST = fx("f3.epub"), fx("f3.manifest.json")


def stop_line(epub, manifest):
    try:
        check_book(epub, manifest)
    except IngestError as exc:
        return exc.error_line()
    raise AssertionError("expected a stop, the run passed")


class F5(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_a_renamed_to_pdf_gives_the_same_artifact_bytes(self):
        renamed = os.path.join(self.dir.name, "book.pdf")
        shutil.copyfile(F3_EPUB, renamed)
        for run in ("first", "second"):
            original_out = os.path.join(self.dir.name, f"original-{run}")
            renamed_out = os.path.join(self.dir.name, f"renamed-{run}")
            write(build(F3_EPUB, F3_MANIFEST), original_out)
            write(build(renamed, F3_MANIFEST), renamed_out)
            for name in (RECORDS, REPORT, DESCRIPTOR):
                with open(os.path.join(original_out, name), "rb") as a, open(os.path.join(renamed_out, name), "rb") as b:
                    self.assertEqual(a.read(), b.read(), f"{name} differs on the {run} run")
            self.assertEqual(verify(renamed_out, renamed, F3_MANIFEST), build(F3_EPUB, F3_MANIFEST).version_id)

    def test_b_no_mimetype_zip_stops_by_content_twice(self):
        path = fx("f5_b.epub")
        self.assertEqual(stop_line(path, F3_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")
        self.assertEqual(stop_line(path, F3_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")

    def test_c_four_bytes_stop_by_content_twice(self):
        path = fx("f5_c.epub")
        self.assertEqual(stop_line(path, F3_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")
        self.assertEqual(stop_line(path, F3_MANIFEST), f"E-INPUT-NOT-EPUB file={path}")


class F6(unittest.TestCase):
    def test_unclassified_spine_item_stops_in_phase_one_twice(self):
        epub, manifest = fx("f6.epub"), fx("f6.manifest.json")
        self.assertEqual(stop_line(epub, manifest), "E-SPINE-UNCLASSIFIED file=ch_c.xhtml")
        self.assertEqual(stop_line(epub, manifest), "E-SPINE-UNCLASSIFIED file=ch_c.xhtml")


class F6b(unittest.TestCase):
    def test_manifest_entry_not_in_spine_stops_twice(self):
        epub, manifest = fx("f6b.epub"), fx("f6b.manifest.json")
        self.assertEqual(stop_line(epub, manifest), "E-MANIFEST-ENTRY-NOT-IN-SPINE file=ch_d.xhtml")
        self.assertEqual(stop_line(epub, manifest), "E-MANIFEST-ENTRY-NOT-IN-SPINE file=ch_d.xhtml")


class F11(unittest.TestCase):
    """M16: the label comes from the navPoint on the second file; one chapter; spine order kept; no stop."""

    def test_one_chapter_labelled_from_the_second_file_no_stop(self):
        epub, manifest = fx("f11.epub"), fx("f11.manifest.json")
        rows = [(p.index, p.chapter, p.chapter_seq, p.text) for p in extract(epub, manifest).paragraphs]
        self.assertEqual(rows, [
            (1, "First chapter", 1, "Z one."),
            (2, "First chapter", 2, "Z two."),
            (3, "First chapter", 3, "A one."),
            (4, "First chapter", 4, "A two."),
        ])

    def test_second_run_is_the_same(self):
        epub, manifest = fx("f11.epub"), fx("f11.manifest.json")
        self.assertEqual(extract(epub, manifest), extract(epub, manifest))


class TwiceRule(unittest.TestCase):
    """M17: every committed fixture runs twice with the same output."""

    def test_committed_extraction_fixtures_run_twice_the_same(self):
        for name in ("f3", "f4", "f7", "f10", "f12"):
            epub, manifest = fx(f"{name}.epub"), fx(f"{name}.manifest.json")
            self.assertEqual(extract(epub, manifest), extract(epub, manifest), name)


if __name__ == "__main__":
    unittest.main()
