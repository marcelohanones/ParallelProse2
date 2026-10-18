# Ingestion fixtures (design)

Status: design only. No fixture file, test code or ingestion code exists. Each fixture is described by its input,
its expected outcome, and the defect it would catch. The rules are in [docs/ingest.md](ingest.md).

## Common conventions

- **Form.** A fixture is a minimal epub, built from a readable description and **committed as bytes** under
  `tests/fixtures/ingest/<name>.epub`, with its per-book manifest beside it. Each fixture has the same parts as a real
  epub: `mimetype`, `META-INF/container.xml`, `content.opf` (spine and manifest), `toc.ncx`, and the xhtml files.
  Tests read the committed bytes and never rebuild them: a rebuilt epub carries new zip timestamps, so its bytes —
  and therefore `version_id` — change between builds. If a builder is kept, one test asserts that rebuilding from the
  description reproduces the committed bytes exactly.
- **Stop means nothing that looks like an artifact is written.** When a fixture expects a stop, the run writes no
  JSONL, no artifact descriptor and no report. It prints one machine-readable error line — rule id, file, and chapter
  where one applies — and a partial artifact is a defect. Output is atomic (M15): the JSONL and the report go to
  temporary paths and are renamed only after every check has passed; the descriptor is renamed last and is the commit
  point, so without it there is no artifact.
- **Temporary files (M21).** Temporary paths are unique to the run, so a leftover from a crash can never be adopted
  and renamed into place by the next one. A typed stop removes the temporaries it created; an unexpected exception
  leaves them, under a name no later run adopts, because a partial JSONL is the only record of how far a crash got.
  The fixtures below test the typed-stop case only; the exception path is covered at package level.
- **Every fixture runs twice.** The second run must be byte-identical to the first, `version_id` and
  `content_hash` included (M17).
- **Names.** Fixture files use neutral names (`ch_a.xhtml`, `ch_b.xhtml`) so that the file name carries no meaning.

## F1 — body file without a chapter id

- **Input.** Spine: `cover.xhtml` (structural), `ch_a.xhtml` (body, chapter `A`), `ch_b.xhtml` (body, **no chapter
  id** in the manifest). Both body files have one text paragraph each. The TOC has one navPoint, for `A`.
- **Expected.** Stop. The error names `ch_b.xhtml` and says a body file has no chapter. No `.jsonl`, no descriptor
  and no report exists afterwards, and no temporary file remains.
- **Defect it catches.** A run that treats the missing id as a continuation of `A`, or that gives `ch_b.xhtml` a
  label from its file name; a run that has already written `ch_a.xhtml`'s paragraph to disk.

## F2 — chapter id with no navPoint

- **Input.** Spine: `cover.xhtml` (structural), `ch_a.xhtml` (body, chapter `A`), `ch_b.xhtml` (body, chapter `B`).
  The TOC has a navPoint for `A` only.
- **Expected.** Stop. The error names chapter `B`, its file `ch_b.xhtml`, and says it has no navPoint.
- **Defect it catches.** A run that names chapter `B` after its file, its id, or the previous navPoint's label.

## F3 — chapter split across files

- **Input.** Spine order: `ch_a_z.xhtml`, `ch_a_a.xhtml`, `ch_b.xhtml`. The manifest gives `ch_a_z` and `ch_a_a`
  chapter `A`, and `ch_b` chapter `B`. The TOC has one navPoint for `A`, **labelled `First chapter`**, pointing to
  `ch_a_z.xhtml`, and one for `B`. Each `ch_a_*` file has three paragraphs. The file names sort in the opposite
  order to the spine on purpose, and the label differs from both the id `A` and every file name on purpose.
- **Expected.** One chapter, labelled `First chapter`. Its paragraphs come from `ch_a_z` first, then `ch_a_a`, in
  spine order. `chapter_seq` runs 1–6 across both files, and `index` runs without a gap into chapter `B`, whose
  `chapter_seq` starts again at 1.
- **Defect it catches.**
  - Ordering by file name instead of spine order.
  - Restarting `chapter_seq` at each file.
  - Never restarting `chapter_seq` for the next chapter.
  - Opening a new chapter at the continuation file.
  - Taking the label from the continuation file, or using the chapter id as the label.
- **Isolation note.** The continuation file carries no navPoint of its own. A run that applies the no-navPoint rule
  per file rather than per chapter stops at `ch_a_a` and fails this fixture — which is the point.

## F4 — nested blocks: no duplicated text, no lost text

