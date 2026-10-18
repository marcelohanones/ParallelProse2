"""Slice 4c tests: the artifact, its identity, and its verification (M5–M22).

    PYTHONPATH=src python -m unittest discover -s tests
"""

import json
import os
import shutil
import tempfile
import unittest
import zipfile
from unittest import mock

from parallelprose2.ingest import identity
from parallelprose2.ingest.artifact import DESCRIPTOR, RECORDS, REPORT, build, spine_rows, verify, write
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.identity import canonical, content_hash, sha256_bytes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "raw")
AUGUSTINE_EPUB = os.path.join(RAW, "The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub")
AUGUSTINE_MANIFEST = os.path.join(REPO, "manifests", "augustine.json")
DEBORD_EPUB = os.path.join(RAW, "The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub")
DEBORD_MANIFEST = os.path.join(REPO, "manifests", "debord.json")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "ingest")
F1_EPUB = os.path.join(FIXTURES, "f1.epub")
F1_MANIFEST = os.path.join(FIXTURES, "f1.manifest.json")
F7_EPUB = os.path.join(FIXTURES, "f7.epub")
F7_MANIFEST = os.path.join(FIXTURES, "f7.manifest.json")
F12_EPUB = os.path.join(FIXTURES, "f12.epub")
F12_MANIFEST = os.path.join(FIXTURES, "f12.manifest.json")


class TempCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def path(self, *parts):
        return os.path.join(self.dir.name, *parts)

    def make_f7(self, name="artifact"):
        out = self.path(name)
        write(build(F7_EPUB, F7_MANIFEST), out)
        return out

    def read(self, out, name):
        with open(os.path.join(out, name), "rb") as f:
            return f.read()

    def write_bytes(self, out, name, data):
        with open(os.path.join(out, name), "wb") as f:
            f.write(data)

    def descriptor(self, out):
        return json.loads(self.read(out, DESCRIPTOR))

    def save_descriptor(self, out, descriptor):
        self.write_bytes(out, DESCRIPTOR, (json.dumps(descriptor, sort_keys=True, indent=2) + "\n").encode("utf-8"))


class TwoRuns(TempCase):
    def test_augustine_two_runs_are_byte_identical(self):
        first, second = self.path("first"), self.path("second")
        write(build(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST), first)
        write(build(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST), second)
        for name in (RECORDS, REPORT, DESCRIPTOR):
            self.assertEqual(self.read(first, name), self.read(second, name), name)

    def test_augustine_records_are_460_and_carry_the_version_id(self):
        out = self.path("augustine")
        built = build(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)
        write(built, out)
        lines = self.read(out, RECORDS).splitlines()
        self.assertEqual(len(lines), 460)
        self.assertEqual({json.loads(line)["version_id"] for line in lines}, {built.version_id})
        self.assertEqual([json.loads(line)["index"] for line in lines], list(range(1, 461)))
        self.assertEqual(json.loads(lines[0])["printed_no"], None)

    def test_augustine_report_lists_the_dropped_p(self):
        report = build(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST).report.decode("utf-8")
        self.assertIn("dropped\t54_split_016.html\t54", report.splitlines())


class WordCounts(unittest.TestCase):
    """The published figures (ledger, Report): each must reproduce under M11."""

    def test_debord_published_counts(self):
        counts = {row[0]: row[2] for row in spine_rows(DEBORD_EPUB, DEBORD_MANIFEST)}
        self.assertEqual(
            {k: counts[k] for k in ["note.html", "contents.html", "index.html", "title.html", "half.html", "titlepage.xhtml"]},
            {"note.html": 271, "contents.html": 57, "index.html": 363, "title.html": 24, "half.html": 7, "titlepage.xhtml": 0},
        )

    def test_augustine_published_counts(self):
        counts = {row[0]: row[2] for row in spine_rows(AUGUSTINE_EPUB, AUGUSTINE_MANIFEST)}
        self.assertEqual(counts["54_split_000.html"], 12)
        self.assertEqual(counts["titlepage.xhtml"], 0)

    def test_f12_inline_boundary_is_nine_tokens(self):
        self.assertEqual({row[0]: row[2] for row in spine_rows(F12_EPUB, F12_MANIFEST)}, {"ch_a.xhtml": 9})


