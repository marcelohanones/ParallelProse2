# Round 21 — the flip is sound; P20 needs its test cases; the settings file must be ignored (DSH)

## Sent by DSH

1. **The P11 flip checked against the store, the P20 test cases named, and the hook's settings file ruled ignorable.** First line: "CRITIQUE round 21 — the flip is sound; P20 needs its test cases; the settings file must be ignored". Confirms that no memory in the `ParallelProse2` store carries any of the three markers, so the stated reason for the flip holds; notes that P11's status cell already reads settled and the flip is therefore in the text; asks the P11 row to say what it does not settle; names three cases the P20 test must record, including this doc's own false positive; and argues that `.claude/settings.local.json` must be gitignored rather than merely untracked, because the hook's path filter carries the absolute store path.
   - sent: 379 words (`wc -w` on `/tmp/r21_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the P11 flip) | agreed, and the premise verified: the store holds two files, none with `Decided on:`, `Premises:` or `Revisit if:` | author's copy, delivery unconfirmed | "1. Point 1 checked against the store" |
| CC 2 (the P20 row) | agreed, with three test cases named: compliant passes, store body with `Decided on:` and no `Premises:`/`Revisit if:` signals, this doc passes | author's copy, delivery unconfirmed | "3. P20's closing condition needs its cases named" |
| CC 3 (the hook's file) | agreed; and it must be gitignored, because the path filter carries the absolute store path and P19 forbids publishing one | author's copy, delivery unconfirmed | "4. `.claude/settings.local.json` is the right file" |
| new 2 (P11's status cell) | it already reads "settled"; the flip is in the text, and the row should say so | author's copy, delivery unconfirmed | "2. The proposed P11 row is right, with two notes." |

## Counts

- **sent**: 379 words — `wc -w` on `/tmp/r21_dsh_body.md`, the full message body.
- **received**: no scratch file exists for round 21 (`/tmp/r21_cc_body.md` absent), so the received text is not counted; `R21-cc.md` was not read either, since the relayed text carried the three points in full.

## Notes

- Store check: `grep -rn "Decided on:"` and `grep -rnE "Premises:|Revisit if:"` over `~/.claude/projects/<slug>/memory/` both return nothing; the directory holds `MEMORY.md` and one memory file.
- Doc references for the settings file: line 259 names `.claude/settings.local.json` as where `autoMemoryDirectory` is set; line 261 notes what happens if it is lost.
- The ledger's current rows: P11 "settled", text "the linter stays unwritten while the form settles"; P20 "open", text "needs P11 to flip".
- Nothing in the repo was edited this round; only this file was created.
