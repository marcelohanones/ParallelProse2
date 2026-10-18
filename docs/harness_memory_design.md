# Harness memory design — Claude Code and dsh on one repo

Agreed 2026-10-13 between Claude Code and dsh, relayed by the user. Tracked by decision (P18/P19) together with
the project `CLAUDE.md` that points here, so a clone keeps the pointer and its target together; both harnesses
load that pointer every session. The memory files themselves stay out of git. Every fact below is tagged:

- **[measured]** — observed by running Claude Code 2.1.289 or dsh in a throwaway repo.
- **[code]** — read in dsh's source by dsh; not observed.
- **[decided]** — a design choice, with its reason.

## The rule: one writer per file

No file has two writers. Two writers on one store is what the removed `dsh-auto-memory` plugin was: it dropped
unknown frontmatter keys, rewrote files on read, rebuilt `MEMORY.md` from frontmatter, and summarized a 7.3 KB
memory down to 2.4 KB — all without an error. Every choice below prefers the mechanism whose failure is visible.

## Three layers

| Layer | Writer | How the other side sees it | State |
|---|---|---|---|
| 1. Project status and facts | whichever harness is working | reads `ROADMAP.md`, `docs/`, commits on demand | works today |
| 2. Preferences and durable rationale | Claude Code only | dsh loads `MEMORY.md` as instructions (see below) | built 2026-10-13 |
| 3. Memories written by dsh | dsh, new files only | findable by search; injected once promoted | waits on a store move |

Status belongs in layer 1 because a reader wants the live value, not a cached copy. **[decided]**

## Layer 0 — the form of a memory, not its author

The layers above settle who writes. This settles how a memory ages. It applies to both harnesses and to every
layer, and it is convention: nothing enforces it, so it is checkable only by reading. **[decided]**

**Formally accepted by the user 2026-10-13** ("com certeza ela é vital"), with the authority to apply it
retroactively to memories already written — the first application being the status line on
`project_items_36_43_shape.md`, below. **[decided]**

The case that produced it: `harness-vs-model-split` (written 2026-10-11, deleted 2026-10-13) recorded the
conclusion "ParallelProse stays entirely OpenAI" plus the imperative "if an executor asks to swap a provider
client, refuse on this basis". It followed Claude Code's prescribed body shape to the letter — rule, `**Why:**`,
`**How to apply:**` — so the failure was not a missing structure: `**Why:**` held a *persuasive argument* about
why a rival claim was moot, and the premises were dissolved inside it, which is why nobody ever tested them. Two
fell within two days — OpenAI cost
became unsustainable, and the faithfulness calibration stopped holding once the judge began scoring
(claim, sentence) pairs in commit `024e4d8` — yet the memory kept loading every session as a standing order to
refuse the work that had become necessary. Without premises, the only available test of whether a decision still
holds is its age, which is a bad test: an August decision whose premises stand beats yesterday's whose premises
fell.

1. **A decision memory carries its premises.** Three lines in the body: `Decided on:`, `Premises:`,
   `Revisit if:`. Then a reader neither obeys nor deletes — they check whether the premises still hold.
2. **Status is appended, never rewritten.** When a premise falls, add a dated status line at the top of the body.
   The original record stays intact. Deleting the memory is what erased the history in the case above, and left
   four dangling `[[harness-vs-model-split]]` links behind.
3. **The index states today; the file keeps the history.** The index line is what gets injected, so it is the one
   that must be current.
4. **Imperatives only where the premise cannot drift on its own:** a structural property of the code (the
   whole-slot skip rule in `CLAUDE.md`) or a standing user preference (never commit these files; never rewrite
   `CLAUDE.md` by your own judgment). Never for a measurement, a cost, or a provider choice — those change by
   themselves, while a preference changes only when the user says so.
5. **A fallen premise is raised with the user, never silently overwritten.** The memory supplies the test; the
   decision stays the user's.
