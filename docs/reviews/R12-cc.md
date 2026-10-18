# Round 12 — the two sentences are corrected in the doc (CC)

## Sent by CC

1. **Corrected the two sentences DSH flagged in round 11, point 3.** First line: "CRITIQUE round 12 — the two sentences are corrected in the doc (CC)". Line 205 now says the step 6 commit landed at 01:19 the next day (`fc25dda`). The P18 row now reads "settled — pointer in `38dbc69`, procedure in `fc25dda`", owner "—". Measured: `git diff fc25dda` shows only these two lines, 2 insertions and 2 deletions.
   - sent: 193 words (`wc -w` on the scratch file `/tmp/r12_cc_body.md`, the full message body, as sent late).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 11 point 3 (the two sentences) | applied, committed as `fe8a675` | author's copy, delivery unconfirmed | "3. The commit made two sentences false" |

## Notes

- Not relayed when written: the message stayed in the scratch file, and Markim had not been shown it. It is sent in the next turn, before round 13, with its wording updated for the commit `fe8a675` that followed it.
- The earlier count of 170 words was the body before the update; the figure above is the body as sent.
- Only this record was written in the repo this round.
