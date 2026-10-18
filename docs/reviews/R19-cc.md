# Round 19 — the email in pyproject.toml is changed to a neutral address (CC)

## Sent by CC

1. **Recorded Markim's decision on round 18.** First line: "CRITIQUE round 19 — the email in pyproject.toml is changed to a neutral address (CC)". The email in `pyproject.toml` is now `parallelprose2@example.com`; the name stays. The change is not committed.
2. **Measured after the change.** `git grep` over the worktree, outside `docs/reviews/`, finds no account name, and `docs/reviews/` has none.
3. **What it does not do.** Six commits in the history still carry the account address in the author field. Removing it means rewriting history, which is a separate decision and is not proposed.
   - sent: 133 words (`wc -w` on the scratch file `/tmp/r19_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 18, the email in `pyproject.toml` | decided by Markim: change to a neutral address; done in the worktree | author's copy, delivery unconfirmed | — |

## Notes

- Not committed. Markim commits the one-line change when he chooses.
- The address `parallelprose2@example.com` uses the reserved `example.com` domain, so it routes nowhere.
- Only this record and `pyproject.toml` were written in the repo this round.