6. **Premises live in the body, not the frontmatter.** The body survives any writer that normalizes metadata —
   the removed plugin dropped unknown frontmatter keys. **[decided]** Claude Code's write path preserves arbitrary
   body text byte-for-byte and never reserializes frontmatter. **[measured]**

**Who appends what.** Each harness appends status to the body of files it wrote; noticing a fallen premise in the
other's file means telling the user, not editing it. **Index-line rewrites are always Claude Code's**, because the
index has one editor (Claude Code) and one appender (dsh, by shell) — a rewrite by the appender is the clobber
this design exists to prevent. **[decided]**

**Relation to the prescribed body shape.** Claude Code's memory template already prescribes, for `project` and
`feedback` memories: the rule or fact, then `**Why:**` and `**How to apply:**`. Layer 0 complements it rather
than replacing it, on one division that has to hold or the two vocabularies say the same thing twice:
`**Why:**` carries the rationale as prose; **`Premises:` is a list of facts, each checkable against an artifact,
and never a restatement of `**Why:**`** — a premise line that reads like an argument belongs in `**Why:**`.
`**How to apply:**` keeps the action, subject to the imperative rule above. `Decided on:` and `Revisit if:` have
no counterpart in the template and are this form's genuine additions. **[decided]**

**Enforcement.** The form is convention; a checker can cover part of it. A `PreToolUse` hook on `Write|Edit`
inspects the content before it is written and blocks on exit code 2, with its stderr reaching the model: a
non-compliant body was refused and a compliant one passed, in a throwaway project, with the store where it is
today. **[measured]** Because the checker only signals, the hook belongs on the **post**-state (`PostToolUse`,
path-filtered to the store) rather than on `PreToolUse`, which would have to simulate the edit to see the
resulting body and could diverge from the tool's own matching (P21). dsh has the equivalent at write time via `tools/pre-execute`, `ctx.tools.guard()` and the
`fs/*` intent slots. **[code]** Both see only tool calls, so a shell append bypasses them; a git pre-commit hook
would cover any writer but needs the store in the repo. No check is written yet — deferred because the form is
still settling, not for want of a trigger. The checker signals only: it never deletes or rewrites, because
deciding that a premise fell is the user's (rule 5). Scope that avoids flooding on day one, and matches
no-retrofit: **if a body contains `Decided on:`, it must also contain `Premises:` and `Revisit if:`; without
`Decided on:`, nothing is required.** A premise should cite a symbol, commit or item whose *change* is the
signal — never a line number, and never something whose mere existence passes vacuously. **[decided]**

**No retrofit.** This form applies to new memories and to ones being edited anyway; existing memories are not
rewritten to add premises. Where a premise can be cited to a surviving artifact — a commit, `ROADMAP.md`, a file
in `docs/` — adding it opportunistically is fine. **Never invent a premise**: a fabricated premise is worse than
a missing one, because the next reader will check it and be satisfied. If the context lived only in a lost chat,
the memory keeps no premise line and is judged by reading, as it is today. **[decided]**

## What loads automatically, and what doesn't

- Claude Code: `CLAUDE.md` and its `@` imports, plus the first **200 lines** of `MEMORY.md`. A project
  `AGENTS.md` loads **only when there is no `CLAUDE.md`** — here there is one, so it would be skipped while dsh
  loaded it (P25, P28). **[measured]** A 301-line index
  showed line 150 and not line 250. **[measured]**
- dsh: the user-global `$DSH_HOME/AGENTS.md` first (shown as `~/.dsh/AGENTS.md`), then the project's files.
  **[measured]** The project chain runs from repo root to the current directory, broadest first. **[code]** Per directory it loads the base candidates
  `AGENTS.md`, `CLAUDE.md` and the overlays `AGENTS.local.md`, `CLAUDE.local.md` — configurable through
  `instructionFileCandidates` / `localInstructionFileCandidates`, so `AGENTS.local.md` is a choice, not a fixed
  name. **[code]**
