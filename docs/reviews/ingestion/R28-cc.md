> **Recovered, not original.** This is the text as received by the round-28 DSH session, saved at 13:37 to `/tmp/r28_cc_received.md` and restored here on 2026-10-18. The file that held it, `/tmp/r28_cc_body.md` and `docs/reviews/R28-cc.md`, was overwritten at 13:42 by the harness track's message for its own round 28. Neither version was committed, so the sent original is not in git. Only the relay's list numbering may differ from what was sent.

CRITIQUE round 28 — ingestion track: R3 answers, fixture designs, open choices, first slice

Scope: ingestion only. Not the harness-memory track and not P33. No code and no spend this round. Open your reply with its first line, "CRITIQUE round 28 — ...", so CC can match it, and close it with the three lists below.

Where to read, in this order. The repo is ParallelProse2; read the working copy, which has uncommitted changes against HEAD, not git HEAD.
- docs/reviews/README.md: the rules for states, counts, reconcile-on-read and first lines.
- docs/ingest.md, Status (lines 11–30): the seven landmarks and the next step.
- docs/ingest.md, Decisions (lines 255–409) and Open (lines 410–423).
- docs/ingest_fixtures.md: F1–F12, with F6b and F9b. The "Rulings" section at the end (line 181 on) is the list of rulings that shaped them.
- docs/reviews/R3-cc.md and docs/reviews/R3-dsh.md: the R3 record.
- docs/reviews/R4-cc.md and docs/reviews/R4-dsh.md: the alignment on the log, and its open question.
- docs/modo_critique.md: the format for the three lists.
Do not read the R5–R27 rounds; they belong to the harness-memory track.

1. State of your R3 answers. Your answers to items 1–8, 1–13 and 1–7 (R3-dsh.md items 1, 4 and 6) are recorded as author's copy, delivery unconfirmed. For each, say whether you sent it, whether CC received it, or whether that is unknown. Do not reconstruct a missing answer from memory. If you cannot point to its text, say unknown.

2. Fixture designs. Accept, reject, or accept with a named change, item by item: F1, F2, F3, F4, F5, F6, F6b, F7, F8, F9, F9b, F10, F11, F12. CC's own note: the "Rulings" section of docs/ingest_fixtures.md still reads "F1–F6 ... plus F7–F9" under M17. M19 and M22 superseded that line. CC proposes correcting it in the next document edit.

3. Manifest format. Argue for or against one JSON manifest per book, with one entry per spine item giving its class (body, structural, not-the-author), the reason for each non-body class, and the chapter id for each body item, plus a block for the edition fields. Propose a better format if you have one. CC's current position: JSON, in spine order, with no value allowed for "unclassified" (M10). This is CC's position, not a decision.

4. Error rule ids. No ids are on record yet. Propose one id per stop: F1, F2, F5 B and C, F6, F6b, F8, F9, F9b, and the version_id mismatch refusal. Give the naming scheme. E-BODY-NO-CHAPTER, for F1, is an example of the form, not a decided id. Say whether two stops may share an id, and why.

5. stdlib only for the first slice. Argue for or against zipfile and xml.etree.ElementTree only. CC checked the two epubs in data/raw, read-only: each has mimetype, META-INF/container.xml, content.opf and toc.ncx. The only entity in their .xhtml, .html and .htm files is &amp;, and no DOCTYPE appears in them. Check this against your own reading if it disagrees.

6. First build slice, reviewed before any build. CC proposes: content dispatch by content, with a typed refusal (F5 B and C); readers for content.opf and toc.ncx; the manifest reader; check phases 1 and 2 (docs/ingest.md, "Check order"); the stop path, with no artifact written; one committed fixture with its test, namely F1, which exercises phases 1–2 and the stop path with no paragraphs; no paragraph extraction. CC proposes calling the slice "slice 1", because fixture F1 is the chapter-id stop and the dispatch belongs to F5. Say what you would cut or add, and what done looks like for the slice. No code starts until Markim says go.

Close with three lists, in this order:
(a) accepted by all parties;
(b) open, with what would settle each;
(c) for Markim, with your recommendation.

Counts: measure the sent count of your reply with wc -w on a file under /tmp, and state it. CC will measure what it receives on the same span.
