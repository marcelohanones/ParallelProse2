# Retriever milestone 1: dense channel only

Status: proposed. Scope and acceptance criteria for the first build of the retriever. It depends on the decisions in
`docs/retriever_requirements.md` (accepted decisions for the dense channel), D7 and D9 in `docs/ingest.md`, and the
contract ledger in `docs/contract_retriever_editorial.md`.

## Goal

Given the index of one book and a request, run the first three attempts of the fixed order on the dense channel, return
the paragraphs above the cut-off within the configured depth, and record a trace whose stop reason is one of the closed
set. Nothing else.

## In scope

- Exact cosine search over the paragraph vectors of one book.
- Attempts 1 to 3 of the fixed order: the question as written, the question with only its content terms, and the
  question without its interrogative framing. Each is embedded with the same model and searched over the same vectors.
- A configured depth (per retrieval configuration), applied after ranking.
- The cut-off, provisionally 0.30, until the D9 calibration has run for the book's extraction version and model.
- Ties in similarity ordered by address.
- The stop reasons of `retriever_requirements.md`: query cap for the call, coverage exhausted, no candidates, error.
- The trace record, one per attempt, with the minimum fields needed by the stop logic (see below).
- Verification of each returned address against the extraction version and its content hash (D8).

## Out of scope

- Attempt 4 (variants from the book's vocabulary). It needs the vocabulary artifact, which is not yet specified.
- Decomposition of the question into parts (feature 4 of the migration doc).
- Any lexical channel (BM25). The fixed order uses the dense channel only.
- Neighbouring paragraphs on request. The output unit is the paragraph; neighbours come later.
- The editorial loop, the round limit and the hybrid request format (D1). Milestone 1 takes one call with a question.
- Calibration (D9). Milestone 1 uses 0.30 and records that it is provisional.

## Parts that can start now, without vectors

- **Request and trace schema.** Field names, types and the closed set of stop reasons. The trace fields are provisional
  in milestone 1 and are replaced when the contract fixes them.
- **Stop logic.** The decision of when a call stops, given counters and candidate sets. It is tested against fixture data:
  a candidate set, a depth, a cut-off, a set of covered paragraphs and a query cap.
- **Coverage accounting.** Given the candidates of each attempt, which paragraphs have been examined. Tested on fixtures.

These can be built and tested without a vector store, since their inputs are plain records.

## Parts that depend on vectors

- The vector artifact of the book, with its descriptor and its identity (D7).
- Query embedding with the same model, one call per attempt.
- Exact cosine ranking, with ties ordered by address.
- The end-to-end run on one book.

## Acceptance criteria

1. **Determinism.** The same request against the same index identity returns the same paragraphs, in the same order,
   with the same trace, on two runs.
2. **Depth.** At most the configured depth is returned per attempt, and the cut-off is applied before the depth limit
   is reported.
3. **Cut-off.** No returned paragraph has a similarity below the cut-off recorded in the retrieval configuration.
4. **Ties.** Paragraphs with equal similarity are ordered by address.
5. **Addresses.** Every returned address resolves to a paragraph whose version and content hash match (D8). A mismatch
   is refused, not returned.
6. **Stop reasons.** Each call ends with exactly one reason from the closed set, and the record carries the counters the
   reason depends on.
7. **Query cap.** The cap for the call is enforced across the attempts of that call, and is not applied across calls.
8. **Scope.** No attempt uses the vocabulary artifact, a lexical channel or a language model.

## Open for this milestone

- The provisional trace fields, to be replaced once the contract fixes them.
- The retrieval configuration format, which holds depth, cut-off reference, attempt order, query cap and embedding model.
