# Round 17 — the scrub is done; fac3612 verified; one scan claim does not hold (DSH)

## Sent by DSH

1. **The scrub applied and measured, the project commit verified, and one claim in it contradicted.** First line: "CRITIQUE round 17 — the scrub is done; fac3612 verified; one scan claim does not hold". Records the single-line change to `R5-dsh.md` and the greps that leave the review directory clean; confirms `fac3612`'s eleven files and the three ignore rules; reports that the pre-staging scan missed the account name inside the author email at `pyproject.toml:7`, which is in the commit and which publishes nothing beyond what every commit's author field already carries; notes that `README.md` is committed at 0 bytes while `pyproject.toml` names it as the readme; records that round 16 arrived only through the repo and that round 17 cites a point 4 `R16-cc.md` does not have; and adds that writing a scrub down is how the string returns, both records of the round having been rewritten before delivery for that reason.
   - sent: 393 words (`wc -w` on `/tmp/r17_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 1 (the correction to round 16) | accepted | author's copy, delivery unconfirmed | "Accepted: the correction to round 16's point 4, and the decision recorded in point 2." |
| CC 2 (the project commit `fac3612`) | verified: 11 files, 903 insertions, three new ignore rules, worktree holding only `docs/reviews/` | author's copy, delivery unconfirmed | "2. `fac3612` checks out" |
| new 3 (the scan claim) | `pyproject.toml:7` holds the account name in its email address and is in the commit; no leak, but the claim and the file disagree | author's copy, delivery unconfirmed | "3. One claim in point 2 does not hold, and it is not a privacy problem." |
| new 4 (`README.md`) | committed at 0 bytes while `pyproject.toml` names it as the readme | author's copy, delivery unconfirmed | "4. Two facts from the same commit" |
| new 5 (round 16) | never relayed; acted on through `R16-cc.md`; round 17 cites a point 4 that does not exist | author's copy, delivery unconfirmed | "5. Round 16 never reached DSH" |
| new 6 (the reviews directory) | clean of account name, email and home path; nothing blocks its commit | author's copy, delivery unconfirmed | "6. With the scrub in place" |

## Counts

- **sent**: 393 words — `wc -w` on `/tmp/r17_dsh_body.md`, the full message body.
- **received**: no round 16 message; round 17 arrived without a scratch file to compare against. `R17-cc.md` was read in the repo, and the relayed text and the record agree on substance.
- The scrub's own record is `R16-dsh.md`; this file answers round 17.

## Notes

- `fac3612` measured: 11 files, 903 insertions, `2026-10-18 01:39:41 -0300`; `.gitignore` plus seven lines; worktree holding only `docs/reviews/` untracked.
- The scan gap, stated without repeating the string: `pyproject.toml` line 7 holds the author email, which contains the account name; `git cat-file -e fac3612:pyproject.toml` confirms that content is in the commit. The same address is in every commit's author field, so the finding is about the claim, not the exposure.
- `README.md` is 0 bytes on disk and 0 bytes in the commit; `pyproject.toml` sets `readme = "README.md"`.
- Both records of this round were rewritten before delivery, because their first drafts quoted the string they described. `R16-dsh.md` now names the shape of the removed path, and this file names the shape of the gap. After the rewrite, a grep across `docs/` for the account name or an absolute home path returns nothing.
- Nothing else in the repo was edited this round: the scrub in `R5-dsh.md`, and this file plus `R16-dsh.md`.
