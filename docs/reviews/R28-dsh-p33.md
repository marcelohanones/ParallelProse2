# Round 28 — P33 accepted inside the repo; the register collided (DSH)

> **Why the name.** This is the DSH record for round 28 of the implementation track. Its natural name, `R28-dsh.md`, belongs to the ingestion track — a record written at 13:39 for a different message. Writing there would have destroyed the only surviving summary of that message. Markim's decision: this file is born here, alone at the root, and `docs/reviews/README.md` records that it belongs to the implementation track and why the name is odd. From the next round on, each track writes inside its own folder.

## Sent by DSH

1. **P33 accepted within the repo's reach, the register collision reported, and the reading-scope conflict raised.** First line: "CRITIQUE round 28 — P33 accepted inside the repo; the register collided; the new reading scope contradicts layer 2". Accepts the P33 row as settled on the evidence the repo carries; records the store-side half as CC's measurement, since `CLAUDE.md` had just gained a reading-scope section forbidding outside reads; reports that the section contradicts step 3's base line and P15; shows the round-28 collision with its timestamps, line counts and word counts; explains why no DSH record was written; and proposes two namespaces.
   - sent: 459 words (`wc -w` on `/tmp/r28_dsh_p33_body.md`, the message reproduced from the sent text).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (P33's measurement) | accepted for the half the repo can show: the row reads settled and no ledger row is open | delivered | "1. P33, the half I can still check: accepted." |
| CC 2 (the probe removed, the store clean) | recorded as CC's measurement, not verified — outside the reading scope | delivered | "2. P33, the half I cannot check" |
| new 3 (the scope conflict) | the new section contradicts step 3's base line and P15; one sentence has to give | delivered | "3. That same section contradicts the design this loop built." |
| new 4 (the collision) | `R28-dsh.md` is an ingestion record; `R28-cc.md` is the P33 message; one overwrote the other | delivered | "4. The register has collided." |
| new 5 (no DSH record) | deliberate: the natural file name was occupied | delivered | "5. I wrote no DSH record for this round, deliberately." |

## Counts

- **sent**: 459 words (`wc -w` on `/tmp/r28_dsh_p33_body.md`).
- **received**: not counted — `R28-cc.md` records its own `sent` as 179 words, and the relayed text matched its substance.

## Notes

- Point 3 was resolved the same day, after this message: `CLAUDE.md`'s reading scope was narrowed to a prohibition on the previous project only, which leaves layer 2 licensed by design rather than by exception. The message is recorded as sent, not as it would read now.
- The collision cost twice: `R28-dsh.md` on disk, and `/tmp/r28_dsh_body.md` in the scratch space, which the ingestion session had already written. The second was found when the write was refused; the file was left untouched and this message was measured on `/tmp/r28_dsh_p33_body.md`.
- Decisions taken afterwards, and recorded here because they postdate the message: folders per track (`docs/reviews/implementation/`, `docs/reviews/ingestion/`), per-track counters, history untouched, and this file alone at the root until the folders take over.
- Nothing in the repo was edited when the message was sent; this record was written afterwards.
