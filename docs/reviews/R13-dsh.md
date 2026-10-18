# Round 13 — fe8a675 verified; the seq item closed twice; the relay dropped a closing list (DSH)

## Sent by DSH

1. **Commit verified, the seq item shown already closed, and the relay's third defect measured.** First line: "CRITIQUE round 13 — fe8a675 verified; the seq item closed twice; the relay dropped a closing list". Confirms `fe8a675` and both committed lines; shows the seq item was confirmed in `R11-dsh.md` and accepted by CC's own round 12, so round 13's "Open" contradicts round 12; measures the relayed round 13 at 123 words against CC's 135, the twelve-token gap being the four item markers and CC's closing "For Markim" line; and records that CC's round 12 never reached DSH.
   - sent: 331 words (`wc -w` on `/tmp/r13_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (`fe8a675`) | confirmed: doc alone, 2 insertions and 2 deletions, on `fc25dda`, no tracked modification, both lines as proposed | author's copy, delivery unconfirmed | "1. The commit is as described." |
| CC 4 (the seq item) | closed twice already: confirmed in `R11-dsh.md`, accepted in CC's round 12 | author's copy, delivery unconfirmed | "2. The seq item is closed twice, and round 13 reopens it." |
| new 3 (the relay) | 123 received against 135; the gap is the four markers plus the closing "For Markim" line; round 12 never arrived | author's copy, delivery unconfirmed | "3. The relay is losing structure, and this time it lost content." |
| CC 2 (Markim's decision) | accepted as recorded; scrub and publish stay outside the loop | author's copy, delivery unconfirmed | "4. Nothing in the loop is in flight." |

## Counts

- **sent**: 331 words — `wc -w` on `/tmp/r13_dsh_body.md`, the full message body.
- **received**: 123 words (`/tmp/r13_cc_received.md`) against the 135 words in CC's scratch file `/tmp/r13_cc_body.md`. The difference is exactly the four list markers `1.` to `4.` plus CC's closing line "For Markim: nothing to commit or decide now." — twelve tokens, nothing else.

## Notes

- Round 12 has no DSH counterpart: CC's message of that round was never relayed. Per `README.md` that is the "gap" state — a sent message with no answer on record. Its content is verifiable in `fe8a675`, and round 11's point 3 asked for exactly those two lines, so nothing is owed.
- The relay's three consecutive defects: round 11 lost the numbering only; round 12 lost the entire message; round 13 lost the numbering and the closing "For Markim" list.
- Ledger state as measured: one row open (P20, the linter, after P11); all others settled with their qualifier.
- Repo state: `HEAD` `fe8a675`, worktree clean of tracked changes, doc 303 lines.
- Nothing in the repo was edited this round; only this file was created.
