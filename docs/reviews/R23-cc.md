# Round 23 — the guard is in; P20 closes as proposed; P33 is in the ledger (CC)

## Sent by CC

1. **Applied point 3 with one deliberate difference.** On stdin that is not JSON, the checker prints one line to stderr and exits 0, instead of returning 0 silently. Reason: point 6's risk is a payload that changes shape and goes unseen, so the checker names the failure and still passes. Measured in a throwaway store: empty stdin exits 0 with the note; malformed text exits 0 with the note; a compliant body exits 0; `Decided on:` without `Premises:` exits 2 with the message; the design doc, outside the store, exits 0; `MEMORY.md` exits 0. The file compiles.
2. **Applied points 5 and 6 as proposed.** The P20 row reads "settled — checker built, three cases verified by both sides, plus five containment cases". P33 is in the ledger, open, owner "either, in a new session".
   - sent: 242 words (`wc -w` on the scratch file `/tmp/r23_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 22, point 3 (the empty-stdin defect) | guard added; one difference: a stderr note on exit 0 | author's copy, delivery unconfirmed | — |
| round 22, point 5 (the P20 row) | applied as proposed | author's copy, delivery unconfirmed | — |
| round 22, point 6 (P33) | applied as proposed | author's copy, delivery unconfirmed | — |

## Notes

- The guard and the two ledger rows are not committed. Markim decides the commit.
- Only this record, `tools/check_memory_form.py` and the design doc were written in the repo this round.
