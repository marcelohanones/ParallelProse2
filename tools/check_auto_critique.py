#!/usr/bin/env python3
"""Check round files against docs/auto_critique2.md.

Signals only: this script never edits, rewrites or deletes anything. Exit 0 when
there is no failure, 2 when at least one file fails, following P7 of
docs/harness_memory_design.md (a check signals; the person decides).

The six items below are the contract's verification section, in its order:

  1. the gate block exists, parses, and nothing after it is a section other than
     the counts footer, and nothing at all follows the footer   -> "gate-last"
  2. to-markim and blocks-advance are coherent                   -> "gate-coherence"
  3. sent in the header matches LC_ALL=C wc -w                   -> "sent"
  4. at most one counts footer                                   -> "single-footer"
  5. the checador key cites the file this message answers, and its number is
     that file's own findings                                   -> "checador"
  6. the file cited in that key is named in the opening line     -> "opening"

Separately, it reports addenda that no opening line names. That report is
registry-level and never fails a file: which message owed the addendum a
response is sense, and the `checador:` key counts findings on the file a
message answers.

The form rules apply from the round the contract's Vigencia names, and the
checador key from the later round it names. Those two numbers live only in the
constants below, and a test reads them back from the contract: never restate
them in prose, which is how they went stale once. The contract's
critique-exceptions block names files whose known deviations must not be
reported as failures.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "auto_critique2.md"
REVIEWS = ROOT / "docs" / "reviews"
FIRST_ENFORCED_ROUND = 1
FIRST_CHECKER_KEY_ROUND = 2
BT = chr(96)

# The rule names the code emits, in the contract's verification order. The
# contract names each one in backticks after "regra", and
# test_contract_lists_every_rule keeps the two lists equal.
RULES = ("gate-last", "gate-coherence", "sent", "single-footer", "checador", "opening")
RULE_HINT_RE = re.compile(r"regra `([\w-]+)`")

ROUND_RE = re.compile(r"^R(\d+)-(cc|dsh)((?:-[a-z0-9]+)*)\.md$")
FILE_RE = ROUND_RE
OPENING_RE = re.compile(r"^Segue as? mensage(?:ns|m)\b")
SENT_RE = re.compile(r"<!--\s*sent:\s*(\d+)\s*palavra")
FENCE_RE = re.compile("^(" + BT + "{3,})([^" + BT + "]*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
COUNTS_RE = re.compile(r"^##\s+Contagens\s*$")
CHECKER_RE = re.compile(r"checador:\s*(\S+\.md)\s*[—-]\s*(\d+)\s*achado")


def parse_round_name(name: str) -> tuple[int, str, str | None] | None:
    """(round, side, suffix) for a round file name, or None.

    The suffix is the addendum subject, or None for a turn file. The watcher and
    the checker both read names through here, so neither can drop a file the
    other sees.
    """
    match = ROUND_RE.match(name)
    if not match:
        return None
    return int(match.group(1)), match.group(2), (match.group(3)[1:] or None)


def word_count(path: Path) -> int:
    env = dict(os.environ, LC_ALL="C")
    out = subprocess.run(["wc", "-w", str(path)], capture_output=True, text=True, env=env)
    return int(out.stdout.split()[0])


def load_exceptions(contract: Path | None = None) -> dict[str, set[str]]:
    """Read the contract's critique-exceptions block: file | rule | reason."""
    path = contract or CONTRACT
    found: dict[str, set[str]] = {}
    if not path.exists():
        return found
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "critique-exceptions":
            inside = True
            continue
        if stripped == "critique-exceptions-end":
            inside = False
            continue
        if inside and stripped:
            parts = [p.strip() for p in stripped.split("|")]
            if len(parts) >= 2:
                found.setdefault(parts[0], set()).add(parts[1])
    return found


def contract_vigencia(contract: Path | None = None) -> tuple[int | None, int | None]:
    """The two round numbers the contract names for the enforcement constants."""
    path = contract or CONTRACT
    if not path.exists():
        return (None, None)
    text = path.read_text(encoding="utf-8")
    form = re.search(r"\*\*Vigência\*\*[^\n]*?rodada R(\d+)", text)
    key = re.search(r"Obrigatória da rodada R(\d+)", text)
    return (int(form.group(1)) if form else None, int(key.group(1)) if key else None)


def contract_rule_ids(contract: Path | None = None) -> list[str]:
    """Rule identifiers named in the contract's verification section, in order."""
    path = contract or CONTRACT
    if not path.exists():
        return []
    ids: list[str] = []
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip().lower().startswith("## verifica")
            continue
        if inside:
            found = RULE_HINT_RE.search(line)
            if found:
                ids.append(found.group(1))
    return ids