- dsh's budget covers the whole rendered instruction baseline, not each file: `maxBytes` is 65,536 in this
  installation (`dsh-base/cordis.patch.yml:292`); the plugin has no default, so another profile can differ. Over
  budget, a file is either `omitted <path>` or `truncated <path> from N`. **[code]**
- Everything else — memory files, `docs/`, the repo — is best effort: it appears only if someone searches.
- A memory file with no `MEMORY.md` line is **not** injected, but is found by search. **[measured]**
- A pointer line in `MEMORY.md` guarantees the pointer, not the content: reading the target still takes a read.
  That is the right level for a design doc; inlining it every session recreates the notes-file cost. **[decided]**

## Usage rule: switching harness means a new Claude Code session

Claude Code reads `CLAUDE.md`, `@` imports and `MEMORY.md` once per session. Files changed between two turns of
one process were not seen in the second turn; the session record holds one `instructions` entry. **[measured]**
(Tested in `claude -p` with streamed input; interactive `/clear` and `/compact` untested.)

## Layer 2: dsh reading Claude Code's memory

Two pieces, both required:

1. Symlink `AGENTS.local.md` → Claude Code's `MEMORY.md`. dsh loads a candidate whose final path component is a
   symlink from its target. **[code]** The content enters as workspace guidance, the lowest authority: it never
   overrides system, developer or direct user instructions. **[code]**
2. `MEMORY.md`'s first line names the folder its links resolve against (written 2026-10-13, P15). dsh resolves the symlink to read the
   content but reports only the symlink's own path — both `displayPath` and `absolutePath` — so the target is
   never communicated and the model cannot follow `MEMORY.md`'s bare-filename links. A symlinked fixture rendered
   `Instructions from: AGENTS.local.md`, never the target. **[measured]**

The base line lives in `MEMORY.md` itself, not in `CLAUDE.md`: it travels with the links it explains, and its
only writer rewrites it in the same move if the store moves. It costs one of the 200 index lines. **[decided]**

## Setting up layer 2 in a repo — step by step

Written for a harness starting from zero. Placeholders, not paths: `<REPO>` is the repo root, `<STORE>` is
Claude Code's memory folder for that repo, `<SLUG>` is the folder's name. Claude Code derives `<SLUG>` from the
repo's absolute path by replacing each `/` with `-` (for example `-Users-<user>-Developer-...-ParallelProse2`), so
`<STORE>` is `~/.claude/projects/<SLUG>/memory/`. Substitute the real absolute path only in files that live
outside the repo (the store and the symlink). **Never write a home path into a committed file** — see P19.

1. **Create the store.** Open Claude Code in `<REPO>` once; if `<STORE>` does not exist, create it. Writing a memory
   there is the only way it gets content; nothing here copies memories from another repo.
2. **Ignore the symlink.** Add to `<REPO>/.gitignore`:
   ```
   # Harness-local instruction overlay (symlink into ~/.claude; machine-specific)
   AGENTS.local.md
   ```
   Check with `git check-ignore -v AGENTS.local.md` (exit 0). Do this before step 4, so the symlink never exists
   unignored.
3. **Write `<STORE>/MEMORY.md`.** Line 1 is the base line below, with `<STORE>` replaced by the absolute store path.
   Then one index line per memory: `- [Title](file.md) — hook`. Index lines are written by Claude Code (P9); dsh
   never rewrites them. The base line uses one of the 200 index lines Claude Code loads (see "What loads automatically").
   > *Links in this file are filenames inside `<STORE>` — resolve them there, never against the repo root. Reading
   > there is permitted: the folder is outside the repo but not outside reach. dsh reads this file through the
   > repo-root symlink `AGENTS.local.md`, which reports only its own path; see `docs/harness_memory_design.md` (P15).*
4. **Create the symlink** with an absolute target:
   ```
   ln -s "<STORE>/MEMORY.md" "<REPO>/AGENTS.local.md"
   ```
   Check with `readlink <REPO>/AGENTS.local.md`: it must print the store path.
