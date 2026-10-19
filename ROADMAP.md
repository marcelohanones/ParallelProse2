# ROADMAP

Code development for ParallelProse2. The ingestion ledger is `docs/ingest.md`; this file summarizes its status and does not decide anything itself. The retriever–editorial contract is in `docs/contract_retriever_editorial.md`.

## Ingestion (`src/parallelprose2/ingest/`)

| landmark | state | commit |
|---|---|---|
| 1. Spec: decisions and M1–M43 applied to `docs/ingest.md` | Done | — |
| 2. Manifests for both books (`manifests/augustine.json`, `manifests/debord.json`) | Done | — |
| 3. Fixture designs F1–F12, F9b, F6b | Done | — |
| 4a. Dispatch, readers, phases 1–2 on Augustine | Done (33 tests) | `e4f36dd` |
| 4b. Paragraphs and addresses on Augustine (460) and Debord (230) | Done | `86c0c0e` |
| 4c. Artifact and identity: JSONL, report, `version_id`, `content_hash`, atomic writes | Done (93 tests) | `c0def6d` to `587787b` |
| 4d. Augustine fixtures pass twice | Done (101 tests) | `10abbcb` |
| 5. Debord printed numbers (D5) and the both-books proof | Done (107 tests) | `dc851a3` |
| 6. Determinism and artifact checks | Done (112 tests) | `3f92b41` |

Open in the ingestion ledger: the vocabulary artifact (mandatory for the retriever's first milestone; method and identity not yet specified).

## Retriever and editorial AI

Not started. The contract is open: D1 is proposed, D2 is accepted as a proposal, D3 is accepted (see `docs/contract_retriever_editorial.md`).
