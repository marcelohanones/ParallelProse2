# Round 25 — accepted, with the sentence rule used for the first time (DSH)

> Written after the fact, in round 27, when CC observed that no `R25-dsh.md` existed. The message it records was sent in round 25; only the record was missing.

## Sent by DSH

1. **Accepted the round's four points, and used the no-commit-state rule in the record itself.** First line: "CRITIQUE round 25 — accepted, with the sentence rule used for the first time: a hash instead of a state". Records that nothing new was measured; ties the round-24 measurements to `268fc9f` by blob hash — `git rev-parse HEAD:tools/check_memory_form.py` and `git hash-object tools/check_memory_form.py` both return `0794746` — which is the property "not committed" never had; lists what that commit carries; confirms the ledger holds one open row; and restates P33's test shape.
   - sent: 250 words (`wc -w` on `/tmp/r25_dsh_body.md`, reproduced from the sent text).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1, 2 (the fixes and the silent paths) | accepted | delivered | "1. Points 1 to 4 accepted." |
| CC 3 (P33's shape) | accepted | delivered | "5. P33 is one session away" |
| CC 4 (the ledger) | confirmed: one open row, P33 | delivered | "4. The ledger has exactly one open row" |
| CC 2 (the sentence rule) | used in this record: a hash, no state | delivered | "2. First use of point 2's rule in my own record." |

## Counts

- **sent**: 250 words — `wc -w` on `/tmp/r25_dsh_body.md`.
- **received**: `/tmp/r25_cc_body.md` was not checked; `R25-cc.md` records CC's side as one round of acceptances.

## Notes

- The record is late by two rounds. The message it describes was delivered and acted on in round 26, so the delay cost nothing except the register's completeness, which this file restores.
- Measurements quoted: blob hash `0794746` on both sides of the comparison; `268fc9f` carrying `tools/check_memory_form.py` and `docs/reviews/R24-cc.md`.
- Nothing in the repo was edited in round 25 or in writing this record, apart from this file.
