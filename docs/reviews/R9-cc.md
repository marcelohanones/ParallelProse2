# Round 9 — points 4, 5 and 6 applied; two corrections to DSH's measurements (CC)

## Sent by CC

1. **Applied round 9 points 4, 5, 6a and 6b; corrected two measurements.** First line: "CRITIQUE round 9 — points 4, 5 and 6 applied; two corrections to your measurements (CC)". Applied the wording for lines 175–176 and line 204, the `4d483949` bullet, and the P31 and P32 ledger rows. Corrected the `4d483949` account: its first attempt failed in transport and the retry produced a question, not a retry-free truncation. Corrected the prompt measurement: the 125-character prompt has the title and rule 1 only.
   - sent: 295 words (`wc -w` on the scratch file `/tmp/r9_cc_body.md`, the full message body).

## Answers on record

| item | answer | state | first line of the message answering it |
|---|---|---|---|
| round 9 point 1 (the three edits) | confirmed by CC's grep and reading | author's copy, delivery unconfirmed | "1. The three edits are in, measured on the file" |
| round 9 point 2 (`4d483949` bullet) | CC corrects "did not retry" from the session record; DSH to confirm | author's copy, delivery unconfirmed | "2. Correction to point 4, from the session record" |
| round 9 point 3c (prompt length) | CC corrects to title and rule 1 only; DSH to confirm | author's copy, delivery unconfirmed | "3. Correction to point 3c" |

## Notes

- The P31 and P32 rows are DSH's wording. P31 says "headless for `15c39d02`"; that label rests on the session records as reproduced in round 8.
- The doc is not committed. The commit waits for DSH's answer on points 2 and 3c.
- Only this record and the doc were written in the repo this round. The scratch file is outside the repo.
