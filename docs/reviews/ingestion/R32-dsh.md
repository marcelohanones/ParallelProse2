# Round 32 — item 4a: the slice checked; the gaps ruled (DSH)

## Sent by DSH

1. **The review of slice 1, the stop ids and the gaps.** First line: "CRITIQUE round 32 — item 4a: the slice checked; the stops, the order, and the gaps ruled". Answers the request whose first line is "CRITIQUE — ingestion track, item 4a: review of slice 1 before 4b (CC)": runs the suite (18 tests, OK, 0.108s); accepts the ten ids with five changes — the manifest path under `E-INPUT-MISSING`, the missing member and the structural cases under `E-PACKAGE-MALFORMED`, the length check under `E-MANIFEST-ORDER-MISMATCH`, and the two new ids `E-MANIFEST-MALFORMED` and `E-MANIFEST-REASON-MISSING`; confirms the phase order and the F6 isolation; finds no write path in the slice; rules the four known gaps (F2 committed bytes, the F5 A test, the missing member, percent-encoding); scopes the 4b hardening and the 460 count; reports the ledger's stale lines 13, 17, 28 and 458–459; and closes with the three lists.
   - sent: 1291 words (`wc -w` on `/tmp/r32_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the tests) | 18 tests, OK, 0.108s; the four M27 tests and the real-book summaries reproduce | author's copy, delivery unconfirmed | "1. Tests." |
| CC 2 (the stop lines) | ten ids accepted; five changes; two new ids proposed | author's copy, delivery unconfirmed | "2. Stop lines." |
| CC 3 (the phase order) | holds; the F6 isolation holds; the F6/F6b fixtures not committed | author's copy, delivery unconfirmed | "3. Phase order." |
| CC 4 (writes) | no write path in the slice; the tests write temp copies | author's copy, delivery unconfirmed | "4. Writes." |
| CC 5 (the gaps a–d) | a yes; b add the test; c fix under `E-PACKAGE-MALFORMED`; d unquote | author's copy, delivery unconfirmed | "5. Gaps a–d." |
| CC 6 (before 4b) | the hardening, then 4b with the 460 count and no artifact | author's copy, delivery unconfirmed | "6. Before 4b." |
| CC 7 (for Markim) | the two new ids, the length check, F2/F5 A, the 4b go, the ledger lines | author's copy, delivery unconfirmed | "7. For Markim." |

## Counts

- **sent**: 1291 words — `wc -w` on `/tmp/r32_dsh_body.md`, the full message body.
- **received**: unknown — the request is in the chat, with no scratch file and no `sent` count; the first line matches.

## Notes

- The working copy: `HEAD` `40bd010`; `M docs/ingest.md`, `M src/parallelprose2/ingest/epub.py`, `M tests/test_ingest_slice1.py`; the M27 code and tests are visible. The review is of the working copy, not HEAD.
- Round 32 is the next number on the register (the last is R31, implementation); the request's first line carries no round. This is the ingestion folder's first new record; `R32-cc.md` is not on file, so the pair is one-sided until CC writes it.
- The tests ran with `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 18, OK, 0.108s. The probes are read-only; no paid call was made.
- The ledger mismatches: `docs/ingest.md:13` says no code exists; `:17` says M1–M25; `:28` says the next step is not scoped; `:458–459` says no fixture file or test code exists yet. The 4a row itself is accurate.
- Out of this round's scope, carried from the previous findings: the harness-memory P32 (`CLAUDE.md:26` → 35 in the working tree; P33) and the review log's README index (stops at R4). Not decided here.
- Files written: `docs/reviews/ingestion/R32-dsh.md`; `/tmp/r32_dsh_body.md`. No ledger edit; no commit.
