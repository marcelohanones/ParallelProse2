"""Slice 4b tests: paragraphs and addresses (D6, M14), on the real books and on the committed fixtures F3, F4, F10.

    PYTHONPATH=src python -m unittest discover -s tests
"""

import os
import tempfile
import unittest
import zipfile

from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.paragraphs import extract

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "raw")
AUGUSTINE_EPUB = os.path.join(RAW, "The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub")
DEBORD_EPUB = os.path.join(RAW, "The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub")
AUGUSTINE_MANIFEST = os.path.join(REPO, "manifests", "augustine.json")
DEBORD_MANIFEST = os.path.join(REPO, "manifests", "debord.json")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "ingest")


def fixture(name):
    return os.path.join(FIXTURES, f"{name}.epub"), os.path.join(FIXTURES, f"{name}.manifest.json")


def rows(extraction):
    return [(p.index, p.chapter, p.chapter_seq, p.text) for p in extraction.paragraphs]


class Augustine(unittest.TestCase):
    def test_460_paragraphs_with_addresses_1_to_460(self):
        result = extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        self.assertEqual(len(result.paragraphs), 460)
        self.assertEqual([p.index for p in result.paragraphs], list(range(1, 461)))

    def test_the_one_empty_p_is_dropped_and_listed(self):
        result = extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        self.assertEqual([(d.href, d.position) for d in result.dropped], [("54_split_016.html", 54)])

    def test_chapter_seq_restarts_per_chapter(self):
        result = extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        first = [p for p in result.paragraphs if p.chapter == "Book I"]
        self.assertEqual([p.chapter_seq for p in first], list(range(1, len(first) + 1)))
        self.assertEqual(result.paragraphs[-1].chapter, "Book XIII")

    def test_second_run_is_identical(self):
        self.assertEqual(extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST), extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST))


class Debord(unittest.TestCase):
    def test_230_paragraphs_with_9_quoted_and_their_sources(self):
        result = extract(DEBORD_EPUB, DEBORD_MANIFEST)
        self.assertEqual(len(result.paragraphs), 230)
        self.assertEqual(sum(p.quoted for p in result.paragraphs), 9)
        self.assertEqual(sum(p.source is not None for p in result.paragraphs), 9)

    def test_the_empty_p_in_ch_7_is_dropped_and_listed(self):
        result = extract(DEBORD_EPUB, DEBORD_MANIFEST)
        self.assertEqual([(d.href, d.position) for d in result.dropped], [("ch-7.html", 18)])


class BodyStops(unittest.TestCase):
    """Stops at the body read (M27 body members, M30): a copy of F3 with one body file broken or missing."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def _copy(self, replace=None, skip=()):
        replace = replace or {}
        epub, manifest = fixture("f3")
        path = os.path.join(self.dir.name, "copy.epub")
        with zipfile.ZipFile(epub) as src, zipfile.ZipFile(path, "w") as dst:
            for info in src.infolist():
                if info.filename in skip:
                    continue
                dst.writestr(info, replace.get(info.filename, src.read(info.filename)))
        return path, manifest

    def _stop(self, path, manifest):
        with self.assertRaises(IngestError) as caught:
            extract(path, manifest)
        return caught.exception.error_line()

    def test_body_file_not_well_formed(self):
        path, manifest = self._copy(replace={"ch_a_z.xhtml": b"<html><body><p>unclosed</body></html>"})
        self.assertEqual(self._stop(path, manifest), "E-XHTML-MALFORMED file=ch_a_z.xhtml")

    def test_body_file_without_body(self):
        path, manifest = self._copy(replace={"ch_a_z.xhtml": b'<html xmlns="http://www.w3.org/1999/xhtml"><head/></html>'})
        self.assertEqual(self._stop(path, manifest), "E-XHTML-MALFORMED file=ch_a_z.xhtml")

    def test_body_member_the_zip_lacks(self):
        path, manifest = self._copy(skip={"ch_a_z.xhtml"})
        self.assertEqual(self._stop(path, manifest), "E-PACKAGE-MALFORMED file=ch_a_z.xhtml")


class Fixtures(unittest.TestCase):
    def test_f3_one_chapter_over_two_files_keeps_spine_order(self):
        epub, manifest = fixture("f3")
        self.assertEqual(rows(extract(epub, manifest)), [
            (1, "First chapter", 1, "Z one."),
            (2, "First chapter", 2, "Z two."),
            (3, "First chapter", 3, "Z three."),
            (4, "First chapter", 4, "A one."),
            (5, "First chapter", 5, "A two."),
            (6, "First chapter", 6, "A three."),
            (7, "Second chapter", 1, "B one."),
            (8, "Second chapter", 2, "B two."),
        ])

    def test_f4_nested_blocks_no_duplicates_no_loss_in_document_order(self):
        epub, manifest = fixture("f4")
        self.assertEqual([text for _, _, _, text in rows(extract(epub, manifest))], [
            "Text one.", "Text two.", "Text three.", "Text four.", "Text five.", "Text six.", "Text seven.",
        ])
        self.assertEqual([seq for _, _, seq, _ in rows(extract(epub, manifest))], list(range(1, 8)))

    def test_f10_normalization_breaks_become_spaces_and_runs_collapse(self):
        epub, manifest = fixture("f10")
        self.assertEqual(rows(extract(epub, manifest)), [(1, "Chapter A", 1, "Line one. Line two. Line three.")])


class MoreFixtures(unittest.TestCase):
    def test_f7_one_paragraph_and_the_empty_p_listed_the_empty_wrapper_silent(self):
        epub, manifest = fixture("f7")
        result = extract(epub, manifest)
        self.assertEqual(rows(result), [(1, "Chapter A", 1, "One text paragraph.")])
        self.assertEqual([(d.href, d.position) for d in result.dropped], [("ch_a.xhtml", 2)])

    def test_f12_inline_element_boundary_keeps_the_text_as_written(self):
        epub, manifest = fixture("f12")
        self.assertEqual(rows(extract(epub, manifest)),
                         [(1, "Chapter A", 1, "The Society of the Spectacle(La Soci\u00e9t\u00e9 du spectacle)")])


if __name__ == "__main__":
    unittest.main()
