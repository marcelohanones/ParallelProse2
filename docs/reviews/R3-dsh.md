# Round 3 — fixture designs (DSH)

## Sent by DSH

1. **Answer to the eight designs.** Answers "CRITIQUE round: ingestion fixture designs (docs/ingest_fixtures.md)".
   Items 1–8; M14's claim checked against the books — zero blocks in either book mix a direct text run with a
   text-bearing child, and the M14 count equals the D6 count in all four scopes (460 and 230 unchanged).
   Recommendations M15–M17.
   State: **author's copy, delivery unconfirmed** — `R3-cc.md` records the applied report, not this review.
2. **M15–M17 applied.** `docs/ingest_fixtures.md` written from scratch (eight designs); the spec gained the
   determinism and report clauses and three decision entries. State: **delivered**.
3. **Review of the draft for the revised round 3.** Eight changes listed, and two document defects found before
   they reached the round: four fixtures whose chapters had no navPoint, and an empty-wrapper sentence that
   contradicted M14. State: **delivered**.
4. **Answer to the revised draft, items 1–13.** Thirteen items; the finding that F6's expected error depended on a
   check order the spec did not state, and that `content_hash` left the report outside the identity. Recommendations
   M18–M19. State: **author's copy, delivery unconfirmed**.
5. **M18–M19 applied.** Check-order section added to the spec; F9b, F10 and F11 added to the fixtures.
   State: **delivered**.
6. **Answer to the round-3 update, items 1–7.** Seven items; the finding that verification never recomputed the file
   hashes, so F9 and F9b tested nothing. Recommendations M20–M22.
   State: **author's copy, delivery unconfirmed**.
7. **M20–M22 applied.** Verification now recomputes; rename order and temporaries entered the determinism section;
   F12 added, two package-level tests named. State: **delivered**.

## Notes

- Two of the three design defects found in this round were in the documents, not in the designs: a fixture cannot
  reach its defect if an earlier check fires first, and M18 exists because of that.
