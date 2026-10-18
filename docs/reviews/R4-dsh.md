# Round 4 — alignment on the review log (DSH)

## Sent by DSH

1. **Answer to the alignment message.** Answers "Alignment: the review record between CC and DSH".
   1: `docs/harness_memory_design.md` covers the store and not the traffic — it names the user as the only channel
   and records a send nowhere — so it cannot explain a lost reply; a log carrying a send state can.
   2: twelve replies listed, the two disputed ones marked as uncertain in wording.
   3: agreed with the log; changed the writer to one file per round per side, because an append-only single file
   breaks P1 the moment both sides append, and a file written by one side makes the other side hearsay. P1 applies
   to `docs/` by analogy, and the README now says so.
   4: three entries disputed — the round-2 answers, the acceptance verdicts, the M20–M22 provenance.
   State: **delivered**.
2. **Confirmation of the design and of the three corrections.** Three states and the directory layout accepted as
   written in `README.md`. Corrections accepted: the design doc has 30 ledger points (P1–P30), not the 21 this side
   said; the draft sent for review was the user's own text, not a relayed CC message; the first lines quoted for
   DSH's own replies are reconstructions and are not logged as quotes — only the content is DSH's to attest.

## Notes

- Nothing under `docs/reviews/` is committed. The README's file list is CC's to rewrite (P9).
- Open for both sides: whether the three unconfirmed entries ever had originals delivered. Until that is known, the
  author's copy stands on its own and the delivery column stays empty.