- **Input.** One body file, `ch_a.xhtml` (body, chapter `A`, with its navPoint in the TOC). A `<ul>` holding
  the first three blocks, then a `div` block:
  1. `<li><p>Text one.</p></li>`: a `p` inside an `li`.
  2. `<li>Text two.</li>`: bare text in an `li`.
  3. `<li>Text three.<p>Text four.</p></li>`: bare text before a `p` child (M14).
  4. `<div>Text five.<p>Text six.</p>Text seven.</div>`: a `div` with runs on both sides of its child (M14).
- **Expected.** Seven paragraphs, in document order: `Text one.`, `Text two.`, `Text three.`, `Text four.`,
  `Text five.`, `Text six.`, `Text seven.`; `index` 1–7 and `chapter_seq` 1–7, unbroken.
- **Defect it catches.**
  - Emitting both an `li` and its `p` (duplication).
  - Dropping `Text two.` when the `li` has no `p` child (silent loss).
  - Dropping `Text three.`, `Text five.` or `Text seven.` when a block has both direct text and a block child —
    the defect M14 exists to prevent.
  - Joining `Text three.` and `Text four.` into one paragraph, or emitting block 4's two runs as one.
  - Emitting the right texts in the wrong order.
- **Note.** The `li` blocks sit inside a `<ul>` so the fixture tests the nesting rule, not a parser's repair of
  invalid HTML.

## F5 — wrong extension: detected by content

- **Input A.** A valid epub (the F3 fixture) renamed `ch_a.pdf`.
- **Expected A.** Ingested as an epub, because the content is one, and the output is byte-identical to the same
  fixture ingested without the rename — `version_id` and `content_hash` included, since the path is not part of the
  identity (M5). The manifest is unchanged afterwards: the edition field that records the source file name still
  holds the committed name, so the rename reaches only the caller's path.
