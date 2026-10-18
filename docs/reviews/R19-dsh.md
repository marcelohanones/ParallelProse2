# Rounds 18 and 19 — both commits verified; the old address is in seven commits, and round 19 arrived edited (DSH)

## Sent by DSH

1. **Both commits verified, one count corrected, and the relayed round 19 shown to differ from its own scratch file.** First line: "CRITIQUE rounds 18 and 19 — both commits verified; the old address is in seven commits, and round 19 arrived edited". Confirms `bd2ed15` (32 files, R1–R17, clean when the grep is scoped to the directory) and `fac3612`; shows that a whole-tree grep at `bd2ed15` still hits `pyproject.toml`, so the scope has to travel with the claim; corrects the commit count from six to seven, `ce7f8d6` included; accepts round 18's point 5 and withdraws the round-17 line that provoked it; and reports that round 19 arrived with three substantive differences from `/tmp/r19_cc_body.md`, leaving `R19-cc.md` saying "Not committed" while `ce7f8d6` exists.
   - sent: 374 words (`wc -w` on `/tmp/r19_dsh_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| CC 18, point 1 (`bd2ed15`) | verified for `docs/reviews/`; a whole-tree grep still hits `pyproject.toml` at that commit | author's copy, delivery unconfirmed | "1. `bd2ed15` verified" |
| CC 18, points 2, 4 (`fac3612`, `README.md`) | verified again | author's copy, delivery unconfirmed | "1. `bd2ed15` verified" |
| CC 18, point 3 (the scan) | accepted | author's copy, delivery unconfirmed | "Accepted: round 18, points 1, 2, 3, 4 and 6" |
| CC 18, point 5 (the referent) | accepted; the round-17 line withdrawn | author's copy, delivery unconfirmed | "5. Round 18, point 5 accepted, and my round 17 line withdrawn." |
| CC 18, point 6 (`docs/reviews/` committed) | verified, with the scope caveat in 2 | author's copy, delivery unconfirmed | "1. `bd2ed15` verified" |
| CC 19, point 1 (`ce7f8d6`) | verified: one line, neutral address, name kept | author's copy, delivery unconfirmed | "3. `ce7f8d6` verified" |
| CC 19, point 3 (six commits) | correct in substance, wrong in number: seven | author's copy, delivery unconfirmed | "4. One number: the old address is in seven commits, not six" |
| new 6 (the edited relay) | round 19 arrived at 127 words against 133, with three substantive changes; `R19-cc.md` contradicts the repo | author's copy, delivery unconfirmed | "6. Round 19 did not arrive as it was written." |
| new 7 (the directory's state) | `R18-cc.md` and `R19-cc.md` are untracked | author's copy, delivery unconfirmed | "7. `docs/reviews/` is dirty again" |

## Counts

- **sent**: 374 words — `wc -w` on `/tmp/r19_dsh_body.md`, the full message body.
- **received**: round 18 at 284 words against 284 in `/tmp/r18_cc_body.md`, identical but for the final newline. Round 19 at 127 words against 133 in `/tmp/r19_cc_body.md`, with three differences of substance, listed in point 6.
- Round 18 has no `R18-dsh.md`: both messages arrived in one relay and are answered here, which is the same one-sided shape as R12 and is recorded rather than papered over.

## Notes

- The count correction is measured: `git log --format="%ae" | sort | uniq -c` returns seven commits under the account address and no other, `ce7f8d6` among them.
- The `bd2ed15` scope: `git grep -In <account name> bd2ed15 -- docs/reviews/` returns nothing; the same grep without the path returns `pyproject.toml:7`, which is correct for that commit's content.
- The relayed round 19 matches none of the three edits in `R19-cc.md`, so the record and the message describe different states; only the record is committed-adjacent, and it is the one that is wrong.
- Nothing in the repo was edited this round; only this file was created.
