# Retriever requirements

Status: draft. Conceptual. The boundary's decisions are in `docs/contract_retriever_editorial.md`, and the component's
place in the architecture is in `docs/architecture.md`. Adaptability is a property of the behaviour described here, so
it is defined after these requirements, not before.

## Purpose

Given the index of one book and a request, return the text units that the index can offer for the block's question or for the query in the request,
each with its address (the unit is the paragraph, D2, accepted as a proposal), together with a trace that lets the editorial AI tell "the book does not address this" from
"this form of the question was not tried".

## Scope

- No judgment of meaning and no judgment of sufficiency. Deciding whether the material is enough belongs to the
  editorial AI.
- No synthesis and no prose.
- No state kept between calls. Anything a later call needs from an earlier one arrives in the request.

## Output of a call

Starting point. This section is a proposal to be tested and discussed before anything is built on it, except the output
unit, which is the paragraph (D2, accepted as a proposal). It describes what a call returns. What the editorial AI
consumes from that return is defined in the contract ledger, not here.

A call returns, as a starting point:

- Paragraphs with the addresses assigned by ingestion (D2, accepted as a proposal).
- The ingestion version the passages come from.
- A trace of the call (see below).

## Coverage

Coverage is about the book, not about relevance: which parts of the book the call has examined. A call that returns few
passages can still have covered a lot of the book, and a call that returns many passages from one region has covered
little.

## Stopping

A call stops for one of a closed set of reasons. The reason is always recorded; a call never stops silently.

- **Query limit reached:** the cap for the call (D3) has been used, counted over every query the retriever runs in that
  call, whatever its origin.
- **Coverage exhausted:** every paragraph of the book has appeared among the candidates of some attempt. A candidate is a
  paragraph returned within the configured depth and above the cut-off. Being scored by a query does not count as examined.
- **No candidates:** no unit reached the minimum cosine similarity. The cut-off is a parameter recorded with the version;
  its provisional value is 0.30, until the calibration of ingestion (decision D9) has run for the book's version and model.
- **Error:** a technical failure, with its own code.

Each record carries the reason, the counters (queries made, and paragraphs examined out of the total), and the parameters
that set the limit: the version configuration, and the cap for the call (D3).
A stop that depends on whether the material answers the thesis is not a reason: that judgment belongs to the editorial
AI.

## Trace

One record per attempt: what was attempted, what it returned, and why the call stopped. The trace must let the editorial
AI distinguish an absence from an attempt that was not made.

## Adaptability

**What does adapting mean here?** It means that the way a call searches the book can change according to what the call
already knows. It does not mean that the retriever understands the question. The change is a fixed rule over the call's
own inputs, not a judgment about meaning.

**Where does adaptation come from?** Three sources could feed it, and they need different things:

- The question itself, varied by rule, with no reading of the book.
- The book's index: its vocabulary and the positions of its passages, both produced by ingestion.
- The results of earlier attempts inside the same call. This is the source most likely to reinforce a region already
  found, because the next attempt tends to go where the last one went. It is the one that needs the most care.

**Where does adaptation happen?** Inside a call, the retriever may decide how to search, as a rule. Between calls, the
editorial AI asks for another round with a query and closed fields, and the retriever only receives the request. Adaptation between
calls is not part of this section.

**What counts as adapting well?** Not finding the most relevant passage. The hard case is a thesis with two distant
parts: the search must reach different regions of the book, not just find more passages similar to the first one it
found. So adaptation is judged by coverage, and a call that adapts must say which parts of the book it reached.

**What must adaptation respect?** Within a call it must be deterministic, so that repeating a request gives the same
result, and the cache and the repeatability of the trace depend on it.

**How is it built?** Adaptation is an internal orchestration of pieces the retriever already has or can use: the dense
channel, the positions and addresses that ingestion produces, the book's vocabulary extracted at ingestion, and
decomposition by grammatical structure. The orchestration decides, from the call's own state, which piece to use next,
when to stop, and what to record. The aim is to get the most out of those pieces, not to add a new one for each
difficulty.

## Determinism

The same request against the same ingestion version returns the same passages, in the same order, with the same trace.
Adaptation inside a call is part of this: it is a fixed rule over the call's own inputs.

## Requests

The only way a call differs from an earlier one is through the request. The retriever uses nothing it did not receive
in that request. The request names the ingestion version that identifies the index it searches, and the index searched is
the one that version identifies.

## Accepted decisions for the dense channel

These decisions were accepted in discussion. Each one is recorded with the reason it was taken.

- **Embedding model.** Starting point: `text-embedding-3-small` (OpenAI), which is multilingual and the cheapest in its
  family. Alternative to test: `text-embedding-3-large`, only if a test on the book in use shows a gain that justifies
  the cost. The model's name, dimensions and price are to be confirmed in the current documentation before fixing.
  The model name, and its version where the API offers one, are part of the version identity.