def fenced_lines(lines: list[str]) -> tuple[list[bool], list[tuple[int, int, str]]]:
    """Mark which lines sit inside a fence, and list the fences found."""
    inside = [False] * len(lines)
    fences: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        match = FENCE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        ticks, info = match.group(1), match.group(2).strip()
        j = i + 1
        while j < len(lines):
            if re.match("^" + BT + "{%d,}\\s*$" % len(ticks), lines[j]):
                break
            j += 1
        for k in range(i, min(j + 1, len(lines))):
            inside[k] = True
        fences.append((i, j, info))
        i = j + 1
    return inside, fences


def parse_keys(body: list[str]) -> dict[str, str]:
    keys: dict[str, str] = {}
    for line in body:
        if ":" in line:
            key, _, value = line.partition(":")
            keys[key.strip()] = value.strip()
    return keys


def gate_keys(path: Path) -> dict[str, str]:
    """The gate block's keys, or {} when there is no critique-gate fence."""
    lines = path.read_text(encoding="utf-8").splitlines()
    _, fences = fenced_lines(lines)
    for start, end, info in fences:
        if info == "critique-gate":
            return parse_keys(lines[start + 1 : end])
    return {}


def header_keys(path: Path) -> dict[str, str]:
    """The header keys: the contract puts them in the first block of the file.

    Only lowercase keys count, so the sent comment and prose lines with a colon
    stay out. The block ends at the first blank line.
    """
    keys: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            break
        key, sep, value = line.partition(":")
        key = key.strip()
        if sep and re.fullmatch(r"[a-z][a-z-]*", key):
            keys[key] = value.strip()
    return keys


def opening_line(lines: list[str]) -> str | None:
    """The first body line: not the sent comment, not a key, not blank."""
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        if re.fullmatch(r"[a-z][a-z-]*:.*", stripped):
            continue
        return stripped
    return None


def analyze(path: Path, _depth: int = 0) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    inside, fences = fenced_lines(lines)
    findings: list[tuple[str, str]] = []

    gate = [(a, b) for a, b, info in fences if info == "critique-gate"]
    if gate:
        start, end = gate[0]
        keys = parse_keys(lines[start + 1 : end])

        # rule 1: after the gate, only the counts footer may appear as a section,
        # and nothing at all may follow the footer. No early break: every heading
        # after the gate is inspected, so a section after the footer is caught.
        seen_footer = False
        for idx in range(end + 1, len(lines)):
            if inside[idx]:
                findings.append(("gate-last", "cerca depois do gate, linha %d" % (idx + 1)))
                continue
            if not lines[idx].strip():
                continue
            heading = HEADING_RE.match(lines[idx])
            if heading:
                if COUNTS_RE.match(lines[idx]) and not seen_footer:
                    seen_footer = True
                    continue
                if COUNTS_RE.match(lines[idx]):
                    findings.append(("gate-last", "segundo rodape depois do gate, linha %d" % (idx + 1)))
                else:
                    findings.append(("gate-last", "secao fora do rodape depois do gate, linha %d" % (idx + 1)))
                continue
            if not seen_footer:
                findings.append(("gate-last", "conteudo solto depois do gate, linha %d" % (idx + 1)))
    else:
        keys = {}
        findings.append(("gate-last", "sem bloco critique-gate"))

    # rule 2: to-markim and blocks-advance are coherent
    to_markim = keys.get("to-markim", "")
    blocks = keys.get("blocks-advance", "")
    if not gate:
        pass
    elif not to_markim:
        findings.append(("gate-coherence", "to-markim ausente"))
    if gate:
        if blocks not in ("yes", "no"):
            findings.append(("gate-coherence", "blocks-advance deve ser yes ou no, veio %r" % blocks))
        elif blocks == "no" and to_markim and to_markim.lower() != "none":
            if not keys.get("why-not-blocking"):
                findings.append(("gate-coherence", "blocks-advance: no sem why-not-blocking"))
        elif blocks == "yes":
            if to_markim.lower() == "none":
                findings.append(("gate-coherence", "blocks-advance: yes sem rótulo em to-markim"))
            elif not keys.get("why-blocking"):
                findings.append(("gate-coherence", "blocks-advance: yes sem why-blocking"))

    # rule 3: the header count matches the canonical command. Runs even when the
    # gate is missing, because a truncated file is exactly when the count matters.
    header = next((l for l in lines if l.strip()), "")
    declared = SENT_RE.search(header)
    if not declared:
        findings.append(("sent", "sem cabecalho de contagem"))
    else:
        actual = word_count(path)
        if int(declared.group(1)) != actual:
            findings.append(("sent", "declarado %s, canonico %d" % (declared.group(1), actual)))

    # rule 5: the checador key, mandatory from FIRST_CHECKER_KEY_ROUND. It cites the file this
    # message answers, and the number the checker reports for that file. The
    # inventory is never the value: it includes the file being written, so it is
    # false by construction. _depth stops a citation loop between two files.
    #
    # rule 6: the opening line names the message(s) this one answers, and the
    # key's target has to be among them. It is a membership test, not equality,
    # because a message can answer a question and its addendum at once.
    name_match = FILE_RE.match(path.name)
    round_no = int(name_match.group(1)) if name_match else 0
    if _depth == 0 and round_no >= FIRST_CHECKER_KEY_ROUND:
        header: list[str] = []
        for line in lines:
            if not line.strip():
                break
            header.append(line.strip())
        key_line = next((l for l in header if l.startswith("checador:")), None)
        cited = CHECKER_RE.search(key_line) if key_line else None
        if key_line is None:
            findings.append(("checador", "chave checador ausente"))
        elif not cited:
            findings.append(("checador", "chave checador em formato invalido: %r" % key_line))
        else:
            target, declared = cited.group(1), int(cited.group(2))
            hits = list(REVIEWS.rglob(target))
            if not hits:
                findings.append(("checador", "arquivo citado nao encontrado: %s" % target))
            elif len(hits) > 1:
                findings.append(("checador", "arquivo citado ambiguo: %s" % target))
            else:
                actual = len(analyze(hits[0], _depth + 1))
                if actual != declared:
                    findings.append(("checador", "%s: declarado %d, real %d" % (target, declared, actual)))

        first_body = opening_line(lines)
        opening = first_body if first_body and OPENING_RE.match(first_body) else None
        if opening is None:
            findings.append(("opening", "linha de abertura ausente"))
        elif cited:
            named = re.findall(r"[\w.-]+\.md", opening)
            if cited.group(1) not in named:
                findings.append(("opening", "alvo %s nao consta da abertura (%s)" % (cited.group(1), ", ".join(named) or "nenhum")))

    # rule 4: at most one counts footer
    counts = [i + 1 for i, l in enumerate(lines) if not inside[i] and COUNTS_RE.match(l)]
    if len(counts) > 1:
        findings.append(("single-footer", "%d rodapes (linhas %s)" % (len(counts), ", ".join(map(str, counts)))))

    # one finding per rule is enough to point the reader at the problem
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for rule, message in findings:
        if rule in seen:
            continue
        seen.add(rule)
        deduped.append((rule, message))
    return deduped