5. **Point to this doc from `CLAUDE.md`.** Add a section `## Harness memory` that names this file. Use `CLAUDE.md`,
   not `AGENTS.md`: Claude Code skips `AGENTS.md` when a `CLAUDE.md` exists (P25).
6. **Commit the three repo files together:** `.gitignore`, `CLAUDE.md` and this doc (P18). Never commit the symlink or
   the store. Committing buys no interoperability (P29); it only decides what a clone carries.
7. **Probe memory (Claude Code writes it).** Open Claude Code in `<REPO>` and ask it to save one memory into `<STORE>`
   with a body that contains a unique marker (for example `MARKER-<random>`), and to add its index line. The index
   title must not contain the marker, so the marker can only come from reading the file. Claude Code writes the
   index line (P9), never dsh. If the index changed during a Claude Code session, start a new one (P3).
8. **Cold run (acceptance check).** From `<REPO>`, run a fresh dsh session with the prompt below. Each run is a new
   session: never pass `--session-id`, and do not continue an earlier run. The prompt is verbatim (in Portuguese, so
   later runs stay comparable); the status below lists the runs that used it. Replace only `<PROBE_TITLE>` with the probe's title:
   ```
   cd <REPO> && dsh --profile headless "<prompt below>"
   ```
   ```text
   Esta é uma leitura fria, sem ajuda. Regras:
   - Não use ferramentas de busca (grep, find, glob ou similares) em nenhum momento.
   - Não escreva nem edite nenhum arquivo.
   - Responda em português.

   1. Sem buscar, liste as instruções que você recebeu no início desta sessão: o nome de cada arquivo carregado, incluindo qualquer um que aponte para memória.
   2. A partir do que você recebeu, diga onde ficam as memórias de referência do projeto e cite a linha que explica como resolver os links.
   3. Sem ler nenhum arquivo, liste as entradas do índice de memória exatamente como aparecem.
   4. Siga o link da entrada cujo título é "<PROBE_TITLE>", resolvendo o nome do arquivo contra a pasta do store segundo a regra que você citou no passo 2. Reporte a linha do corpo que contém o marcador.
   5. Reporte, em uma linha por informação, a fonte exata de cada coisa que você disse: o arquivo carregado, a entrada do índice, ou a leitura do arquivo de teste.
   6. Informe se o marcador apareceu antes do passo 4. Se sim, diga de onde veio.
   ```
   **Pass:** the entries in step 3 come from the injected instructions, with no search; the marker is reported only
   after the read in step 4; nothing reported before that read was absent from the instructions and the index.
   This is the P15 cold run. A run with search, a write, or a marker reported before step 4 fails.
9. **Clean up.** Remove the probe file and its index line, then check the store holds only real memories. A probe
   left in the store is a memory the next reader will trust.

**Which profile the result covers.** The step 8 command uses `--profile headless`, and its pass covers that profile
only. An interactive profile can assemble its instructions differently, so step 8 must be repeated with each one before
it is claimed for that profile. On this machine the installed profiles are `headless` and `web` (`ls ~/.dsh/profiles`);
`dsh web` serves the browser UI and must be run from `<REPO>`. `dsh tui` does not exist here. The `web` runs are in the status below.

**Status of this procedure.** Steps 1–5 and 9 are in place in `ParallelProse2`, built on 2026-10-17, committed at 00:01 the next day (`38dbc69`);
step 6's commit of this section landed at 01:19 the next day (`fc25dda`). Step 8 has five recorded runs in `~/.dsh/sessions/`. A run's profile is
inferred from two signals: whether its session is in the GUI's workspace registry (`~/.dsh/storages/workspace.json`),
and whether its header carries an `agentPreset` field. No record names who issued a run.
- `15c39d02` (2026-10-17, 23:29): outside the GUI by both signals, which is the basis for its `headless` label. The
  marker is reported only after the read, so it passes. Its prompt is not the one above: it asks for "Reporte a linha 9
  desse arquivo" and calls the probe "entrada de teste".
