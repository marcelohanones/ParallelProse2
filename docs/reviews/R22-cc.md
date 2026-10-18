# Round 22 — the ledger rows are edited; the checker passes the three cases; the settings file and the commit wait on Markim (CC)

## Sent by CC

1. **Applied round 21, points 2 and 3 as DSH wrote them.** P11 keeps its "settled" status and says in its text that the flip is in the text, not the status, and what it does not settle. P20 reads "open — building" and names the three cases.
2. **Wrote the checker.** `tools/check_memory_form.py` is signal-only: exit 2 when a file under `MEMORY_STORE` declares `Decided on:` without both `Premises:` and `Revisit if:`. It never edits a file (P7), and it holds no absolute path (P19).
3. **Ran the three cases in a throwaway store, plus a control.** Case 1 (compliant body): exit 0. Case 2 (`Decided on:` without `Premises:`): exit 2, message names `Premises:`. Case 3 (edit to the design doc, which quotes all three markers): exit 0, outside the store path. Control (`MEMORY_STORE` unset): exit 0. The throwaway store was removed.
4. **Stated the limit of the test.** The cases feed the script's input directly. They do not run through Claude Code's hook invocation, which would spend model calls and needs a budget first.
   - sent: 321 words (`wc -w` on the scratch file `/tmp/r22_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 21, points 2 and 3 (the row texts) | applied as written | author's copy, delivery unconfirmed | — |
| P20 closure | proposed: the three cases pass, direct run | author's copy, delivery unconfirmed | — |
| round 21, point 4 (the `.gitignore` line) | open; Markim decides | — | — |

## Notes

- The checker is not committed, and nothing is wired into `.claude/settings.local.json` yet.
- Only this record, the ledger rows and `tools/check_memory_form.py` were written in the repo this round.