- **Indexed unit.** The paragraph, one address per paragraph. No splitting of long paragraphs in this version, because a
  split would create child addresses that the ingestion does not define. Very short paragraphs are reported by
  ingestion; they are not dropped from the index.
- **Index type.** Exact search. A book has a few hundred paragraphs, so the cost is negligible, and the order of results
  is deterministic by construction. Paragraphs with equal similarity are ordered by their address, so the order holds
  even on ties.
- **Depth.** A parameter of the retriever's configuration, fixed per version and recorded in the version identity and in the trace. The cut by the character budget happens after
  ranking, at delivery, not inside the search.
- **Metric.** Cosine similarity. OpenAI embeddings are returned normalized, so the dot product gives the same ranking,
  and the query needs no prefix.
- **Vectors as an artifact.** The paragraph vectors are an artifact of ingestion, with their own descriptor, and they
  enter the version identity together with the model name and version. The query is embedded in each call with the same
  model. A result may be cached by the key of model, query and ingestion version.
- **Addresses.** The address is the paragraph's position from ingestion, and it is always cited together with the
  ingestion version. A content hash of the normalized text is stored as a check: an address that does not match its
  version and hash is refused.
- **Coverage region.** The paragraph. Chapters are a derived view in the report, not the unit of coverage.
- **Cut-off.** A cosine similarity parameter, calibrated by ingestion from the book's own paragraphs (decision D9 in
  `docs/ingest.md`). Until the calibration has run, the provisional value is 0.30.
- **Output unit.** The paragraph, delivered by default. A neighbouring paragraph may be requested by its address when the
  editorial AI needs context. This resolves D2 in the contract ledger as an accepted proposal.
- **No language model inside the retriever.** The retriever contains no language model. Next-round requests arrive from
  the editorial AI as a query in text and closed fields (D1, proposed). The embedding model that vectorizes queries is
  part of the search, not a language model. The multi-query variant, which would put a language model inside the
  retriever, is therefore out of this component.
- **Query cap (D3).** The retriever enforces a cap on the queries it runs within a call, whatever their origin. The value
  is a parameter of the version's configuration. The cap across the calls of a block is held by the editorial AI, because
  the retriever keeps no state between calls.
- **Attempt order (first version), held as data.** The order is a list in configuration, read once at the start of a
  call, and the whole list is recorded in the version identity. Changing the order is therefore a configuration change
  that produces a new version; it is never a silent edit to the code. The first version's list, the same for every block:
  (1) the question as written, at the declared depth; (2) the question with only its content terms; (3) the question
  without its interrogative framing; (4) variants built from the book's vocabulary. The vocabulary artifact is mandatory,
  and ingestion specifies it; the slot is reserved now, and the list is complete only once that specification exists.
  An attempt is skipped only when all its candidates lie in paragraphs already covered. The
  stopping rules above apply after each attempt. A query from the editorial AI, when there is one, runs after this list, as
  its own call.

## Proposed, not accepted

- **Filter, not direction, in the first version.** Results from earlier attempts only remove later attempts whose
  candidates are all covered; they never choose what to search next. This is a design decision, not a parameter: moving
  to direction makes each step depend on the previous one, which changes the trace, the reproducibility and the cache key.
  Changing it later is a redesign and must be recorded as one.

## Vocabulary of the book (research, not decided)

**Purpose.** To find out whether terms extracted from the book itself reach paragraphs that the question as written does
not reach, and whether they do so reproducibly.

**Status.** Research only. The vocabulary is a mandatory artifact of the first milestone; research decides only the method. It depends on an ingestion
artifact that is not yet specified; its specification goes into `docs/ingest.md`.

**Questions to answer.**
- Which extraction method gives terms that the book itself uses for the concepts in a question: co-occurrence counts,
  word vectors trained on the book, or keyword extraction?
- Is the output stable on a text of this size, a translated book with a limited vocabulary? Vary the seed and the
  neighbours and compare.
- Is training reproducible? Word vector training is reproducible only with a fixed seed and a single worker; this weighs
  on the choice of method.
- Do the variants built from these terms reach paragraphs that the question as written does not? This measures reach,
  not meaning, so it needs no reference set.

**How to test, without spending API calls.** Run the extraction locally on the text already ingested, for the book in
use. Inspect a sample of extracted terms against the paragraphs they came from, and count the paragraphs that only the
variants reach. Repeat the extraction with the same inputs to check reproducibility.

**What the research does not decide.** Which method is adopted,
and what the artifact's identity is. Those are decided after the results.

## Open

- The fields of the trace are not defined yet. They depend on what the editorial AI reads, and are set together with the
  contract.
- The closed fields of the request (D1; open in the contract ledger).