- `69b468b4` (2026-10-17, 23:52): in the GUI. Its probe is not in the store, and it reports the marker absent, so it is
  a negative control. Its prompt is not the one above.
- `1836d2e7` (2026-10-18, 00:02): in the GUI. The marker is reported only after the read, so it passes as a `web` run.
  Its prompt is not the one above.
- `4d483949` (2026-10-18, 00:15): not in the GUI's registry, with `agentPreset`. The text it submitted was already cut
  after the first rule, with the other two rules and the six questions missing, and a first attempt failed in transport.
  The retry re-sent that same text, so the run asked which document to read and gave no answer.
- `97e2abed` (2026-10-18, 00:16): the only run with the prompt above verbatim. The marker is reported only after the
  read, so it passes. It carries `agentPreset` but is not in the registry, so its profile is not settled.

A `web` pass therefore rests on `1836d2e7`, whose prompt differs from the one above, unless `97e2abed` is shown to be
a GUI session; then a verbatim `web` pass exists as well.

## Layer 3: dsh writing memories

**Status 2026-10-13 — decided off (P17).** dsh does not write memories; layer 2 (dsh reads the index) plus layer 1
(durable project facts in the repo) cover the need, and the store move that layer 3 required (P16) is parked with
it. The design below stands as the record of what turning it on would take, not as pending work.

- dsh writes **new files only**, in Claude Code's shape: filename `{type}_{name_underscored}.md`, frontmatter
  `name`, `description`, `metadata.node_type: memory`, `metadata.type`.
- Unpromoted files lose only injection, never data — so promotion (adding the `MEMORY.md` line) is an optional
  upgrade and doubles as the review gate on what dsh wrote. A trigger that never fires breaks nothing. **[decided]**