class F7Report(TempCase):
    def test_rows_and_dropped_position(self):
        self.assertEqual(spine_rows(F7_EPUB, F7_MANIFEST), (
            ("cover.xhtml", "structural", 3, "cover, no prose"),
            ("note.xhtml", "not-the-author", 11, "translator's note, excluded"),
            ("ch_a.xhtml", "body", 5, "A"),
        ))
        report = build(F7_EPUB, F7_MANIFEST).report.decode("utf-8").splitlines()
        self.assertIn("dropped\tch_a.xhtml\t2", report)

    def test_written_artifact_verifies(self):
        out = self.make_f7()
        self.assertEqual(verify(out, F7_EPUB, F7_MANIFEST), build(F7_EPUB, F7_MANIFEST).version_id)


class Stops(TempCase):
    def test_a_stop_writes_nothing(self):
        out = self.path("never")
        with self.assertRaises(IngestError):
            build(F1_EPUB, F1_MANIFEST)  # F1 stops in phase 2; build never reaches write
        self.assertFalse(os.path.exists(out))

    def test_directory_without_descriptor_is_incomplete(self):
        out = self.make_f7()
        os.remove(os.path.join(out, DESCRIPTOR))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.rule_id, "E-ARTIFACT-INCOMPLETE")


class FixtureDerived(TempCase):
    """F8, F9 and F9b are made here from the F7 artifact; they are not committed bytes yet (see the handoff)."""

    def test_f8_manifest_change_is_a_different_input(self):
        out = self.make_f7()
        with open(F7_MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["spine"][1]["reason"] = "edited reason"
        edited = self.path("edited.manifest.json")
        with open(edited, "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        self.assertNotEqual(build(F7_EPUB, edited).version_id, build(F7_EPUB, F7_MANIFEST).version_id)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, edited)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-DIFFERENT-INPUT file={out}")

    def test_f9_tampered_record_keeps_version_id_and_fails_content_hash(self):
        out = self.make_f7()
        records = self.read(out, RECORDS)
        self.write_bytes(out, RECORDS, records.replace(b"One text", b"Ona text", 1))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-CONTENT-MISMATCH file={RECORDS} record=1")

    def test_f9b_record_identity_disagrees_with_descriptor_and_hashes_consistent(self):
        out = self.make_f7()
        lines = self.read(out, RECORDS).splitlines()
        record = json.loads(lines[0])
        record["version_id"] = "0" * 64
        lines[0] = canonical(record)
        self.write_bytes(out, RECORDS, b"\n".join(lines) + b"\n")
        descriptor = self.descriptor(out)
        for entry in descriptor["files"]:
            if entry["name"] == RECORDS:
                entry["sha256"] = sha256_bytes(self.read(out, RECORDS))
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        self.save_descriptor(out, descriptor)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-IDENTITY-MISMATCH file={RECORDS} record=1")


class PackageLevel(TempCase):
    """M22: the two rules no epub can exercise."""

    def test_version_id_moves_when_a_source_file_changes(self):
        root = self.path("package")
        shutil.copytree(identity.PACKAGE_ROOT, root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        before = identity.version_id(F7_EPUB, F7_MANIFEST, root=root)
        with open(os.path.join(root, "ingest", "errors.py"), "a", encoding="utf-8") as f:
            f.write("\n# changed\n")
        self.assertNotEqual(identity.version_id(F7_EPUB, F7_MANIFEST, root=root), before)

    def test_a_run_killed_between_renames_leaves_a_directory_that_does_not_verify(self):
        out = self.path("killed")
        built = build(F7_EPUB, F7_MANIFEST)
        real_replace = os.replace
        calls = []

        def killed_before_descriptor(src, dst):
            calls.append(dst)
            if len(calls) == 3:
                raise RuntimeError("killed between renames")
            return real_replace(src, dst)

        with mock.patch("parallelprose2.ingest.artifact.os.replace", side_effect=killed_before_descriptor):
            with self.assertRaises(RuntimeError):
                write(built, out)
        self.assertFalse(os.path.exists(os.path.join(out, DESCRIPTOR)))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.rule_id, "E-ARTIFACT-INCOMPLETE")


class ArtifactRound34(TempCase):
    """Round 34 rules: the report's version-id, a missing file, a malformed descriptor, kills, a second run, script/style."""

    def test_report_tamper_with_consistent_descriptor_fails_on_report_identity(self):
        out = self.make_f7()
        report = self.read(out, REPORT).decode("utf-8")
        report = report.replace(f"version-id\t{self.descriptor(out)['version_id']}", "version-id\t" + "0" * 64)
        self.write_bytes(out, REPORT, report.encode("utf-8"))
        descriptor = self.descriptor(out)
        for entry in descriptor["files"]:
            if entry["name"] == REPORT:
                entry["sha256"] = sha256_bytes(self.read(out, REPORT))
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        self.save_descriptor(out, descriptor)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-IDENTITY-MISMATCH file={REPORT}")

    def test_missing_records_file_is_incomplete_and_names_the_path(self):
        out = self.make_f7()
        os.remove(os.path.join(out, RECORDS))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-INCOMPLETE file={os.path.join(out, RECORDS)}")

    def test_descriptor_that_is_not_json_is_malformed(self):
        out = self.make_f7()
        self.write_bytes(out, DESCRIPTOR, b"{not json")
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-MALFORMED file={os.path.join(out, DESCRIPTOR)}")

    def test_kill_after_the_first_rename_leaves_no_descriptor(self):
        out = self.path("killed-early")
        built = build(F7_EPUB, F7_MANIFEST)
        real_replace = os.replace
        calls = []

        def killed_after_first(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise RuntimeError("killed after the first rename")
            return real_replace(src, dst)

        with mock.patch("parallelprose2.ingest.artifact.os.replace", side_effect=killed_after_first):
            with self.assertRaises(RuntimeError):
                write(built, out)
        self.assertFalse(os.path.exists(os.path.join(out, DESCRIPTOR)))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.rule_id, "E-ARTIFACT-INCOMPLETE")

    def test_kill_after_the_second_rename_over_an_old_descriptor_does_not_verify(self):
        out = self.make_f7()  # a complete artifact with the old descriptor
        with open(F7_MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["spine"][1]["reason"] = "edited reason"
        edited = self.path("edited.manifest.json")
        with open(edited, "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        newer = build(F7_EPUB, edited)  # new records and report, so the old descriptor no longer matches them
        real_replace = os.replace
        calls = []

        def killed_before_descriptor(src, dst):
            calls.append(dst)
            if len(calls) == 3:
                raise RuntimeError("killed before the descriptor rename")
            return real_replace(src, dst)

        with mock.patch("parallelprose2.ingest.artifact.os.replace", side_effect=killed_before_descriptor):
            with self.assertRaises(RuntimeError):
                write(newer, out)
        with self.assertRaises(IngestError):
            verify(out, F7_EPUB, F7_MANIFEST)

    def test_second_run_gives_the_same_line_for_f8_f9_and_f9b(self):
        out = self.make_f7()
        records = self.read(out, RECORDS)
        self.write_bytes(out, RECORDS, records.replace(b"One text", b"Ona text", 1))
        lines = []
        for _ in range(2):
            with self.assertRaises(IngestError) as caught:
                verify(out, F7_EPUB, F7_MANIFEST)
            lines.append(caught.exception.error_line())
        self.assertEqual(lines[0], lines[1])
        self.assertEqual(lines[0], f"E-ARTIFACT-CONTENT-MISMATCH file={RECORDS} record=1")

    def test_structural_xhtml_that_is_not_well_formed_stops_with_the_xhtml_id(self):
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "f7_broken_cover.epub")
            with zipfile.ZipFile(F7_EPUB) as src, zipfile.ZipFile(copy, "w") as dst:
                for info in src.infolist():
                    data = b"<html><body><h1>unclosed</body></html>" if info.filename == "cover.xhtml" else src.read(info.filename)
                    dst.writestr(info, data)
            with self.assertRaises(IngestError) as caught:
                build(copy, F7_MANIFEST)
            self.assertEqual(caught.exception.error_line(), "E-XHTML-MALFORMED file=cover.xhtml")

    def test_f8_second_run_gives_the_same_line(self):
        out = self.make_f7()
        with open(F7_MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["spine"][1]["reason"] = "edited reason"
        edited = self.path("edited.manifest.json")
        with open(edited, "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        lines = []
        for _ in range(2):
            with self.assertRaises(IngestError) as caught:
                verify(out, F7_EPUB, edited)
            lines.append(caught.exception.error_line())
        self.assertEqual(lines[0], lines[1])
        self.assertEqual(lines[0], f"E-ARTIFACT-DIFFERENT-INPUT file={out}")

    def test_f9b_second_run_gives_the_same_line(self):
        out = self.make_f7()
        lines = self.read(out, RECORDS).splitlines()
        record = json.loads(lines[0])
        record["version_id"] = "0" * 64
        lines[0] = canonical(record)
        self.write_bytes(out, RECORDS, b"\n".join(lines) + b"\n")
        descriptor = self.descriptor(out)
        for entry in descriptor["files"]:
            if entry["name"] == RECORDS:
                entry["sha256"] = sha256_bytes(self.read(out, RECORDS))
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        self.save_descriptor(out, descriptor)
        seen = []
        for _ in range(2):
            with self.assertRaises(IngestError) as caught:
                verify(out, F7_EPUB, F7_MANIFEST)
            seen.append(caught.exception.error_line())
        self.assertEqual(seen[0], seen[1])
        self.assertEqual(seen[0], f"E-ARTIFACT-IDENTITY-MISMATCH file={RECORDS} record=1")

    def test_missing_report_file_is_incomplete(self):
        out = self.make_f7()
        os.remove(os.path.join(out, REPORT))
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-INCOMPLETE file={os.path.join(out, REPORT)}")

    def test_records_that_are_not_json_are_malformed_at_the_line(self):
        out = self.make_f7()
        self.write_bytes(out, RECORDS, b"{not json\n")
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-MALFORMED file={RECORDS} record=1")

    def test_report_that_is_not_utf8_is_malformed(self):
        out = self.make_f7()
        self.write_bytes(out, REPORT, b"\xff\xfe not utf-8\n")
        descriptor = self.descriptor(out)
        for entry in descriptor["files"]:
            if entry["name"] == REPORT:
                entry["sha256"] = sha256_bytes(self.read(out, REPORT))
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        self.save_descriptor(out, descriptor)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-MALFORMED file={os.path.join(out, REPORT)}")

    def test_consistent_spine_line_edit_in_the_report_is_a_content_mismatch(self):
        out = self.make_f7()
        report = self.read(out, REPORT).decode("utf-8")
        report = report.replace("spine\tch_a.xhtml\tbody\t5\tA", "spine\tch_a.xhtml\tbody\t6\tA")
        self.write_bytes(out, REPORT, report.encode("utf-8"))
        descriptor = self.descriptor(out)
        for entry in descriptor["files"]:
            if entry["name"] == REPORT:
                entry["sha256"] = sha256_bytes(self.read(out, REPORT))
        descriptor["content_hash"] = content_hash({e["name"]: e["sha256"] for e in descriptor["files"]})
        self.save_descriptor(out, descriptor)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-CONTENT-MISMATCH file={REPORT}")

    def test_descriptor_with_an_extra_file_is_malformed(self):
        out = self.make_f7()
        self.write_bytes(out, "extra.txt", b"extra\n")
        descriptor = self.descriptor(out)
        descriptor["files"].append({"name": "extra.txt", "sha256": sha256_bytes(b"extra\n")})
        self.save_descriptor(out, descriptor)
        with self.assertRaises(IngestError) as caught:
            verify(out, F7_EPUB, F7_MANIFEST)
        self.assertEqual(caught.exception.error_line(), f"E-ARTIFACT-MALFORMED file={os.path.join(out, DESCRIPTOR)}")

    def test_script_and_style_text_is_not_words(self):
        import xml.etree.ElementTree as ET
        from parallelprose2.ingest.artifact import word_count
        body = ET.fromstring('<body xmlns="http://www.w3.org/1999/xhtml"><p>one two</p><script>x y z</script>'
                             '<style>a b</style><p>three</p></body>')
        self.assertEqual(word_count(body), 3)


if __name__ == "__main__":
    unittest.main()
