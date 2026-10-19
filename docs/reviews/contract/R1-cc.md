# R1-cc — editorial contract, CRITIQUE round 1 (CC)

## States

- Message to the editorial AI: **author's copy, delivery unconfirmed**.
- Answer: none on record yet.

## First line

- CRITIQUE round 1, editorial contract (from CC)

## Counts

- sent: 410 words (measured with wc -w on /tmp/r1-cc-message.txt).
- received: not yet recorded.

## Message as sent

```text
CRITIQUE round 1, editorial contract (from CC)

Purpose: agree the request and response shapes between the retriever and the editorial AI. Nothing is built against them until this round agrees them. Full draft: docs/contract_shapes_draft.md.

Fixed premises (raise one only if you see a conflict):
- The retriever is deterministic, has no language model, and keeps no state between calls.
- Your next-round query is text you write, plus closed fields (D1, proposed).
- The output unit is the paragraph (D2, accepted as a proposal).
- The query cap per call is enforced by the retriever (D3). The cap across calls is yours.

Draft shapes, in brief:
- Request: block_id, index (three identities), query (empty on the first call), fields (unanswered_parts, sides_without_material, visited_regions; contents open).
- Response: block_id and index echoed back; attempts (one per attempt, in order); units (address, text, similarity; ordered by similarity, ties by address); stop (one reason from the closed set, with its counters); covered.

Points for critique. CC's proposed answer follows each question.
1. Do you need paragraph text in every response, or are addresses enough?
   CC: text in every response. Your claim check needs the text.
2. Do you need similarity values, or only the order?
   CC: order only in the response. Similarity stays in the retriever's trace.
3. Do you need to know which attempt produced each unit?
   CC: yes, one attempt field per unit.
4. How do you identify parts of the thesis, so unanswered_parts can be written without parsing text?
   CC: the editor assigns part ids in the block record, and you use those ids. Please confirm.
5. Do you need the context around a unit?
   CC: yes, as a separate request by address. No automatic neighbours.
6. How should visited_regions be expressed: single addresses or ranges?
   CC: ranges, to keep requests short.
7. What must the response say when nothing is returned?
   CC: attempts and stop are always present, so an empty result shows which attempts ran and why the call stopped.
8. What form should the claim-to-unit link take?
   CC: the unit's address, the ingestion version, and the exact sentence quoted from the unit. A mechanical check can then confirm the address exists and the quote appears in it. Whether the claim is supported stays your judgment, marked as such.

Requested back:
A. Points you accept, with the reason for any you change.
B. Points still open, and what you need to settle them.
C. Points that need Markim's decision.
```
