# Round 22 — the three cases reproduce; one defect the control never reached; the wiring already exists (DSH)

## Sent by DSH

1. **Both ledger rows confirmed, the three cases reproduced with five more, one defect found, and the wiring shown to be already in place.** First line: "CRITIQUE round 22 — the three cases reproduce; one defect the control never reached; the wiring already exists". Re-runs the checker in a throwaway store and records the exit codes; adds `MEMORY.md`, the prefix sibling, the store's parent, the bold marker and the missing file as extra containment cases, all correct; reports that empty or malformed stdin raises `JSONDecodeError` uncaught, exit 1, which the `MEMORY_STORE`-unset control never reached; shows that `.claude/settings.local.json` is already wired, ignored and uncommitted, and that `tools/check_memory_form.py` is committed at `34c4b41`; closes P20 on the guard landing and proposes P33 for the live invocation.
   - sent: 481 words (`wc -w` on `/tmp/r22_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the rows) | as described; P11 carries the flip in its text and names the P12 scope | author's copy, delivery unconfirmed | "1. The rows are as described." |
| CC 3 (the three cases) | reproduced exactly, plus five containment cases, all correct | author's copy, delivery unconfirmed | "2. The three cases reproduce independently" |
| new 3 (the stdin defect) | empty or malformed stdin raises uncaught, exit 1; the control returns before the parser | author's copy, delivery unconfirmed | "3. One defect, and the control could not have caught it." |
| CC 5 (Markim's three decisions) | all three already done in the repo: ignored at `.gitignore:23`, wired in `.claude/settings.local.json`, `tools/` committed at `34c4b41` | author's copy, delivery unconfirmed | "4. The wiring already exists" |
| new 6 (P33) | the hook's live invocation is unmeasured; proposed as P33 | author's copy, delivery unconfirmed | "6. What that does not buy is the hook firing." |

## Counts

- **sent**: 481 words — `wc -w` on `/tmp/r22_dsh_body.md`, the full message body.
- **received**: 321 words in CC's scratch file `/tmp/r22_cc_body.md`; the relayed text was not transcribed to a file this round, so no comparison is recorded.

## Notes

- Independent run, store `/tmp/memtest`, payloads on stdin: compliant 0; missing `Premises:` 2 with the field named; missing `Revisit if:` 2 with the field named; no markers 0; `MEMORY.md` 0; prefix sibling 0; store parent 0; genuinely outside 0; `**Decided on:**` bold 2; `MEMORY_STORE` unset 0; missing file 0; relative path 0.
- The defect's reproduction: `printf '' | MEMORY_STORE=/tmp/memtest python3 tools/check_memory_form.py` → exit 1 with a traceback from line 58.
- Repo state as measured: `HEAD` `8fd5e23`; `34c4b41` holds the checker; `.gitignore` line 23 is the settings entry; worktree clean.
- Nothing in the repo was edited this round; only this file was created.
