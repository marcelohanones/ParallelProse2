# Ingestion ledger

This file is the ingestion ledger: its status, its decisions and its open items. `docs/ingest_fixtures.md` is the test
set for these decisions. Nothing about ingestion is decided anywhere else in this repo.

Precedence: this ledger governs over `docs/documento_de_migracao.md` where they differ, because it records later and
more specific decisions. The migration doc sets the starting rules. CLAUDE.md's "Fonte" section states the same rule.

Source of the rules: `docs/documento_de_migracao.md`, section "Instruções para a ingestão", as amended by M1.

## Status

Slice 1 of this stage exists in `src/parallelprose2/ingest/` (landmark 4a, tested); no paragraph or artifact code is written yet. Landmarks, in order:

| # | landmark | state | status |
|---|---|---|---|
| 1 | Spec: decisions D-order, D1–D6, M1–M27 applied to this file | applied; DSH accepted the applied text in R28 (new; rounds 1–4 not recovered) | Done |
| 2 | Manifests: classification written for both books; edition values typed and reviewed | manifests written at `manifests/augustine.json` and `manifests/debord.json`, per M23; spine checked against each epub; edition values as confirmed by Markim | Done |
| 3 | Fixture designs: F1–F12, F9b, and the F6b variant | designed; DSH accepted all of them in R28, F7 with one change, now applied | Done |
| 4a | Ingestion runs on Augustine, first part: dispatch, readers, phases 1–2, F1 stop | built in `src/parallelprose2/ingest/` and tested (34 tests); no paragraphs, no artifact; committed as `e4f36dd`, manifest ids in M26 as `3871237`; M27 and M28 ids and the round 32 hardening uncommitted | Done |
| 4b | Paragraphs and addresses on Augustine (D6, M14), checked against the 460 count | `src/parallelprose2/ingest/paragraphs.py`: Augustine 460 paragraphs, addresses 1–460, one empty `<p>` dropped and listed; Debord 230 with 9 quoted and sourced; F3, F4 and F10 committed as bytes with tests (43 tests); no artifact (4c); uncommitted | Done |
| 4c | Artifact and identity: JSONL, report, `version_id`, `content_hash`, atomic writes | not started | Not started |
| 4d | All fixtures (F1–F12, F6b, F9b) pass twice, and both books run with no stop | not started | Not started |
| 5 | Ingestion runs on Debord | waits on Augustine first (D-order) | Not started |
| 6 | Determinism and artifact checks: `version_id`, `content_hash` | checked on a real run of both books; rules in Determinism and Version id | Not started |
| 7 | Output ready for the retriever (contract D1–D3) | contract D1–D3 is open; the output format depends on it | Parked |

Next: 4b is built (43 tests, uncommitted). Then 4c, the artifact and identity: the JSONL, the report, `version_id`, and
`content_hash`, which needs Markim's go.

Terms: "thesis" (or "tese") means the block's claim in the project's contract. Debord's printed numbers are
"printed numbers", stored as `printed_no`. The two are never interchanged (M4).

## Goal

Turn each epub into an ordered list of body paragraphs with a positional address. No judgment about the text, no
question, no selection by relevance at this stage. The address is assigned once here and never again.

## Input

One epub per book. Augustine first, then Debord (D-order).

| book | file | spine items | TOC entries (top level / total) | body |
|---|---|---|---|---|
| Augustine, *Confessions* (Pusey) | `data/raw/The_Confessions_Of_Saint_Augustine-Saint_Augustine.epub` | 18 | 15 / 15 | Books I–XIII, files `54_split_004`–`016` |
| Debord, *Society of the Spectacle* (Knabb 2002) | `data/raw/The_Society_of_the_Spectacle_(Knabb_2002)-Guy_Debord.epub` | 15 | 14 / 235 | chapters 1–9, files `ch-1`–`ch-9` |

## Dispatch

Detect the format from content, not extension: the zip must contain `mimetype` with `application/epub+zip`
and a `META-INF/container.xml`. Both inputs pass.

## Classification (M2, M3, M7, M10)

Every spine item of a book is classified in that book's **manifest**, a reviewed per-book file. Three classes
exist, and a fourth state that is an error:

- **body**: addressed, belongs to a chapter.
- **structural**: generated or redundant matter (cover, half-title, title page, contents, index). Excluded; nothing
  is lost, because a machine generated it or the book prints the same information elsewhere.
- **not-the-author**: a named person's prose that is not the author's. Excluded by judgment and never silently: the
  manifest carries the reason, and the report prints it with the word count.
- **absent from the manifest**: unclassified, and the run stops, naming the file. `unclassified` is not a value
  the manifest can hold (M10).

Classification is a named list per book, not a rule on TOC labels. A label rule cannot separate Augustine's
`000` (labelled with the book's own title) from a chapter. Declared judgment: every non-body class is a judgment,
recorded in the manifest and printed in the report. It is not a mechanical fact and is not derived from labels.

Manifest content for the two books (spec-level; the manifest file is written later):

Augustine (18 spine items):
- `titlepage.xhtml`: structural (image-only cover).
- `54_split_000`: structural (title page; TOC label is the book's title).
- `54_split_001`: structural (Duke Classics copyright notice; no TOC entry).
- `54_split_002`: structural (contents list; TOC label `Contents`).
- `54_split_003`: structural (edition and translator page; no TOC entry).
- `54_split_004`–`016`: body, chapters `Book I`–`Book XIII`, one file each.

Debord (15 spine items):
- `titlepage.xhtml`: structural (TOC label `Cover`).
- `half.html`: structural (no TOC entry).
- `title.html`: structural (TOC label `Title Page`).
- `contents.html`: structural (TOC label `Contents`).
- `note.html`: not-the-author (TOC label `Translator’s Note`). 271 words of Ken Knabb's prose about the
  translation, excluded so the translator's sentences are never addressed as Debord's. Recorded here as a decision,
  not left as a side effect of a list (M7).
- `ch-1.html`–`ch-9.html`: body, chapters `1: The Culmination of Separation` through `9: Ideology Materialized`.
- `index.html`: structural (TOC label `Index`). A generated map to printed numbers, not prose (M3).

## Chapters (M6, M8)

- A chapter is a top-level TOC navPoint in a body item.
- Every body file carries a `chapter` id in the manifest. Files sharing an id are one chapter, in spine order.
- A chapter's label is the TOC label of the navPoint mapping to any of the chapter's files, first in spine order
  (M16). A chapter whose files carry no navPoint stops the run: a chapter with no printed label is not named after a
  file, an id, or the previous chapter's label.
- A body file with no `chapter` id stops the run (M8): it is neither a new chapter nor a continuation, and it is
  not guessed from its position or its name.
- Reading order is the spine order in `content.opf`, never file-name order.

Augustine: one navPoint per Book, one file each (checked for all 13). Debord: one navPoint per chapter, one file
each; the 221 numbered entries are nested inside those chapters and point to anchors inside the files.

## Check order (M18)

A run checks a book in this order, and the first failure stops it:

1. **Classification** — every spine item is in the manifest, every manifest entry is in the spine, and every class is
   one of the three (M2, M7, M10).
2. **Chapters** — every body file carries a `chapter` id, and every chapter has a navPoint (M6, M8, M16).
3. **Paragraphs** — the leaf and direct-text rules are applied and the addresses are assigned (D6, M14).

The order is part of the contract: a book that breaks two rules reports the earlier one, never the later. A spine item
that is unclassified therefore reports M10's error even though it also has no chapter id.

## Paragraphs

Block elements are `p`, `div`, `blockquote` and `li`. Inline elements (`span`, `em`, `i`, `a` and the like) do not
split a run of text. A block's **direct text runs** (text not inside a child block) are each one paragraph, and each
child block is processed the same way, all in document order (D6, amended by M14). A block with no direct text and
no text-bearing child produces nothing (an empty wrapper). Excluded: headings (`h1`–`h6`), the table of contents,
and attribution lines (`p.attrib` inside `blockquote`). Attribution goes to `source` on the quoted paragraph.

Text is normalized: `<br>` becomes a space, runs of whitespace collapse to one space, the result is trimmed.
An empty `<p>` (no text after normalization) is dropped and listed in the report. It consumes no address. An
empty wrapper element (a `div`, `blockquote` or `li` with no text of its own and no text-bearing child)
produces nothing and is not listed.

## Fields per paragraph (output)

| field | rule |
|---|---|
| `index` | integer, 1…N over kept paragraphs, in reading order. Assigned here only. |
| `version_id` | see "Version id" |
| `chapter` | TOC label of the chapter (`Book I`; `1: The Culmination of Separation`). The label, not a number. |
| `chapter_seq` | position within the chapter, from 1 |
| `text` | normalized text, as written |
| `quoted` | true when the block is inside a `blockquote` |
| `source` | the attribution line of the blockquote, or null |
| `printed_no` | the printed number (D5): the number of the numbered entry the block belongs to; null when the book prints none, or for epigraphs |

Output format: JSON Lines, one object per paragraph. Recommended; internal to ingestion and does not touch the
contract.

## Printed numbers (Debord)

- The printed number is the text of `<h3 class="num">N</h3>`. Its `id` (`toc_N`) restarts in every chapter, so
  it is not a key; `printed_no` is.
- Each number covers the single leaf block that follows it. Verified: 221 numbers, 1–221, no duplicates, no
  gaps; every number covers exactly one block.
- Each chapter opens with a `blockquote` holding an epigraph (quote + attribution). The 9 epigraphs are
  paragraphs (`quoted=true`, `source` = attribution) with `printed_no` null.
- Printed number 146 is in `<div class="calibre3">` in `ch-5.html`. It is kept.

## Version id (M5, M9, M12, M13)

`version_id` is a single hash over a canonical serialization of:
- the sha256 of the epub file bytes;
- the sha256 of the ingestion source files — every file under `src/parallelprose2/`, sorted by path (the code,
  not a hand-bumped version string);
- the sha256 of the book's manifest (edition fields and classification).

The canonical serialization is JSON with sorted keys and no insignificant whitespace.

Excluded from the identity: the file path.

The **artifact descriptor** is committed next to the two files and lists, for each of them, its name and its
sha256. `content_hash` is the sha256 of the canonical serialization of that list — `(name, sha256)` pairs, sorted
by name — not of the files concatenated, so the boundary between the two cannot shift. The descriptor is what an
artifact is verified and compared by: the JSONL alone carries only `version_id`, and a copied fragment is not an
artifact.

Verification runs one recomputation, two directions and one equality:
- the stored `content_hash` is never trusted (M20). Verification recomputes each file's sha256 from disk and
  rebuilds the `(name, sha256)` list before comparing; the stored value is a convenience for a reader, never
  evidence. A file altered without its descriptor is caught here and nowhere else.
- unequal `version_id`: refuse. Different input; there is nothing to compare.
- equal `version_id`, unequal `content_hash`: refuse, and print the first differing record. The same input that did
  not produce the same output is a defect, not a variant of the artifact.
- an artifact whose records carry a `version_id` different from its descriptor's is refused: one artifact, one
  identity.

Edition fields live in the manifest and are typed in once, reviewed once. `content.opf` carries no translator
or edition year for either book.

## Determinism

Output order is: spine order, then document order within a file, then the order of the `index` assignment.
Nothing is iterated over an unordered collection. Two runs on the same input produce byte-identical output.

Output is written atomically (M15, M21): the JSONL and the report go to temporary paths unique to the run, and are
renamed only after every check has passed. The descriptor is renamed last — it is the commit point, so a run that
stops leaves no artifact. A typed stop removes the temporaries it created; an unexpected exception leaves them,
under a name no later run adopts, because a partial JSONL is the only record of how far a crash got.

## Report

The report is an audit of the run:
- each spine item with its class and its word count, and the recorded reason for every non-body item;
- each empty `<p>` dropped, with its position;
- the manifest hash and the version id.

Empty wrapper elements are not listed (they are not blocks). The report is part of the artifact and enters
`content_hash` (M9).

**Word count (per spine item, in the report).** The number of whitespace-separated tokens in the text of the
file's `<body>` element that contain at least one letter or digit. Element boundaries act as whitespace: the
`<body>`'s text nodes are taken in document order and separated by one space before splitting, so a word glued to
the next by an inline tag — `The Society of the Spectacle(La Société du spectacle)` — counts as two tokens at that
edge, even though the edition prints them joined. Script, style, head and title text are excluded. Punctuation-only
tokens (`.`, `&`, `(`, `)`) are not words. The count covers all text the file carries, not only the paragraphs D6
would emit. Measured: `note.html` 271, `contents.html` 57 (both match the figures previously in this spec),
`index.html` 363, `title.html` 24, `half.html` 7, `titlepage.xhtml` 0; under the same rule, Augustine's
`54_split_000` 12.

## Tests

Required by the migration doc, one per known edge. Status against the two books:

| test | covered by | status |
|---|---|---|
| file with no TOC entry is not a chapter and yields no address | Augustine `001`, `003`; Debord `half.html` | covered by data (classified structural) |
| body file with no `chapter` id stops the run | none | **not covered** — designed as F1; not built |
| chapter id assigned but no navPoint for it stops the run | none | **not covered** — designed as F2; not built |
| several TOC entries into one file keep every title and number | Debord: 221 numbered entries into 9 files | covered by data |
| chapter split over several files: one chapter, spine order kept | none | **not covered** — designed as F3; not built |
| nested `<li><p>`: no duplicated text | none found | **not covered** — designed as F4; not built |
| wrong extension: detected by content | none | **not covered** — designed as F5; not built |
| internal line breaks: no artificial breaks mid-sentence | Augustine 4 `<br>` in `<p>`; Debord 1 in `ch-5` | covered by data (and designed as F10) |
| spine item missing from the manifest stops the run | none | **not covered** — designed as F6 (and F6b); not built |

Also required:
- Running ingestion twice gives byte-identical output with the same `version_id` and the same `content_hash`.
- A `version_id` mismatch between two artifacts is refused, and so is an equal `version_id` with an unequal
  `content_hash`.
- Front matter, headings, the table of contents and the index never appear in the output.
- The report lists exactly the non-body items, with their class and reason, and the dropped empty `<p>`.

Every fixture in `docs/ingest_fixtures.md` is a required test, and each one runs twice so the determinism rule
above is exercised with it (M17).

Two rules are tested at package level rather than by a fixture, because no epub can exercise them (M22): the
`version_id` moves when a file under `src/parallelprose2/` changes (M13), and a run killed between the two renames
leaves a directory that does not verify (M15). A deferred one is recorded as unverified, never as covered.

## Proibições

- No judgment about the text: no interpretation, no question, no selection of paragraphs in this stage.
  Classifying a file is a judgment of the manifest's, declared in the report, never one taken about the prose here.
- No address is created outside this stage.

## Critério de pronto

The tests pass on the real files for both books, and running ingestion twice gives byte-identical output with
the same `version_id` and the same `content_hash`.

## Decisions

Each decision: what it settles, the premise that made it necessary, and what would invalidate it.

**D-order — Augustine first, then Debord.** Settles: which book is implemented first.
Premise: Augustine has no printed numbers and one file per Book, so it is the simpler baseline.
Invalidated by: Augustine failing a test that only applies to Debord.

**D4 — ingestion before the retriever–editorial contract.** Settles: the order of work.
Premise: the ingestion is the best-documented stage, and the contract's format depends on what ingestion emits.
Invalidated by: ingestion output found unfit for the editorial AI's needs; then the contract would redefine it.

**D1 — the editorial AI sends a closed directive, not text (parked with the contract).** Settles: who writes
the next-round request. Premise: the retriever stays deterministic (premise 1 of the migration doc).
Invalidated by: premise 1 changing to allow an LLM inside the retriever.

**D2 — output unit (parked with the contract).** Open until the editorial AI's requirements are written.

**D3 — per-block query cap (parked with the contract).** Open until the adaptive design exists.

**D5 — `printed_no` is a second key, not the address.** Settles: the reader-facing citation for Debord.
Premise: the reader must match the output to the printed book, and Debord's numbers are its own citation.
Invalidated by: a decision that reader-facing citations use only the positional `index`.
Reversible: without the field, the address is unchanged.

**D6 — paragraph = leaf text block (p, div, blockquote, li).** Settles: what counts as a paragraph.
Premise: printed number 146 is text in a `<div>`; a `<p>`-only rule would drop it silently.
Invalidated by: an edition whose paragraphs are nested text blocks that should count as one, or text in an
element outside the four above. This supersedes the earlier Q3 answer ("each `<p>`").

**M1 — front matter: amend the migration doc in place.** Settles: the front-matter test. The doc's line now
reads: a file with no TOC entry, or front matter, yields no chapter and no address; it is classified as apparatus
(structural, or not-the-author) and listed; an unclassified file stops the run.
Premise: the doc's test is protecting against a tiny front-matter document, and excluding the file meets that
without inventing a title from content.
Invalidated by: a body file that needs a title the TOC does not give.
Supersedes: the earlier D-front ("title from content" was the doc's wording).

**M2 — three-way classification, fail-closed.** Settles: how every spine item is classified.
Premise: a label rule missed Augustine's `000` (its label is the book's own title), and the old code caught it
only through a word-count threshold.
Invalidated by: a book whose spine items can't be listed by hand, which would make a per-book manifest impractical.

**M3 — Debord's `index.html` is excluded as structural.** Settles: whether the index is addressed.
Premise: it is a generated map to printed numbers (83 blocks, mean 4.4 words, 70 of 83 with numerals), not prose.
Invalidated by: a use of the index as a source of content the editorial AI must quote.
It is last in the spine, so excluding it shifts no address.

**M4 — term reservation.** Settles: "thesis/tese" is the block's claim; Debord's numbers are "printed numbers"
(`printed_no`).
Premise: one word for two objects, one of them the object the editorial AI reasons about, produces drift.
Invalidated by: the editorial AI having no use for the block's claim as a distinct object.

**M5 — `version_id` derivation.** Settles: what the id is computed from (see "Version id").
Premise: a hand-bumped code version lets two different outputs compare equal; a path in the identity refuses
identical content after a repackage or rename.
Invalidated by: a case where content equality must be checked without the manifest.

**M6 — chapter identity.** Settles: how a chapter spanning several spine files is one chapter (see "Chapters").
Premise: without a rule the split-file test cannot be written; a fixture would assert behavior the spec never
defined.
Invalidated by: a book where one navPoint's files are not in spine order.
Refined by M8: the navPoint alone could not distinguish a continuation file from an orphan one.

**M7 — the non-body classes are two, not one.** Settles: whether a translator's note is filed with a generated
index. Premise: a single class holding both a machine-generated map and a named person's prose hides a judgment
about authorship inside a claim about format; the note is the only excluded item in either book that is authored
prose, and after exclusion it can never be addressed, because no address is created outside this stage.
Invalidated by: a decision to address the note in its own artifact, separate from the book's address space.
Supersedes: the single "apparatus" class of M2.

**M8 — chapter identity comes from the manifest.** Settles: what makes two spine files one chapter. Premise: M6's
clauses contradicted each other — a split chapter's continuation file is exactly a body file with no navPoint — so
the split-chapter test could not be written, and the tests added in round 1 asserted opposite outcomes for one
input shape.
Invalidated by: a book whose chapter boundaries cannot be listed by hand without reading the whole book.

**M9 — the report enters the artifact identity.** Settles: what `content_hash` covers and where it lives. Premise:
the report is the artifact that makes the classification judgment auditable, and M5 left it outside both hashes, so
two runs could differ in the audit and compare equal; JSON Lines has no slot for a per-artifact value.
Invalidated by: a downstream stage that must compare artifacts by their paragraphs alone, with no file-level check.

**M10 — "unclassified" means absent.** Settles: whether the fail-closed state can be written as a value. Premise: a
manifest that can hold `unclassified` turns the stop into something a reviewer writes past; an absent entry is not
a decision anyone can make by accident.
Invalidated by: a manifest format that must emit a value for every spine item it lists.

**M11 — an element boundary counts as a word boundary.** Settles: how the report's word count splits across tags.
Premise: the rule as first stated ("tokens in the text of the body") gives 23 for `title.html` and 10 for
`54_split_000` under a literal joining of the text, and 24 and 12 when element edges separate; the spec published
the second pair without stating the rule, so two implementations could disagree on two of the seven files measured.
Invalidated by: a decision that the count should follow what a reader sees, joined — the figures then become 23 and
10, and the published list changes.

**M12 — `content_hash` is a hash of the descriptor's file list.** Settles: what the content hash is computed over.
Premise: hashing the two artifacts concatenated is not injective — a different split point yields the same bytes —
and nothing required an artifact's records and its descriptor to agree on `version_id`.
Invalidated by: a storage format that cannot name the two artifacts independently, which would leave only a
concatenation to hash.

**M13 — the source file set is named.** Settles: which files the code hash covers. Premise: "the ingestion source
files" was a set with no boundary, so two runs over different sets could share a `version_id`.
Invalidated by: a build that generates code outside `src/` at run time, which the set would miss.

**M14 — bare text beside a block child is its own paragraph.** Settles: what a block with both direct text and a
text-bearing child emits. Ruled: each direct text run becomes its own paragraph, and each child block is processed
the same way, recursively, all in document order. A block with two runs and one child block yields three paragraphs. Premise: the leaf rule cannot place the bare text, and dropping it would be silent loss. Checked: no body
block in either book mixes the two, so the counts above do not change. Invalidated by: an edition whose bare text
is a caption or label that must not be addressed as prose. Amends: D6.

**M15 — a stop leaves no artifact, and output is atomic.** Settles: what a run that stops leaves on disk. Premise:
since M9 and M12 the report is part of the artifact, so a report written on failure would make "a report exists" stop
meaning "the run completed"; and "writes nothing" is only true if output is buffered, which an implementation that
writes as it goes is not. With no file written, the error line is the only durable record of why the run stopped, so
it is machine-readable: rule id, file, and chapter where one applies.
Invalidated by: a workflow that must resume a partly ingested book from where it stopped.

**M16 — a chapter's label comes from any of its files.** Settles: the label when the navPoint targets a file that is
not the chapter's first. Premise: the earlier wording named "the navPoint mapping to the chapter's first file", which
is undefined for a TOC that anchors mid-chapter — the chapter still carries a navPoint, so it does not stop, and it
has no label either.
Invalidated by: an edition whose navPoints point at files outside their own chapter.

**M17 — the fixture set is wider than the six edges, and every fixture runs twice.** Settles: what the tests are.
Premise: the six edge fixtures left the report's content, the three identity refusals and determinism untested, and
those are the rules that make two artifacts comparable at all.
Invalidated by: a format in which an artifact can be compared without its descriptor.

**M18 — the order of checks is fixed.** Settles: which error a book that breaks more than one rule reports. Premise:
an unclassified spine item also has no chapter id, so a chapter check running first reports M8's error instead of
M10's — the expected error of the one stop fixture whose defect depends on order.
Invalidated by: a book where the chapter check must run first to avoid a spurious classification error.

**M19 — the fixture set extends to F9b, F10 and F11.** Settles: whether M17's set is closed. Premise: three spec
rules had no test — the record-versus-descriptor identity of M12, the normalization rule, and M16's own case, a
navPoint pointing at a chapter's non-first file.
Invalidated by: a rule change that makes any of the three unobservable.

**M20 — verification recomputes the hashes.** Settles: what a verifier trusts. Premise: `content_hash` is defined
over the descriptor's own `(name, sha256)` list, so a file altered without its descriptor leaves that list — and the
stored `content_hash` — internally consistent; a verifier that only recomputes `H(list)` refuses nothing. F9 and
F9b both depend on this step, and neither followed from the text before it.
Invalidated by: a format where the file hashes are not recomputable at verification time.

**M21 — rename order and temporaries.** Settles: what a stop leaves and in what order files appear. Premise: M15
said when files are renamed, never in what order or what happens to temporaries, so two fixture assertions had no
rule behind them; a fixed temporary name left by a crash can be adopted by the next run and renamed into place.
Invalidated by: a storage layer that gives atomic directory swaps, where order and temporaries disappear as concepts.

**M22 — the three rules no fixture reaches.** Settles: how the word-count boundary, the source hash and
crash-atomicity are tested. Premise: no epub can change the code or kill a process between renames, and F7's text
has no inline element, so the boundary rule M11 decided was never exercised.
Invalidated by: a harness that can drive ingestion in-process and fault-inject, which would make the package-level
tests fixtures like the rest.

**M23 — the manifest is one JSON file per book, with a spine array.** Settles: the format of the manifest and what it
holds. Ruled by Markim in round 28, on DSH's recommendation: one JSON file per book; a `spine` array in reading order
with one object per spine item, `{href, class, chapter?, reason?}`; a separate `edition` object (title, translator,
year, source file name) that is never an entry. Class is exactly `body`, `structural` or `not-the-author`; there is no
`unclassified` value (M10). `chapter` is required for `body` (M8); `reason` is required for both non-body classes (M7).
Phase 1 compares the array to the OPF spine index by index: same length, same href at each position; a duplicate href
is a format error. Premise: a per-spine-item array makes both directions of the classification check, and the order
check, one comparison; a reason written as data is printed and hashed, where a comment would drift. Invalidated by: a
book whose spine cannot be listed by hand, or a need for comments the report must not carry.

**M24 — error rule ids: eight, one per failure condition.** Settles: the machine-readable id of each stop. Ruled by
Markim in round 28, on DSH's recommendation: `E-INPUT-NOT-EPUB` (F5 B and C), `E-SPINE-UNCLASSIFIED` (F6),
`E-MANIFEST-ENTRY-NOT-IN-SPINE` (F6b), `E-BODY-NO-CHAPTER` (F1), `E-CHAPTER-NO-NAVPOINT` (F2),
`E-ARTIFACT-DIFFERENT-INPUT` (F8, the unequal `version_id` refusal), `E-ARTIFACT-CONTENT-MISMATCH` (F9),
`E-ARTIFACT-IDENTITY-MISMATCH` (F9b). Form: `E-` plus uppercase kebab; the noun names the object, the tail the
condition; no numbers and no stage prefix. The `E-` says the id is an error, the stop that the M15 error line carries;
it marks no stage, version or track, and it was in the form CC proposed in R28 (`E-BODY-NO-CHAPTER`). Two stops share an id only when they are the same condition: F5 B and C,
and F8 with the `version_id` refusal. F9 and F9b do not share. Premise: the id names the condition, so the error line
is unambiguous for a reader that matches on it. Invalidated by: a reader that must tell apart two fixtures that
trigger the same condition.

**M25 — slice 1 uses the standard library only.** Settles: the parser stack for the first build slice. Ruled by Markim
in round 28, on DSH's recommendation: `zipfile` and `xml.etree.ElementTree`, nothing else. Premise: both epubs open
with `zipfile`, their `.xhtml` and `.html` files parse with `xml.etree.ElementTree`, the only named entity is `&amp;`,
and no DOCTYPE appears (checked by CC and DSH). Invalidated by: a book with an HTML named entity or malformed markup.
In that case the parse error becomes a typed stop, and `lxml` is added then, not before.

**M26 — the manifest checks outside M24 get ids.** Settles: the machine-readable ids of the three manifest checks that
M24 leaves out. Ruled by Markim in the ingestion track: `E-MANIFEST-DUPLICATE-HREF` (a manifest href listed twice),
`E-MANIFEST-ORDER-MISMATCH` (the manifest order differs from the spine at some position), and
`E-MANIFEST-CLASS-INVALID` (a class outside `body`, `structural` and `not-the-author`). Form as M24. Premise: phase 1
needs an id for each of its checks, or the error line is ambiguous for a reader that matches on it. Invalidated by: a
manifest format that cannot express a duplicate, an order or a class value. A length difference from the spine is a
mismatch of order too, approved in round 32 and stopped as `E-MANIFEST-ORDER-MISMATCH` on the extra item.

**M27 — two ids for unreadable input.** Settles: the ids for a missing input path and for a package file that is not
well-formed XML. Ruled by Markim in the ingestion track: `E-INPUT-MISSING` (the path given to the run does not exist;
the `file` is that path) and `E-PACKAGE-MALFORMED` (the `META-INF/container.xml`, the `content.opf` or the `toc.ncx` is
not well-formed XML; the `file` is that member). Form as M24. Premise: a missing path and a malformed package are two
conditions, and M24 gives one id per condition. Invalidated by: a need to report one of these conditions with more
detail than the id and the file carry. Extended in round 32, approved by Markim: the same id also covers a member that the container or the OPF names and
the zip lacks, and the structural gaps (a `rootfile` without `full-path`; an OPF without `manifest` or `spine`, or a spine
without `toc`; a manifest item without `id` or `href`; a `navMap` missing from the NCX; a navPoint without a label or
content). xhtml parsing is still not done by slice 1.

**M28 — two manifest ids: malformed manifest, and a missing reason.** Settles: the ids for a manifest that is not
a manifest (`E-MANIFEST-MALFORMED`: not JSON, or missing `spine`, `edition`, an entry's `href` or `class`), and for a
non-body entry with no `reason` (`E-MANIFEST-REASON-MISSING`, which M23 requires). Ruled by Markim in round 32, on
DSH's recommendation. The `file` is the manifest path for the first, and the entry's href for the second. The reason
check runs in phase 1, after the class check and before the order check. Form as M24. Premise: M23 requires a reason
for both non-body classes, and a missing reason is the same kind of gap as an unclassified item, so it needs its own
stop. Invalidated by: a rule that allows a non-body entry without a reason.

**M29 — four extraction choices in paragraph extraction.** Settles: how the extraction treats structure the ledger does
not name. Recorded by CC in round 33 for Markim's review; not yet ruled. (1) Containers that are neither block nor inline
(`ul`, `ol`, `body`) pass their children through, without a paragraph of their own; their direct text, if any, would be
a paragraph. Premise: D6 names only `p`, `div`, `blockquote` and `li` as blocks, and a `ul` holds only `li` blocks.
Invalidated by: a container with direct text that is not a block. (2) The inline set is `span`, `em`, `i`, `b`, `strong`,
`a`, `small`, `sup`, `sub`, `u`, `font`, `abbr`, `cite`, `code`, `q` and `img`; an element outside it is treated as a
block. Premise: the set is what the two books use. Invalidated by: a new inline element that splits a run when it should
not. (3) Whitespace for normalization is Unicode whitespace, so a non-breaking space collapses to a space. Premise:
Debord has 19 non-breaking spaces in its html and Augustine has one. Invalidated by: a rule that keeps them as text.
(4) A blockquote's attribution `<p>` is not text of the body; it is the `source` of the quoted paragraphs, and it still
counts toward the position of a dropped `<p>`. Premise: D6 already excludes it, and the position stays the `<p>` ordinal
in the file. Invalidated by: a dropped `<p>` report that is meant to count only text paragraphs.

## Open

- **Manifest ids** — decided in M26 (`E-MANIFEST-DUPLICATE-HREF`, `E-MANIFEST-ORDER-MISMATCH`, `E-MANIFEST-CLASS-INVALID`) and M28 (`E-MANIFEST-MALFORMED`, `E-MANIFEST-REASON-MISSING`).
- **Fixtures** — designed and accepted by DSH in R28 (F7 with one change, applied); F1 and F2 are built as committed bytes (`tests/fixtures/ingest/`), with tests. `docs/ingest_fixtures.md` holds F1–F6 (F6b as a variant), F7–F9, F9b and
  F10–F12; F3–F12 are not built as files yet. The two package-level tests of M22 are designed, not written.
- **Word count** — closed (M11). Method stated under Report, including the element-boundary rule; every published
  figure reproduces under it.
- **Manifest values.** Typed and confirmed by Markim: Augustine, "1921 Chatto & Windus edition" (`54_split_003`),
  translator Edward Bouverie Pusey; Debord, translator Ken Knabb (`content.opf` creator), 2002 from the file name.
  Written to `manifests/augustine.json` and `manifests/debord.json`.
- **Augustine `citation_mark` and `printed_source`.** Not checked; default null, since no page markers were found.
- **Augustine headings (A5).** Closed. Checked read-only: the first `h1`/`h2` of each Book file equals its navPoint
  label, 13 of 13.

## Counts (verified read-only)

- Augustine: spine `<p>` 465; with text 464; empty 1 (in `54_split_016`). Front matter `54_split_003`: 4 text
  paragraphs, structural. Body Books I–XIII: 461 `<p>`, 460 with text. Paragraphs run 1–460.
- Debord: spine `<p>` 340; with a word character 331; blank 9. Body `ch-1`–`ch-9`: 238 `<p>` with text plus
  1 `<div>` (printed number 146). Minus 9 attribution lines, 230 paragraphs = 221 numbered paragraphs + 9
  epigraphs. Paragraphs run 1–230 with front matter and the index as structural.
- Context, not binding: the old ingest (`ingest.py`) also promoted headings. It gives 473 paragraphs for Augustine (460 `<p>`
  + 13 `<h1>`), 238 for Debord (220 numbered `<p>` + 9 epigraphs + 9 `<h2>` chapter heads). These are not
  comparable to the counts above. Do not compare artifacts across the two pipelines.