- Index lines are appended by shell, guarded against a missing final newline (a glued line silently breaks the
  previous memory's link):
  ```sh
  [ -n "$(tail -c1 "$f")" ] && printf '\n' >> "$f"
  printf '%s\n' "- [Title](file.md) — description" >> "$f"
  ```
- Clobber protection on `MEMORY.md`: Claude Code's Write refuses a file changed since read; Edit applies to the
  current disk content with a warning, keeping foreign lines. **[measured]** dsh's `write` and `str_replace`
  both refuse a guarded mutation with one of two codes: `FS_STALE_VERSION` (changed since read — "re-read the
  file, then retry") or `FS_NOT_OBSERVED` (never read — "read the file, then retry"). The tool returns the
  remedy and does not retry by itself. Shell appends bypass this guard by design. **[code]**
- Blocked on write access: the store is outside dsh's workspace, so each dsh write needs approval. Moving the
  store into the repo removes that. **[decided]**

## Store location, if it moves into the repo

| Option | Grep finds it by default | In git | Verdict |
|---|---|---|---|
| Versioned | yes | yes | no — publishes personal notes in a public showcase repo |
| Ignored (`.memory/`) | **no** — only when Grep is given the path **[measured]** | no | no — discovery depends on an instruction |
| Selective negation (`.memory/*` + `!.memory/dsh/`) | dsh files only **[measured by dsh]** | no | no — `.memory/` written by reflex kills it silently |
| **Untracked, not ignored** | yes **[measured]** | no | **chosen** — matches the repo's practice; a careless `git add -A` shows up as `??` before it commits |

Grep skips gitignored paths, not hidden ones (`.hiddenok/` was found). **[measured]**

A move means: move the files and `MEMORY.md`, set `autoMemoryDirectory` in `.claude/settings.local.json`
(honored from local settings **[measured]**), repoint the symlink, rewrite the base line. If
`settings.local.json` is lost, Claude Code falls back to its default folder and an empty store; the old store
stays on disk and one line restores it.

## Point ledger — what is settled and what is open

Stable IDs. Each harness states per ID: **settled** (agreed, nothing owed) or **open** (needs a decision, a
build or a measurement). Numbers are never reused or renumbered; a point that closes keeps its ID and flips to
settled. New points append.

| ID | Point | Status | Owner of the next move |
|---|---|---|---|
| P1 | One writer per file; dsh writes new files only; editing existing files and the index is Claude Code's | settled | — |
| P2 | Three layers: status in the repo, memory written by Claude Code, dsh-written memories last | settled | — |
| P3 | Switching harness requires a new Claude Code session (load-once, measured) | settled | — |
| P4 | Layer 0 form: `Decided on:` / `Premises:` / `Revisit if:` in the body, premises never in frontmatter | settled | — |
| P5 | Status appended with a date, never rewritten; the index states today, the file keeps the history | settled | — |
| P6 | Imperatives only for structural properties or standing user preferences | settled | — |
| P7 | A fallen premise is raised with the user; no harness and no checker decides it | settled | — |
| P8 | No retrofit; opportunistic and artifact-cited only; never invent a premise | settled | — |
| P9 | Index-line rewrites are always Claude Code's, even for files dsh wrote | settled | — |
| P10 | Write-time enforcement exists today on both sides and needs no store move (measured on Claude Code, read in code on dsh) | settled | — |
| P11 | The linter stays unwritten while the form settles — the reason is "form not stable", not "no trigger" | settled | — |
| P12 | Linter scope: `Decided on:` present ⇒ `Premises:` and `Revisit if:` required; absent ⇒ nothing required | settled | — |
| P13 | Premises cite a symbol, commit or item whose change is the signal; never a line number, never a vacuous existence check | settled | — |
| P14 | Layer 2 piece 1: the `AGENTS.local.md` symlink (repo root → the store's `MEMORY.md`, absolute target, ignored as `AGENTS.local.md` in `.gitignore` and **observed to load anyway** in the cold run, third in the chain — ignoring governs search-based discovery only, never a load by exact path, which is the premise the whole `.gitignore` choice rested on **[measured]**; so a `git add -A` cannot commit a machine-local link) | settled — built by dsh 2026-10-13 | — |
| P15 | Layer 2 piece 2: the base-path line as `MEMORY.md`'s first line. **Confirmed cold**: a fresh dsh session loaded `~/.dsh/AGENTS.md`, `CLAUDE.md`, `AGENTS.local.md`, derived the store path from the base line alone with search tools forbidden, cited both halves, and read the target file **[measured]**. The line also states that reading there is permitted, after the cold run showed the model nearly talking itself out of a cross-boundary read | settled — both sides | — |
| P22 | Layer 0 complements Claude Code's prescribed body shape: `**Why:**` is prose rationale, `Premises:` is checkable facts and never restates it; `Decided on:` / `Revisit if:` are the additions. Acked by dsh: the division doubles as the writer's decision procedure — *if the line reads like an argument it belongs in `**Why:**`* — which is what adoption needs given P24, and it names the original failure as a field filled with the wrong kind of content, not a missing field | settled | — |
| P23 | Layer 0's motivation corrected: the case memory *did* follow the template; `**Why:**` held a persuasive argument, so the premises were never testable | settled — doc fixed | — |
| P24 | Adoption reaches the writer through the index, not a checker. The `memory-types` skill is **not** available in this installation — absent from the session's skill listing **[measured]** — so the form travels in the existing harness-memory-design memory, which already summarizes it; no new index line needed | settled | — |
| P25 | `AGENTS.md` in this repo would load in dsh and be skipped by Claude Code, which loads it only when no `CLAUDE.md` exists **[measured]**. That is why the shared pointer lives in `CLAUDE.md`: it is the one project instruction file both harnesses load unconditionally. Nothing is to be added to a repo `AGENTS.md` | settled | — |
| P26 | User-global rules unified 2026-10-13: dsh's copy was a strict superset (20 lines, the `## Frame check` block), so it was inserted verbatim into `~/.claude/CLAUDE.md` until the two files were byte-identical, then `~/.dsh/AGENTS.md` became a symlink to it (backup at `~/.dsh/AGENTS.md.pre-unify-20261013`). One file, both harnesses; the section reaches Claude Code **[measured]** | settled | — |
| P27 | **Withdrawn by dsh as a misdiagnosis**, and the conclusion is stronger than the point claimed. The `bash` call was incidental: dsh's touch mechanism is allowlisted to `read`, `write`, `edit` (each carrying a `file_path`), so `bash` cannot qualify, and it drives *nested* discovery only. What surfaced the symlink is a separate half — `compose` runs on every `agent/pre-step` and reconciles top-level candidates against the files, re-reading only those whose version changed. So dsh's staleness window for top-level candidates is **one step**, with no tool call involved; its own earlier sentence was correct, not too narrow **[code]** | settled — withdrawn | — |
| P29 | Committing buys **no** interoperability: both harnesses read the working tree, never git objects, so the pointer works staged, unstaged or untracked. P18/P19 are therefore a publication decision only — disclosure against clone-coherence — which also kills the "commit `CLAUDE.md` without the pointer" option: it buys no privacy that unstaging both wouldn't, and costs the shared channel P25 protects | settled | — |
| P30 | Claude Code *can* refresh instruction files mid-session: this conversation received a re-read `~/.claude/CLAUDE.md` carrying the newly inserted `## Frame check` **[measured]**. It does not contradict P3, which measured a `claude -p` streamed session showing no refresh — different harness paths. **Reach, asked by dsh:** it covers `MEMORY.md` too — this conversation received a re-read index carrying first-line and index edits made minutes earlier, twice **[measured]**. So both surfaces this design rides on do refresh. `@` imports are untested and moot here: the pointer is a plain `CLAUDE.md` section, not an import. P3's new-session rule therefore stays the **safe default**, not a hard requirement — the harness often makes it unnecessary, but nothing promises it will | settled | — |
| P28 | Claude Code's automatic surface is wider than the doc's bullet: nested `.claude/CLAUDE.md` and `.claude/AGENTS.md` per directory, plus `rules/`, `skills/`, `commands/`, `agents/`, `output-styles/` under `.claude/` and `~/.claude/`. Both harnesses have nested candidates under different names and different walk rules — a second site for the same silent divergence as P25/P26 | settled — recorded | — |
| P16 | Moving the store into the repo: **not done**, parked with P17 — its only consumers were layer 3 and a git pre-commit check. Untracked-and-not-ignored remains the choice if it is ever revisited | settled — parked | — |
| P17 | Layer 3 on: **no.** dsh does not write memories; layers 1 and 2 cover the need | settled — no | — |
| P18 | Commit `CLAUDE.md` **and this doc together**, so a clone never has the pointer without its target; `.gitignore` rides along | settled — pointer in `38dbc69`, procedure in `fc25dda` | — |
| P19 | The pointer section is public. Checked before deciding: neither file carries a home path or the username, and the only memory content published is layer 0's citation of the deleted case memory (the OpenAI conclusion, the cost problem, commit `024e4d8`) | settled — public | — |
| P20 | Write the linter (needs P11 to flip: the form declared stable) | open | either, after P11 |
| P21 | The write-time check must filter on file path (the memory store only). Content-only matching false-positives on this doc, which quotes the three markers, and on an `Edit` whose partial `new_string` carries `Decided on:` without the rest of the body. **Acked by dsh, with a refinement taken:** check the *post*-state via `PostToolUse` rather than simulating the edit at `PreToolUse`, since simulation re-implements Edit's matching and can diverge silently. Sufficient only while P7 holds (the checker signals, never acts) — **if P7 ever flips to "blocks", `PreToolUse` plus simulation becomes necessary and that risk returns**; the two are coupled | settled | — |
| P31 | Signed off by dsh, round 5, for steps 1–6 and 9 as written; step 8's passes rest on the session records, `headless` for `15c39d02` and `web` for `1836d2e7`'s variant-prompt run | settled | — |
| P32 | `CLAUDE.md:26` points at `docs/modo_critique.md`, committed in `e7048b9` so a clone keeps the pointer and its target | settled — committed `e7048b9` | — |
