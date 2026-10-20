#!/usr/bin/env python3
"""Watcher da troca automática — uma execução por chamada, cinco passos.

  1. reconcilia: lista docs/reviews, compara com o estado, e sabe quem escreveu;
  2. checa: analyze() sobre o arquivo liberado, nunca sobre a pasta;
  3. decide: gate sem pergunta em aberto dispara; com pergunta, não dispara e avisa;
  4. dispara: `dsh --profile headless "<linha>"`, fora do sandbox;
  5. conta: o salto, para relatar; nao ha trava.

Ele nunca escreve no registro e nunca responde por um harness. O que ele escreve
é o próprio estado, em tools/.watcher-state.json, fora de docs/reviews.

Uso:
    python3 tools/watcher_auto_critique.py            # uma passada
    python3 tools/watcher_auto_critique.py --dry-run  # decide e mostra, não dispara
    python3 tools/watcher_auto_critique.py --reset    # zera o contador de relato
    python3 tools/watcher_auto_critique.py --set-cc-cmd "claude -p --permission-prompts none"
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_auto_critique as chk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
STATE = ROOT / "tools" / ".watcher-state.json"
HOP_LOGS = ROOT / "tools" / ".watcher-hops"
DSH_BIN = "dsh"
TIMEOUT = 1800
NOTICES_KEPT = 20
# acrescentado à linha de disparo do dsh: o procedimento da v12 não é opcional, e a
# investigação do ambiente não é passo de rodada (R15-cc, medido na R15-dsh)
PROCEDURE_NOTE = (" Siga o procedimento de rodada da v12 (sete passos): leitura em lote, "
                  "escrita única, contagem única, checador no fim. Não investigue o ambiente.")


def new_state() -> dict:
    return {
        "initialized": False,
        "seen": {},
        "chain": {
            "count": 0,
            "last_hop": None,
        },
        "notices": [],
        "cc_argv": None,
    }


def load_state(path: Path) -> dict:
    state = new_state()
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        state.update(loaded)
        state["chain"] = {**new_state()["chain"], **loaded.get("chain", {})}
    return state


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    os.replace(tmp, path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan(reviews: Path) -> list[dict]:
    """Os arquivos de rodada da pasta: nome é identidade, sha detecta reescrita."""
    entries = []
    for path in sorted(reviews.glob("*.md")):
        parsed = chk.parse_round_name(path.name)
        if not parsed:
            continue
        round_no, side, suffix = parsed
        entries.append({
            "name": path.name,
            "path": path,
            "round": round_no,
            "side": side,
            "suffix": suffix,
            "sha": sha256(path),
        })
    return entries


def sides_of(entries: list[dict], round_no: int) -> set[str]:
    """Os lados que já escreveram a rodada; adendo não conta para o par."""
    return {e["side"] for e in entries if e["round"] == round_no and e["suffix"] is None}


def dispatch_line(trigger: dict, entries: list[dict]) -> dict:
    """A linha de disparo, na forma que o contrato dá para cada caso."""
    round_no, side = trigger["round"], trigger["side"]
    other = "dsh" if side == "cc" else "cc"
    if other in sides_of(entries, round_no):
        target = round_no + 1
        line = "par completo:   leia docs/reviews/R%d-%s.md e responda em R%d-%s.md" % (
            round_no, side, target, other)
    else:
        target = round_no
        line = "rodada aberta:  leia docs/reviews/R%d-%s.md e responda em R%d-%s.md" % (
            round_no, side, target, other)
    return {"line": line, "responder": other, "round": target}


def dsh_home() -> Path:
    return Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))


def preflight() -> tuple[bool, str]:
    """O perfil do dsh é gravado em ~/.dsh; um sandbox bloqueia ali antes da API."""
    home = dsh_home()
    try:
        home.mkdir(parents=True, exist_ok=True)
        probe = home / ".watcher-probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return False, "escrita bloqueada em %s (%s); rode fora do sandbox" % (
            home, exc.strerror or exc)
    return True, ""


def run_argv(argv: list[str], timeout: int, env: dict | None = None) -> tuple[bool, str, dict]:
    """Roda e devolve a saída: é dela que sai a reconciliação de tokens da Regra 6."""
    try:
        proc = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout,
                              env=env)
    except OSError as exc:
        return False, "falha ao executar %s: %s" % (argv[0], exc), {"argv": argv, "error": str(exc)}
    except subprocess.TimeoutExpired:
        return False, "timeout de %ds" % timeout, {"argv": argv, "error": "timeout"}
    output = {"argv": argv, "returncode": proc.returncode,
              "stdout": proc.stdout, "stderr": proc.stderr}
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-1:] or [""]
        return False, "saiu com %d: %s" % (proc.returncode, tail[0][:200]), output
    return True, "", output


def dispatch(responder: str, line: str, state: dict, dsh_bin: str, timeout: int, target: str,
             hop: str):
    # os dois lados seguem o mesmo protocolo: o trecho vai na linha de disparo de cada um
    line = line + PROCEDURE_NOTE
    if responder == "dsh":
        # --json troca a mensagem final pelos eventos do passo, com o uso de cada
        # chamada: e do stdout do salto que sai a reconciliacao da Regra 6.
        argv = [dsh_bin, "--profile", "headless", "--json", line]
    else:
        cc = state.get("cc_argv")
        if not cc:
            return False, "lado cc sem comando configurado; o watcher nao chuta", None, {}
        template = list(cc)
        if any("{line}" in part or "{target}" in part for part in template):
            argv = [part.replace("{line}", line).replace("{target}", target) for part in template]
        else:
            argv = template + [line]
    # O salto se anuncia no ambiente: a sessao o le na abertura, sem subir a
    # cadeia de pais com ps (que nao casa com o comando aprovado).
    env = dict(os.environ)
    env["WATCHER_HOP"] = hop
    ok, reason, output = run_argv(argv, timeout, env=env)
    return ok, reason, argv, output


def write_hop_log(log_dir: Path, trigger: dict, plan: dict, output: dict) -> Path:
    """Guarda a saída do salto fora do registro: reconciliação sem mensagem nova."""
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = "%d" % time.time_ns()
    path = log_dir / ("hop-%s-R%d-%s.json" % (stamp, plan["round"], plan["responder"]))
    record = {"round": plan["round"], "responder": plan["responder"], "line": plan["line"],
              "trigger": trigger["name"], "output": output}
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    return path


def run_pass(reviews: Path, state: dict, *, dsh_bin: str = DSH_BIN, timeout: int = TIMEOUT,
             dry_run: bool = False, hop_logs: Path | None = None, persist=None) -> dict:
    """Uma passada: reconciliar, checar, decidir, disparar, contar.

    persist(state) grava o estado nos pontos em que uma interrupção custaria
    dinheiro: depois da linha de base e depois de marcar o arquivo liberado como
    visto, antes do disparo. Sem isso, uma passada morta durante um salto volta
    com o mesmo arquivo novo e o dispara de novo.
    """
    if dry_run:
        # o modo seco trabalha numa cópia: nada do estado real é marcado nem gravado
        state = copy.deepcopy(state)
        persist = None

    def save_now() -> None:
        if persist is not None:
            persist(state)

    entries = scan(reviews)
    seen = state["seen"]
    result = {"action": "idle", "reason": "", "line": "", "responder": "", "notices": []}

    def note(text: str) -> None:
        result["notices"].append(text)
        state["notices"] = (state["notices"] + [text])[-NOTICES_KEPT:]

    new = [e for e in entries if e["name"] not in seen]
    changed = [e for e in entries if e["name"] in seen and seen[e["name"]] != e["sha"]]
    gone = [name for name in seen if name not in {e["name"] for e in entries}]

    if not state.get("initialized"):
        for entry in entries:
            seen[entry["name"]] = entry["sha"]
        state["initialized"] = True
        note("linha de base: %d arquivo(s) no registro, nenhum disparo" % len(entries))
        save_now()
        result["action"] = "baseline"
        return result

    for entry in changed:
        seen[entry["name"]] = entry["sha"]
        note("arquivo reescrito nao e mensagem nova, e nao dispara: %s" % entry["name"])
    for name in gone:
        del seen[name]
        note("arquivo saiu do registro: %s" % name)

    turns = [e for e in new if e["suffix"] is None]
    if not turns:
        result["action"] = "notice" if (changed or gone) else "idle"
        return result
    if len(turns) > 1:
        for entry in turns:
            seen[entry["name"]] = entry["sha"]
        note("mais de um arquivo novo (%s); o watcher nao escolhe" % ", ".join(e["name"] for e in turns))
        result["action"] = "ambiguous"
        return result

    trigger = turns[0]
    chk.REVIEWS = reviews  # a chave do checador resolve contra o mesmo registro
    try:
        findings = chk.analyze(trigger["path"])
    except OSError as exc:
        note("nao consegui ler %s: %s" % (trigger["name"], exc))
        result["action"] = "error"
        return result
    label, reported = chk.classify(trigger["round"], findings, chk.load_exceptions().get(trigger["name"], set()))
    keys = chk.gate_keys(trigger["path"])
    header = chk.header_keys(trigger["path"])
    seen[trigger["name"]] = trigger["sha"]
    save_now()  # antes de qualquer decisao: um salto interrompido nao volta
    chain = state["chain"]

    if label == "FALHA":
        detail = "; ".join("%s: %s" % pair for pair in reported)
        note("FALHA em %s (%s) — recuso o salto, a mensagem fica" % (trigger["name"], detail))
        result.update(action="refuse", reason="FALHA")
        return result

    if header.get("gap"):
        chain["count"] = 0
        note("gap declarado em %s: a vez fecha sem arquivo, contador zerado" % trigger["name"])
        result.update(action="hold", reason="gap")
        return result

    if keys.get("blocks-advance") == "yes":
        note("%s bloqueia o avanco (to-markim: %s); nao disparo" % (
            trigger["name"], keys.get("to-markim", "")))
        result.update(action="hold", reason="blocks-advance")
        return result

    later = [e["round"] for e in entries if e["round"] > trigger["round"]]
    if later:
        note("R%d ja existe; %s chegou fora de ordem, nao disparo" % (min(later), trigger["name"]))
        result.update(action="refuse", reason="fora de ordem")
        return result

    plan = dispatch_line(trigger, entries)

    if dry_run:
        note("dry-run: dispararia %s -> %s" % (plan["responder"], plan["line"]))
        result.update(action="dry-run", line=plan["line"], responder=plan["responder"])
        return result

    if plan["responder"] == "dsh":  # a sonda e do dsh; o lado cc nao usa ~/.dsh
        ok, why = preflight()
        if not ok:
            note("nao disparo: %s" % why)
            result.update(action="refuse", reason="preflight", line=plan["line"], responder=plan["responder"])
            return result

    hop = "R%d-%s" % (plan["round"], plan["responder"])
    target = hop + ".md"
    ok, why, argv, output = dispatch(plan["responder"], plan["line"], state, dsh_bin, timeout,
                                     target, hop)
    if hop_logs is not None and output:
        write_hop_log(hop_logs, trigger, plan, output)
    if not ok:
        if argv is None:  # lado sem comando configurado: recusa, nao tentativa falha
            note("nao disparo: %s" % why)
            result.update(action="refuse", reason="comando", line=plan["line"], responder=plan["responder"])
        else:
            note("disparo falhou (%s): %s" % (plan["responder"], why))
            result.update(action="failed", reason=why, line=plan["line"], responder=plan["responder"])
        return result

    # A frase de regra de arquivo nao casada vem com returncode 0. Se ficasse so
    # no hop log, ela sumiria do chat: o hop que gravou a R7-cc a carregou e ela
    # levou tres rodadas para aparecer.
    warning = "is not matched by file permission checks"
    stderr = (output or {}).get("stderr") or ""
    if plan["responder"] == "cc" and warning in stderr:
        line = next((text.strip() for text in stderr.splitlines() if warning in text), "")
        note("aviso no stderr do lado cc: %s" % line[:200])

    chain["count"] += 1
    chain["last_hop"] = {"round": trigger["round"], "trigger": trigger["name"], "responder": plan["responder"]}
    save_now()
    note("salto %d: %s -> %s" % (chain["count"], trigger["name"], plan["line"]))
    result.update(action="dispatch", line=plan["line"], responder=plan["responder"], argv=argv)
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Watcher da troca automatica (cinco passos, uma passada).")
    parser.add_argument("--state", default=str(STATE))
    parser.add_argument("--reviews", default=str(REVIEWS))
    parser.add_argument("--hop-logs", default=str(HOP_LOGS))
    parser.add_argument("--dsh", dest="dsh_bin", default=DSH_BIN)
    parser.add_argument("--timeout", type=int, default=TIMEOUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--set-cc-cmd")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    state_path = Path(args.state)
    state = load_state(state_path)

    if args.status:
        chain = state["chain"]
        print("registro: %d arquivo(s) no estado; cadeia: %d salto(s) desde o ultimo reset" % (
            len(state["seen"]), chain["count"]))
        if chain.get("last_hop"):
            print("ultimo salto: %s" % chain["last_hop"])
        for line in state["notices"][-5:]:
            print("  " + line)
        return 0

    if args.reset:
        previous = state["chain"]["count"]
        state["chain"]["count"] = 0
        state["chain"]["last_hop"] = None
        state["notices"] = (state["notices"] + [
            "reset manual: contador %d -> 0" % previous])[-NOTICES_KEPT:]
        save_state(state_path, state)
        print("contador zerado: o Markim disparou a mao")
        return 0

    if args.set_cc_cmd:
        state["cc_argv"] = shlex.split(args.set_cc_cmd)
        save_state(state_path, state)
        print("comando do lado cc: %s" % " ".join(state["cc_argv"]))
        return 0

    result = run_pass(Path(args.reviews), state, dsh_bin=args.dsh_bin,
                      timeout=args.timeout, dry_run=args.dry_run,
                      hop_logs=Path(args.hop_logs),
                      persist=lambda current: save_state(state_path, current))
    for line in result["notices"]:
        print(line)
    if result["action"] == "idle":
        print("nada novo no registro")
    if not args.dry_run:
        save_state(state_path, state)
    return 1 if result["action"] in ("refuse", "failed", "error") else 0


if __name__ == "__main__":
    sys.exit(main())