- **Input B.** A zip with no `mimetype` entry, named `book.epub`.
- **Expected B.** Stop before parsing. The error says the input is not an epub, by content.
- **Input C.** Four random bytes named `book.epub`, not a zip at all.
- **Expected C.** The same typed stop as B, not a traceback from the zip reader.
- **Defect it catches.** Dispatch on the extension alone (case A refused), dispatch on the name without checking the
  zip (case B accepted), a path leaking into the identity (case A's output differs), a run that rewrites the manifest
  to match the new name, an unhandled exception where a typed refusal belongs (case C).

## F6 — the manifest and the spine must match exactly

- **Input.** Spine: `cover.xhtml` (structural), `ch_a.xhtml` (body, chapter `A`), `ch_c.xhtml` (in the spine, **not in
  the manifest**). The TOC has one navPoint, for `A`.
- **Expected.** Stop. The error names `ch_c.xhtml` and says it is not classified.
- **Variant F6b.** The manifest lists `ch_d.xhtml`, which is not in the spine. **Expected:** stop, naming
  `ch_d.xhtml`. An entry is a per-spine-item classification; the book-level fields in the same file (edition
  metadata) are not entries and never trip this check.
- **Defect it catches.** A run that treats an unclassified file as body or skips it silently; a manifest that has gone
  stale — copied from another book, or written before the epub was re-encoded — which would silently drop a chapter.
- **Isolation note.** This is the one fixture whose expected error depends on the order of checks. `ch_c.xhtml` has
  no chapter id either, so a chapter check running before the classification check reports M8's error instead of
  M10's. [docs/ingest.md](ingest.md) fixes the order: classification, then chapters, then paragraphs (M18).

## F7 — the report: classes, word count, empty `<p>`, empty wrapper

- **Input.** Spine: `cover.xhtml` (structural), `note.xhtml` (`not-the-author`, with its reason), `ch_a.xhtml`
  (body, chapter `A`, with its navPoint) containing one text paragraph, one empty `<p>`, and one empty wrapper
  `<div>`.
- **Expected.** The body file emits one paragraph, `index` 1 — the empty `<p>` consumes no address. The report
  lists `cover.xhtml` and `note.xhtml` with class and reason, prints `ch_a.xhtml`'s word count as the number of
  tokens its text carries (the empty `<p>` and the empty wrapper add none), lists the empty `<p>` with its
  position, does not list the empty wrapper, and prints the manifest hash and the `version_id`.
- **Defect it catches.** A report that lists every file flatly, with no class and no reason; a report with no word
  count, or one that counts the empty elements; a report that omits the dropped empty `<p>`, leaving the gap between
  `<p>` count and paragraph count unexplained; a report that lists empty wrappers as drops, burying the audit in
  noise; an empty `<p>` that takes an address.

## F8 — a changed manifest changes the `version_id`

- **Input.** The F7 fixture ingested twice: once as committed, once after editing the reason recorded for
  `note.xhtml` — a field whose value the report prints.
- **Expected.** The two artifacts carry different `version_id`s and different reports, and comparing them is refused
  — different input, nothing to compare.
- **Defect it catches.** A `version_id` that ignores the manifest, letting a classification change ride through as if
  nothing had changed; a report that does not carry the reason it was told to record.

## F9 — a tampered artifact keeps its `version_id` and fails on `content_hash`

- **Input.** One F7 artifact, untouched in its descriptor, with one byte of the JSONL changed (a character in one
  paragraph's `source`).
- **Expected.** Verification refuses: `version_id` matches (same input), `content_hash` does not, and the error names
  the first differing record.
- **Defect it catches.** A `content_hash` that covers only some fields — a hash over `text` alone passes this tamper
  — and a verifier that trusts the descriptor's `version_id` without recomputing the file hashes.

## F9b — a record whose `version_id` disagrees with the descriptor's

- **Input.** One F7 artifact with **one record's `version_id` changed, and the descriptor made consistent again** —
  its file sha256 and `content_hash` recomputed over the changed file. Everything else, including the descriptor's
  own `version_id`, is untouched.
- **Expected.** Verification refuses on identity, naming the record: one artifact, one identity. The hash checks pass,
  because the tamper was made consistent.
- **Defect it catches.** A verifier that checks file hashes and never compares the descriptor's `version_id` to the
  records' — the case where every hash agrees and the artifact still says two different things about what produced
  it.
- **Why the tamper is made consistent.** Without recomputing the descriptor, F9b and F9 fail for the same reason and
  the third clause of M12 stays untested.

## F10 — normalization

- **Input.** One body file, chapter `A`, with its navPoint, one paragraph: `  Line one.<br/>Line two.   Line three.  `
  — leading and trailing spaces, a `<br>`, and a run of spaces.
- **Expected.** One paragraph, text exactly `Line one. Line two. Line three.` — the `<br>` becomes a space, the run
  collapses to one, the ends are trimmed. `index` 1.
- **Defect it catches.** A `<br>` dropped so the words fuse (`Line one.Line two.`); a run of spaces preserved; the
  text not trimmed; the `<br>` turned into a line break that survives into the stored text.

## F11 — navPoint on a chapter's second file

- **Input.** Spine order: `ch_a_z.xhtml`, `ch_a_a.xhtml`. The manifest gives both chapter `A`. The TOC has one
  navPoint for `A`, **labelled `First chapter`, pointing to `ch_a_a.xhtml`** — the second file, not the first.
- **Expected.** One chapter labelled `First chapter`; both files' paragraphs, `ch_a_z` first; no stop.
- **Defect it catches.** The rule M16 replaced — a label taken only from the navPoint that maps to the chapter's
  *first* file — which either stops here or falls back to the file name for a chapter that does carry a navPoint.

## F12 — the word-count boundary at an inline tag

- **Input.** One body file, chapter `A`, with its navPoint, one paragraph:
  `The Society of the Spectacle(<i>La</i> Société du spectacle)`.
- **Expected.** One paragraph, and a report word count of nine: `The`, `Society`, `of`, `the`, `Spectacle(`,
  `La`, `Société`, `du`, `spectacle)`. The element boundary between `(` and `La` acts as whitespace (M11).
- **Defect it catches.** A count that reads the text literally and fuses `Spectacle(La` into one token, giving eight
  — the reading M11 decided against; and a count that splits inside the inline element's own text.

## Rulings that shaped these fixtures

- **M14 (ruled):** bare text beside a block child is its own paragraph, applied recursively (F4, blocks 3 and 4).
- **M15 (ruled):** a stop writes nothing that looks like an artifact, output is atomic, temporaries are cleaned on a
  typed stop, and the error line is machine-readable (conventions).
- **M16 (ruled):** a chapter's label comes from any navPoint that maps to its files, first in spine order (F2, F11).
- **M17 (ruled):** the fixture set is F1–F6 with F6b as a variant, plus F7–F9; every fixture runs twice.
- **M18 (ruled):** the order of checks is fixed — classification, then chapters, then paragraphs (F6's isolation).
- **M19 (ruled):** the set extends to F9b, F10 and F11.
- **M20 (ruled):** verification recomputes each file's sha256 from disk; the stored `content_hash` is never trusted
  (F9, F9b).
- **M21 (ruled):** the descriptor is renamed last, temporaries are unique per run, a typed stop cleans them, an
  unexpected exception leaves them (conventions).
- **M22 (ruled):** F12 covers the word-count boundary; the source hash and crash-atomicity are package-level tests.
