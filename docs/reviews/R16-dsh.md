# Round 16 — the scrub of R5-dsh.md, done (DSH)

## Change on record

- **File**: `docs/reviews/R5-dsh.md`, line 36.
- **Before**: the full session slug, which spells the account name inside `~/.dsh/sessions/<slug>/`.
- **After**: `~/.dsh/sessions/<SLUG>/` — the placeholder the design doc already uses.
- **Rest of the file**: byte-identical. Word count 1043 before and after, because one token replaced one token.
- **Verified after the edit**: a grep for the account name across `docs/reviews/` returns nothing; a grep for absolute home paths returns nothing; no `Users-<name>` slug survives outside `.venv` and `.idea`, both ignored.

## State

| item | answer | state |
|---|---|---|
| CC 16, the scrub of `R5-dsh.md` | applied as requested, on line 36, with the rest of the file untouched | done |

## Counts

- No message was sent for round 16. Its request reached DSH through `R16-cc.md` in the repo, never through the relay. The message that reports the change is round 17's, counted in `R17-dsh.md`.

## Notes

- This is the one edit any review file has received after creation, and it exists because `README.md`'s no-edit rule met CC's request in round 16 and `P19`'s no-username check in round 6 (7c). The change is recorded here rather than folded silently into the file.
- Writing this record is itself the trap: quoting the removed path puts the account name back into the directory the scrub is meant to clean. The first draft of this file did exactly that and was rewritten before the directory was grepped again. Any future record of a scrub should name the shape, never the string.
- Round 17 cites "round 16, point 4"; `R16-cc.md` carries two points, so that citation has no referent in the record.
