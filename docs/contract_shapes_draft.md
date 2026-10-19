# Contract shapes: draft for the CRITIQUE round with the editorial AI

Status: draft. Not agreed. These shapes are the starting point for a CRITIQUE round with the editorial AI, and they are
to be replaced by what that round settles. The retriever implements only what is written here as agreed; everything
marked open waits for the round.

Decisions these shapes rely on: D1 (hybrid request: query in text plus closed fields, proposed), D2 (paragraph as the
output unit, accepted as a proposal), D3 (query cap within a call, held by the retriever; the cap across calls held by
the editorial AI).

## Request: editorial AI to retriever

One request per call. Fields marked `(open)` have no agreed form yet.

- `block_id`: identifier of the block the call serves.
- `index`: the index the call searches, as its three identities: `extraction_version` (the `version_id`),
  `vector_identity`, `cut_off_identity`.
- `query`: the new query, as text, written by the editorial AI. Empty or absent for a first call, which runs the fixed
  attempt order on the block's question.
- `fields`: closed fields that constrain the search. Their content is open. The candidates are:
  - `unanswered_parts`: identifiers of parts of the thesis that have no material yet (open: how parts are identified).
  - `sides_without_material`: which side of the comparison has no material (open: the side identifier).
  - `visited_regions`: paragraphs already covered, as addresses or address ranges (open: the form).

What the request does not carry: a round number (the editorial AI counts its own rounds), a depth or a cap (both are
retrieval configuration), and any text outside `query`.

## Response: retriever to editorial AI

One response per call.

- `block_id` and `index`: echoed from the request, so that a mismatch is visible.
- `attempts`: one entry per attempt, in order. Each has `kind` (`question`, `content_terms`, `no_framing`,
  `editorial_query`), the query text used, and the candidates it produced.
- `units`: the paragraphs returned, each with its address, its text, and its similarity. Ordered by similarity, ties by
  address. Only paragraphs above the cut-off and within the depth.
- `stop`: exactly one reason from the closed set (query cap for the call, coverage exhausted, no candidates, error), with
  the counters the reason depends on.
- `covered`: the paragraphs examined in this call, so the editorial AI can update `visited_regions` in its next request.

Open: whether `text` is always returned or only on request, whether `similarity` is returned to the editorial AI at all,
and whether `attempts` carries the candidates in full or only their addresses.

## Questions for the CRITIQUE round

1. Does the editorial AI need the paragraph text in every response, or are addresses enough for its judgment?
2. Does it need the similarity values, or only the order?
3. Does it need to know which attempt produced each unit?
4. How does the editorial AI identify parts of the thesis, so that `unanswered_parts` can be written without parsing text?
5. Does it need the context around a unit? If yes, is a neighbour request by address enough?
6. How should `visited_regions` be expressed: individual addresses, or ranges?
7. What must the response say when the call returns nothing, so that the editorial AI can tell an absence from a call
   that did not run?
