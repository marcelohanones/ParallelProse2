"""Slice 5 tests: Debord's printed numbers (D5) and the both-books proof (Augustine and Debord, no stop).

    PYTHONPATH=src python -m unittest discover -s tests
"""

import json
import os
import tempfile
import unittest

from parallelprose2.ingest.artifact import DESCRIPTOR, RECORDS, REPORT, build, verify, write
from parallelprose2.ingest.paragraphs import extract

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "raw")
AUGUSTINE_EPUB = os.path.join(RAW, "The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub")
AUGUSTINE_MANIFEST = os.path.join(REPO, "manifests", "augustine.json")
DEBORD_EPUB = os.path.join(RAW, "The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub")
DEBORD_MANIFEST = os.path.join(REPO, "manifests", "debord.json")


class PrintedNumbers(unittest.TestCase):
    def setUp(self):
        self.result = extract(DEBORD_EPUB, DEBORD_MANIFEST)

    def test_221_numbers_each_once_from_1_to_221(self):
        numbers = [p.printed_no for p in self.result.paragraphs if p.printed_no is not None]
        self.assertEqual(len(numbers), 221)
        self.assertEqual(sorted(numbers), list(range(1, 222)))

    def test_the_nine_epigraphs_have_no_number_and_are_the_quoted_paragraphs(self):
        unnumbered = [p for p in self.result.paragraphs if p.printed_no is None]
        self.assertEqual(len(unnumbered), 9)
        self.assertTrue(all(p.quoted for p in unnumbered))

    def test_146_is_kept_from_the_div_in_ch_5(self):
        paragraph = next(p for p in self.result.paragraphs if p.printed_no == 146)
        self.assertEqual(paragraph.href, "ch-5.html")
        self.assertTrue(paragraph.text.startswith("The irreversible time of production"))

    def test_augustine_has_no_printed_numbers(self):
        result = extract(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        self.assertTrue(all(p.printed_no is None for p in result.paragraphs))


class NonIntegerPrintedNumber(unittest.TestCase):
    """M43: a printed number that is not an integer stops as E-PRINTED-NUMBER-MALFORMED, with the href as the file."""

    def test_non_integer_h3_num_stops_with_the_href(self):
        import zipfile
        from parallelprose2.ingest.errors import IngestError
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "debord_bad_number.epub")
            with zipfile.ZipFile(DEBORD_EPUB) as src, zipfile.ZipFile(copy, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "ch-5.html":
                        data = data.replace(b'<h3 class="num" id="toc_22">146</h3>', b'<h3 class="num" id="toc_22">14a</h3>', 1)
                    dst.writestr(info, data)
            with self.assertRaises(IngestError) as caught:
                extract(copy, DEBORD_MANIFEST)
            self.assertEqual(caught.exception.error_line(), "E-PRINTED-NUMBER-MALFORMED file=ch-5.html")


class BothBooks(unittest.TestCase):
    def test_debord_builds_writes_and_verifies_twice_the_same(self):
        with tempfile.TemporaryDirectory() as d:
            first, second = os.path.join(d, "first"), os.path.join(d, "second")
            write(build(DEBORD_EPUB, DEBORD_MANIFEST), first)
            write(build(DEBORD_EPUB, DEBORD_MANIFEST), second)
            for name in (RECORDS, REPORT, DESCRIPTOR):
                with open(os.path.join(first, name), "rb") as a, open(os.path.join(second, name), "rb") as b:
                    self.assertEqual(a.read(), b.read(), name)
            self.assertEqual(verify(first, DEBORD_EPUB, DEBORD_MANIFEST), build(DEBORD_EPUB, DEBORD_MANIFEST).version_id)
            with open(os.path.join(first, RECORDS), "rb") as f:
                records = [json.loads(line) for line in f.read().splitlines()]
            self.assertEqual(len(records), 230)
            self.assertEqual(sum(r["printed_no"] is not None for r in records), 221)


if __name__ == "__main__":
    unittest.main()
