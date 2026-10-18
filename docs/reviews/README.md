# Review log

Records each CRITIQUE round between Claude Code (CC) and DSH: what was sent, what came back, and the state of each.

## Rules

- **One file per round per side.** `R{n}-cc.md` is written by CC; `R{n}-dsh.md` is written by DSH.
- **Created by its author, never edited afterwards.** A correction is a new entry in the next round's file, not an edit.
  This follows the one-writer rule of `docs/harness_memory_design.md` (P1), applied here by analogy: P1 governs the
  memory store, not `docs/`.
- **Index.** An optional index may be added to this README. Only CC rewrites it (P9).
- **Reconcile on read.** The first act of each round is to read this directory and compare states before writing.

## States

Each entry gives one state per item it records:

- **delivered**: the answering message is in the record both sides can read.
- **author's copy, delivery unconfirmed**: the author holds the content, but the other side has no confirmed receipt.
- **gap**: a sent message with no answer on record.

Each entry also records the first line of the message it answers, so a mis-relay shows up by eye.

## Counts

Each entry records two word counts per message. The boundary is **round 5**: `R5-cc.md` and `R5-dsh.md` are the first
entries that carry counts. `R1`–`R4` are closed and are not edited to add counts.

**The counted span.** From the message's first authored character to its last. Excluded: any framing the relay adds
around the message, and any fence the relay wraps it in. Included: everything the author wrote inside the body,
including any fence the author placed there as part of the content. Raw markup is counted as transmitted, not as
rendered: `[text](path)` counts as the tokens it is made of.

**`sent`** is measured, not estimated. The author writes the message body to a scratch file outside the repo (for example
under `/tmp`), takes the count with `wc -w` on that file, records it, and then sends the file's content. Scratch
files are never written inside the repo, so nothing untracked is left for `git add -A` to pick up.
An author counting its own generated text by introspection is not a measurement.

**`received`** is counted by the receiving side on the text it received, with the same span rule. If the receiver cannot
tell where the authored body starts or ends, it records the count as `unknown`, not as a number. An `unknown` is not a
mismatch.

A mismatch between `sent` and `received`, both measured, is a signal to check the relay, the same way a mismatched
first line is. Counts are a check on delivery, not on content: a difference in wording does not show up here.

## Periods and tracks

- **R1–R28 are one mixed period.** They stay where they are, in this folder, mixed; none is moved or renamed.
- **From the next round, each track writes inside its own folder:** `implementation/` for the harness memory design,
  `ingestion/` for the ingestion spec (`docs/ingest.md`). The one-writer rule holds inside each folder.
- **`R28-dsh-p33.md` belongs to the implementation track.** Its name is odd on purpose, as its header explains; it is
  not to be renamed to `R28-dsh.md`.

## Files

- `R1-cc.md`: round 1, ingestion spec.
- `R2-cc.md`: acceptance request, items 1–11.
- `R3-cc.md`: fixture designs, eight designs and then the thirteen-design update.
- `R4-cc.md`: alignment on this log.
- `R1-dsh.md`, `R2-dsh.md`, `R3-dsh.md`, `R4-dsh.md`: DSH's side of the same rounds, written by DSH.

Each side's files are written by that side only.
