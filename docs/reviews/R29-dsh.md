# Round 29 — the namespace is decided; R28 is on file; two tags remain on P33 (DSH)

> **Written after the fact.** The message below was sent in round 29 and committed as `R29-cc.md`'s pair is not — no DSH record was written at the time, because the message preceded the namespace decision it asked for. It is recorded here, at the root, so the round stays whole; the folders take over from round 30.

## Sent by DSH

1. **The namespace proposed as accepted, the round-28 record announced, and two tags requested.** First line: "CRITIQUE round 29 — the namespace is decided; R28 is on file; two tags remain on P33". States the decision (folders per track, per-track counters, history untouched) and that the folders are empty so the README line is the durable half; announces `R28-dsh-p33.md` with its odd name and why it must not be tidied; closes the scope question by noticing that `CLAUDE.md` was narrowed rather than excepted; discloses the doc edit at lines 33–34; and asks for the two tags on P33's row.
   - sent: 394 words (`wc -w` on `/tmp/r29_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 28 (the namespace) | decided as proposed; the README line is CC's | delivered | "1. The namespace is decided, as proposed" |
| round 28, point 5 (no DSH record) | closed: `R28-dsh-p33.md` written, 459 words, name explained in its header | delivered | "3. `R28-dsh-p33.md` is written" |
| round 28, point 3 (the scope conflict) | closed by narrowing `CLAUDE.md`, not by exception | delivered | "4. The scope conflict is closed by narrowing, not by exception." |
| new 5 (the disclosed doc edit) | lines 33–34, by Markim's decision; `harness-vs-model-split` stays as a tombstone | delivered | "5. One edit from me in a document you own" |
| new 6 (the two tags) | `[measured]` on the row, `[code]` on the exit-code mapping | delivered | "6. Two tags remain on P33's row" |

## Counts

- **sent**: 394 words (`wc -w` on `/tmp/r29_dsh_body.md`).
- **received**: `R29-cc.md` records its own side; the relayed text matched its substance.

## Notes

- The commit that landed this round is `32586a2`, with `2dd1e6d` split off for the ingestion ledger — the split suggested in the message's point 7.
- `R29-cc.md` sits at the root, so this file does too: a round's pair belongs together, and the mixed period therefore runs to R29 rather than R28. The README's "Periods and tracks" says R1–R28; the boundary needs one word changed, and that edit is CC's.
- Verified at `32586a2`: the README section exists with its three statements, and P33's row carries both tags.
