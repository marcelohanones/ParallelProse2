# Round 26 — Markim reverses the untracking: docs/reviews stays versioned; the implementation closes except P33 (CC)

## Sent by CC

1. **Recorded Markim's decision.** `docs/reviews/` stays versioned. The ignore rule added in round 25's discussion was removed by Markim; the directory is tracked as before, 45 files, from `bd2ed15` on. Nothing is removed from the history, and no hash changes.
2. **Closed the implementation except P33.** The ledger's only open row is P33, which waits on a new Claude Code session that edits a violating file in the store, with the exit code and stderr recorded.
   - sent: 164 words (`wc -w` on the scratch file `/tmp/r26_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| the untracking (round 25 discussion) | reversed by Markim; `docs/reviews/` stays versioned | — | — |
| P33 | open; new session | — | — |

## Notes

- Only this record was written in the repo this round.
- The `.gitignore` in the working tree differs from HEAD by one trailing blank line; it is Markim's edit and is left as is.
