# ROADMAP

Code development for ParallelProse2. The ingestion ledger is `docs/ingest.md`; this file summarizes its status and does not decide anything itself. The retriever–editorial contract is in `docs/contract_retriever_editorial.md`.

## Next items

| # | Item | State | Status | Commit |
|---|---|---|---|---|
| 1 | Spec: decisions and M1–M43 applied to `docs/ingest.md` | applied | Done | — |
| 2 | Manifests for both books (`manifests/augustine.json`, `manifests/debord.json`) | reviewed and confirmed | Done | — |
| 3 | Fixture designs F1–F12, F9b, F6b | accepted in R28 | Done | — |
| 4a | Dispatch, readers, phases 1–2 on Augustine | 33 tests | Done | `e4f36dd` |
| 4b | Paragraphs and addresses on Augustine and Debord | 460 and 230 paragraphs | Done | `86c0c0e` |
| 4c | Artifact and identity: JSONL, report, `version_id`, `content_hash`, atomic writes | 93 tests | Done | `c0def6d` to `587787b` |
| 4d | Augustine fixtures pass twice | 101 tests | Done | `10abbcb` |
| 5 | Debord printed numbers (D5) and the both-books proof | 107 tests | Done | `dc851a3` |
| 6 | Determinism and artifact checks | 112 tests | Done | `3f92b41` |
| 7 | Retriever milestone 1, non-vector parts: request and trace schema, stop logic, coverage accounting. Fixture tests, no API calls. | ready once this roadmap is committed | To do | — |
| 8 | Vector spec and cost estimate under D7: current price check, written estimate, descriptor and identity | ready to write; the run waits for approval of the estimate | To do | — |
| 9 | Build paragraph vectors for Augustine and Debord, then the dense channel (attempts 1–3, depth, cut-off) | waits for 7, 8 and approval of the run | Blocked | — |
| 10 | Vocabulary research plan: pass bar, translation handling, artifact content. Local runs only. | to write; blocks attempt 4 only | To do | — |
| 11 | Contract round 2: relay the reply; answers to B1–B4 when the editorial system is ready | reply drafted; waiting for relay | To do | — |
| 12 | Calibration of the cut-off and depth (D9) | deferred; waits for 9 and a defined control set | Blocked | — |
