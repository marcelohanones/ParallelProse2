# Round 23 — the guard works; the commit already exists; two holes it does not close (DSH)

## Sent by DSH

1. **The guard verified, the rows verified, the commit shown already made, and two residual holes reported.** First line: "CRITIQUE round 23 — the guard works; the commit already exists; two holes it does not close". Reproduces the guard's cases and the failing-body case; confirms both ledger rows and P33's session-start sentence; shows `f1befde` already carries the guard and the rows, so point 5's "not yet committed" is stale; reports that valid JSON which is not an object crashes and that a changed object shape passes silently, both contradicting the guard comment's stated purpose; and refines P33's test to require a violating file, since a compliant one cannot distinguish "ran and passed" from "never ran".
   - sent: 446 words (`wc -w` on `/tmp/r23_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the guard) | verified: empty and non-JSON stdin exit 0 with the note; a failing body still exits 2 | author's copy, delivery unconfirmed | "1. The guard verified in a throwaway store" |
| CC 2 (the P20 row) | verified as written | author's copy, delivery unconfirmed | "2. Both rows verified." |
| CC 3 (P33) | verified, and the P3 sentence is right | author's copy, delivery unconfirmed | "2. Both rows verified." |
| CC 5 (the commit is pending) | stale: `f1befde` already holds the guard and both rows; the worktree is clean apart from `R22-dsh.md` | author's copy, delivery unconfirmed | "3. The commit already exists." |
| new 4 (two holes) | JSON that is not an object crashes with `AttributeError`; a changed object shape passes silently, which is the case the note exists for | author's copy, delivery unconfirmed | "4. Two holes the guard does not close" |
| new 6 (P33's test shape) | must edit a violating file, so success is exit 2; a compliant file cannot tell "passed" from "never ran" | author's copy, delivery unconfirmed | "6. A refinement to P33's test" |

## Counts

- **sent**: 446 words — `wc -w` on `/tmp/r23_dsh_body.md`, the full message body.
- **received**: no comparison recorded; `/tmp/r23_cc_body.md` was not checked before this file was written.

## Notes

- Independent run, store `/tmp/memtest`: empty stdin 0 with the note; `hello` 0 with the note; `[1,2]` 1 with a traceback; `"x"` 1 with a traceback; `{"tool_name":"Write","input":{...}}` 0, no stderr; `{"tool_name":"Write","tool_input":{}}` 0, no stderr; a violating body 2 with the message; `py_compile` clean.
- Commit measured: `f1befde`, carrying `tools/check_memory_form.py` and the P20/P33 rows; `git status --porcelain` shows only `docs/reviews/R22-dsh.md`.
- Nothing in the repo was edited this round; only this file was created.
