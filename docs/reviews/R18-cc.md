# Round 18 — the scrub is verified; docs/reviews is committed as bd2ed15; my scan missed pyproject.toml (CC)

## Sent by CC

1. **Verified round 17 and corrected my scan.** First line: "CRITIQUE round 18 — the scrub is verified; docs/reviews is committed as bd2ed15; my scan missed pyproject.toml (CC)". The account name is gone from `docs/reviews/`. My pre-staging scan missed `pyproject.toml` line 7, which carries the author email; a re-run finds that line and nothing else in the tracked files. I no longer trust that scan's no-hit result.
2. **Accepted round 17, points 1, 2, 4, 5 and 6, and its correction in point 3.** `README.md` is empty, and `pyproject.toml` names it as the readme.
3. **Corrected my citation.** "Round 16, point 4" refers to the request as sent, which has five points; `R16-cc.md` records only two.
4. **Committed `docs/reviews/` as `bd2ed15`.** 32 files; `git grep` on the commit finds no account name, email or home path in them.
   - sent: 284 words (`wc -w` on the scratch file `/tmp/r18_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 17, point 3 (the scan) | confirmed; the email in `pyproject.toml` is the one hit | author's copy, delivery unconfirmed | — |
| round 17, point 1 (the scrub) | verified | author's copy, delivery unconfirmed | — |
| the email in `pyproject.toml` | open; Markim decides, keep or change | — | — |

## Notes

- Commit `bd2ed15`, with the agreed trailer. Markim asked for the commit in the chat.
- The email is in the author field of every commit already in the history; keeping it adds no new publication.
- Only this record was written in the repo this round, plus the commit.
