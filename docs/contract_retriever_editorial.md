# Retriever–editorial contract ledger

This file is the ledger for the contract between the retriever and the editorial AI: what the editorial AI sends for a
new round, what the retriever returns, and how many queries a block may spend. The format is agreed through CRITIQUE
with the editorial AI (`docs/documento_de_migracao.md`, the section on the output format and "A fronteira é um contrato
escrito"). Neither stage settles it alone.

Ingestion's side of the boundary is in `docs/ingest.md`: its output is fixed by item 6 there, and D4 in that file records
that ingestion is settled before this contract.

Precedence: this ledger governs over `docs/documento_de_migracao.md` where they differ, for the same reason as `docs/ingest.md`.

## Status

All three decisions are open. Nothing in this file is implemented.

## Decisions

Each decision: what it settles, the premise that made it necessary, and what would invalidate it.

**D1 — the editorial AI sends a closed directive, not text.** Settles: who writes the next-round request. Premise: the
retriever stays deterministic (premise 1 of the migration doc). Invalidated by: premise 1 changing to allow an LLM inside
the retriever.

**D2 — output unit.** Open until the editorial AI's requirements are written.

**D3 — per-block query cap.** Open until the adaptive design exists.