def unnamed_addenda(reviews: Path | None = None) -> list[str]:
    """Addenda in the folder that no opening line names, in folder order.

    The fact is mechanical: an addendum has its own name shape and sits in the
    folder. Which message owed it a response is sense, so this report is
    registry-level and never fails a file; it stays out of any `checador:` key,
    which counts findings on the file a message answers.
    """
    root = reviews or REVIEWS
    named: set[str] = set()
    addenda: list[str] = []
    for path in sorted(root.rglob("*.md")):
        match = FILE_RE.match(path.name)
        if not match:
            continue
        if match.group(3):
            addenda.append(path.name)
        line = opening_line(path.read_text(encoding="utf-8").splitlines())
        if line and OPENING_RE.match(line):
            named.update(re.findall(r"[\w.-]+\.md", line))
    return [name for name in addenda if name not in named]


def classify(round_no: int, findings: list[tuple[str, str]], named: set[str]) -> tuple[str, list[tuple[str, str]]]:
    """Return (label, findings to report or fail on)."""
    if round_no < FIRST_ENFORCED_ROUND:
        return "historico", findings
    unlisted = [f for f in findings if f[0] not in named]
    if unlisted:
        return "FALHA", unlisted
    if findings:
        return "excecao", findings
    return "ok", []


def main() -> int:
    exceptions = load_exceptions()
    failed = excepted = history = ok = 0
    rows: list[str] = []
    for path in sorted(REVIEWS.rglob("*.md")):
        match = FILE_RE.match(path.name)
        if not match:
            continue
        round_no = int(match.group(1))
        findings = analyze(path)
        label, reported = classify(round_no, findings, exceptions.get(path.name, set()))
        if label == "FALHA":
            failed += 1
        elif label == "excecao":
            excepted += 1
        elif label == "ok":
            ok += 1
        else:
            history += 1
        detail = "; ".join("%s: %s" % f for f in reported) or "-"
        rows.append("%-22s %-12s %s" % (path.name, label, detail))
    print("\n".join(rows))
    unnamed = unnamed_addenda()
    if unnamed:
        print("\n" + "\n".join("adendo que nenhuma abertura nomeia: %s" % name for name in unnamed))
    print("\n%d ok, %d excecao(oes), %d historico, %d falha(s)" % (ok, excepted, history, failed))
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
