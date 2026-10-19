# Retriever–editorial contract ledger

This file is the ledger for the contract between the retriever and the editorial AI: what the editorial AI sends for a
new round, what the retriever returns, and how many queries a call may spend, and how the editorial AI holds the limit across the calls of a block. The format is agreed through CRITIQUE
with the editorial AI (`docs/documento_de_migracao.md`, the section on the output format and "A fronteira é um contrato
escrito"). Neither stage settles it alone.

Ingestion's side of the boundary is in `docs/ingest.md`: its output is fixed by item 6 there, and D4 in that file records
that ingestion is settled before this contract.

Precedence: this ledger governs over `docs/documento_de_migracao.md` where they differ, for the same reason as `docs/ingest.md`.

The two-graph architecture and its premises are in `docs/architecture.md`.

## Status

D1 is open; D2 is accepted as a proposal; D3 is accepted. Nothing in this file is implemented.

## Decisions

Each decision: what it settles, the premise that made it necessary, and what would invalidate it.

**D1 — proposed: the next-round request is hybrid.** It carries a query in text, written by the editorial AI, and closed
fields that constrain the search. Settles: what the editorial AI sends for a new round, and who writes the query. The
query is the search content; the closed fields are what the retriever's coverage accounting can act on. Premise: the
retriever has no language model and stays deterministic in its rules (premise 1 of the migration doc), and each kind of
input is used for what the retriever does well: semantic search for the query, coverage accounting for the fields.
Invalidated by: premise 1 changing to allow a language model inside the retriever, or the editorial AI being
unable to write a query without the retriever's help. The exact specification of the fields and of their values is open.

**D1 loop — proposed.** The retriever runs its fixed attempts first, with the question of the block. Then the editorial
AI judges whether the material is enough. If it is not, it sends a new request, and the retriever runs it with its own
rules. The loop stops in one of two ways: the editorial AI judges the material sufficient, or a hard limit is reached.
The editorial AI keeps its own round limit, read from the version's configuration.
The query cap (D3) is enforced by the retriever within each call; across calls, the editorial AI holds the limit.

**D2 — output unit.** Accepted as a proposal: the paragraph, delivered by default, with a neighbouring paragraph available
by its address when the editorial AI needs context. The details are in `docs/retriever_requirements.md`.

**D3 — query cap.** Accepted: the retriever enforces a cap on the queries it runs within a call, whatever their origin.
The value is a parameter of the version's configuration, and the unit is the query. The cap across the calls of a block
is held by the editorial AI, read from the same configuration. Settles: who counts the queries of a block, and what the
retriever enforces. Premise: the retriever keeps no state between calls (premise 4 of the architecture), so it cannot
count across calls. There is no hard limit independent of the editorial AI for the block as a whole.
Invalidated by: a requirement for a block-wide limit that does not depend on the editorial AI, which would require the
retriever to hold state or the request to carry a count.

## Editorial input (starting point, not settled)

This section sketches what the editorial AI needs in order to judge a block, so that the retriever's output is designed
against it. It is a proposal to be tested and discussed through CRITIQUE with the editorial AI.

What the editorial AI judges a block with, as a starting point:

- The block's thesis and question. They come from the editor, not from the retriever, and they are the criterion the
  judgment is made against.
- The units the retriever returned for the book, each with its address, and the ingestion version they come from.
- The trace of the calls made for the block, including which parts of the thesis received no material (open: how
  this is recorded).
- Optionally, the context around a unit, if the contract allows it (open).
- The editorial AI's own earlier requests for the same block, so that a new request does not repeat them.

What the editorial AI sends back, as a starting point: a hybrid request (D1, proposed), made of a query in text and closed
fields. The fields are open: they may cover which part of the thesis is unanswered, which side of the comparison has no
material, and which regions have already been visited.

Open: how the two sides are versioned together, and what the editorial AI may ask the retriever for beyond a new round.

## Editorial output (starting point, not settled)

The editorial AI produces two things, and they go in different directions:

- Toward the retriever: a request for another round, or nothing. As a starting point, this is the hybrid request
  described above (D1, proposed).
- Toward the rest of the project: the block's prose, with each claim linked to the unit that supports it. The link
  carries the unit's address and the sentence the claim rests on, so that the claim can be checked mechanically. Whether
  the claim is supported is a judgment of the editorial AI, and the output should mark it as one.

Open: the exact form of the claim-to-unit link; whether the output records which parts of the thesis the prose covers;
and how the judgment is marked in the output, so that a reader can see it is a judgment and not a mechanical check.
