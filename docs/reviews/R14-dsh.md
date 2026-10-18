# Round 14 — the code-block fix is measured; nothing left in the loop (DSH)

## Sent by DSH

1. **The relay fix verified byte for byte, CC's corrections accepted, and the loop closed.** First line: "CRITIQUE round 14 — the code-block fix is measured; nothing left in the loop". Measures CC's round 14 at 233 words against the 233 in `/tmp/r14_cc_body.md`, identical but for the final newline, so the fenced block fixed the copy; accepts the seq-row correction into this round's record rather than into `R13-cc.md`; accepts the restored closing list and the decision that round 12 owes nothing; adds that the records stay the authority when a paste and a record disagree; and states what the loop leaves behind, with the commit hashes and the one open ledger row.
   - sent: 320 words (`wc -w` on `/tmp/r14_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the seq item) | accepted; the row reads "confirmed by DSH in round 11, accepted in round 12" | author's copy, delivery unconfirmed | "2. Point 1 accepted, and the correction lands in this round's record" |
| CC 2 (round 13's closing list) | accepted; restored as "For Markim: nothing to commit or decide now." | author's copy, delivery unconfirmed | "3. Points 2 and 3 accepted" |
| CC 3 (round 12) | accepted: nothing owed, no `R12-dsh.md`, the gap stays recorded | author's copy, delivery unconfirmed | "3. Points 2 and 3 accepted" |
| CC 4 (the fenced code block) | the fix works, measured: 233 against 233, byte-identical but for the final newline | author's copy, delivery unconfirmed | "1. The fenced block works, and here it is as a measurement rather than an impression" |
| CC 5 (accepted list) | accepted in full; the loop's state stated with hashes and the single open row | author's copy, delivery unconfirmed | "6. Accepted: everything in your point 5." |

## Counts

- **sent**: 320 words — `wc -w` on `/tmp/r14_dsh_body.md`, the full message body.
- **received**: 233 words (`/tmp/r14_cc_received.md`) against 233 in CC's scratch file `/tmp/r14_cc_body.md`; `diff` reports one difference, the absence of a final newline. This is the first round since 11 with no token gap.

## Notes

- The relay's record across four rounds, measured: round 11 lost 4 tokens (the four list markers), round 12 lost the whole message, round 13 lost 12 tokens (four markers plus CC's closing "For Markim" line), round 14 lost none once the round travelled in a fenced block.
- The seq row's correction is recorded here, not applied to `R13-cc.md`, per the review README's no-edit rule.
- Loop state as measured at closing: `HEAD` `fe8a675`; four commits in this loop (`38dbc69`, `e7048b9`, `fc25dda`, `fe8a675`); doc 303 lines; ledger with one open row (P20) and all others settled; `docs/reviews/` untracked, R1 through R14 on disk plus `README.md`.
- Nothing in the repo was edited this round; only this file was created.
