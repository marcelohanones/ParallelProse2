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
PENDING_LIMIT = 15 * 60  # P-d: rascunho com o marcador por mais disso vira aviso
POLL_SECONDS = 10  # o monitor consulta a pasta a cada dez segundos
NOTICES_KEPT = 20
# acrescentado à linha de disparo, nos dois lados: aponta o procedimento do contrato em vez de
# copiá-lo, para não envelhecer; e a investigação do ambiente não é passo de rodada
PROCEDURE_NOTE = (" Siga o procedimento de rodada de docs/auto_critique2.md (sete passos). "
                  "Não investigue o ambiente.")


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
        # só os campos que o contrato conhece: resíduo de versões antigas sai na gravação
        chain = loaded.get("chain", {})
        state["chain"] = {key: chain.get(key, default) for key, default in new_state()["chain"].items()}
    return state


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    os.replace(tmp, path)


def in_writing(path: Path) -> bool:
    """Rascunho: o cabeçalho ainda traz o marcador 0000, e a escrita do autor não terminou."""
    return bool(re.search(r"^<!-- sent: 0000\b", path.read_text(encoding="utf-8"), re.M))


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
    entries.sort(key=lambda e: (e["round"], e["side"]))  # por número de rodada, não pelo texto do nome
    return entries


def cited_names(path: Path) -> set[str]:
    """Os arquivos que a abertura cita: a linha "Segue a mensagem ..." da rodada."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Segue "):
            return set(re.findall(r"R\d+-[a-z]+\.md", line))
    return set()


def pair_trigger(turns: list[dict]) -> dict | None:
    """Dois turnos da mesma rodada, de lados diferentes: o último é o que cita o outro.

    Sem citação, ou com citação mútua, não há último: devolve None e ninguém dispara.
    """
    if len(turns) != 2:
        return None
    first, second = turns
    if first["round"] != second["round"] or first["side"] == second["side"]:
        return None
    first_cites_second = second["name"] in cited_names(first["path"])
    second_cites_first = first["name"] in cited_names(second["path"])
    if first_cites_second and not second_cites_first:
        return first
    if second_cites_first and not first_cites_second:
        return second
    return None


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
    """Roda e devolve a saída: é dela que sai a reconciliação de passos da Regra 6."""
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


def count_steps(stdout: str) -> int | None:
    """Passos de modelo do salto: os eventos step_start do stdout JSON. Texto puro é sem base."""
    count = 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("phase") == "step_start":
            count += 1
    return count if count else None


def predicted_steps(hop_logs: Path | None, responder: str) -> float | None:
    """A previsão do salto: a mediana de todas as medidas do mesmo lado, a partir de três. Antes, sem base."""
    if hop_logs is None or not (hop_logs / "index.jsonl").exists():
        return None
    measured = []
    for line in (hop_logs / "index.jsonl").read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        if entry.get("responder") == responder and entry.get("status") == "salto" and entry.get("passos") is not None:
            measured.append(entry["passos"])
    if len(measured) < 3:
        return None
    measured.sort()
    middle = len(measured) // 2
    if len(measured) % 2:
        return measured[middle]
    return (measured[middle - 1] + measured[middle]) / 2


def record_hop(hop_logs: Path | None, plan: dict, trigger: dict, status: str, reason: str,
               log_path: Path | None, passos: int | None = None, previsto: float | None = None) -> None:
    """Uma linha por salto: rodada, alvo, motivo, caminho do log, e os passos contra a previsão."""
    if hop_logs is None:
        return
    hop_logs.mkdir(parents=True, exist_ok=True)
    entry = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "round": plan["round"],
             "responder": plan["responder"],
             "target": "R%d-%s.md" % (plan["round"], plan["responder"]), "trigger": trigger["name"],
             "status": status, "reason": reason, "log": str(log_path) if log_path else None,
             "passos": passos, "previsto": previsto}
    with (hop_logs / "index.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + chr(10))


def passos_of(output: dict | None) -> int | None:
    """Os passos do salto a partir da saída que o dispatch devolveu; sem saída, sem base."""
    if not output or "stdout" not in output:
        return None
    return count_steps(output.get("stdout") or "")


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
    names_now = {e["name"] for e in scan(reviews)}
    if state.get("ambiguous") and set(state["ambiguous"]) != names_now:
        state.pop("ambiguous")  # o registro mudou: a ambiguidade de antes não vale mais
    stale = state.pop("disparando", None)  # um salto que não voltou: o processo caiu durante ele
    if stale and hop_logs is not None and not dry_run:
        record_hop(hop_logs, stale, {"name": stale["trigger"]}, "salto-interrompido",
                   "o processo caiu durante o salto; olhar humano", None, previsto=stale.get("previsto"))
    result = {"action": "idle", "reason": "", "line": "", "responder": "", "notices": []}

    def note(text: str) -> None:
        result["notices"].append(text)
        state["notices"] = (state["notices"] + [text])[-NOTICES_KEPT:]

    if stale:
        note("salto interrompido: %s (gatilho %s); olhar humano, sem novo disparo" % (
            stale["target"], stale["trigger"]))
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

    # adendo não abre nem fecha rodada: é marcado e avisado, e não conta para o par
    addenda = [e for e in new if e["suffix"] is not None]
    for entry in addenda:
        seen[entry["name"]] = entry["sha"]
        note("adendo %s: não abre nem fecha rodada, e não dispara" % entry["name"])
    turns = [e for e in new if e["suffix"] is None]
    # rascunho (cabeçalho ainda com 0000) não é turno: espera, e não entra em seen
    drafts = {e["name"] for e in turns if in_writing(e["path"])}
    turns = [e for e in turns if e["name"] not in drafts]
    waiting = state.get("pending", {})
    state["pending"] = {name: waiting.get(name, {"since": time.time(), "warned": False}) for name in drafts}
    for name in drafts:
        entry = state["pending"][name]
        if not entry["warned"] and time.time() - entry["since"] > PENDING_LIMIT:
            entry["warned"] = True
            note("%s segue em 0000 há mais de 15 min: aviso, não FALHA" % name)
    if not turns:
        result["action"] = "pending" if drafts else ("notice" if (changed or gone or addenda) else "idle")
        return result
    if len(turns) > 1:
        # o par que chega junto colapsa no último escritor, pela citação; o resto não dispara
        trigger_pair = pair_trigger(turns)
        if trigger_pair is None:
            for entry in turns:
                seen[entry["name"]] = entry["sha"]
            state["ambiguous"] = sorted(e["name"] for e in turns)  # fica no estado até o registro mudar
            note("mais de um arquivo novo (%s); o watcher nao escolhe" % ", ".join(e["name"] for e in turns))
            result["action"] = "ambiguous"
            return result
        for entry in turns:
            if entry is not trigger_pair:
                seen[entry["name"]] = entry["sha"]
        turns = [trigger_pair]

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
    # a marca em seen e o registro do salto vão na mesma gravação, antes do subprocesso:
    # separadas, uma queda entre as duas perderia o arquivo sem aviso
    previsto = predicted_steps(hop_logs, plan["responder"])  # declarada antes do disparo
    state["disparando"] = {"hop": hop, "round": plan["round"], "responder": plan["responder"],
                           "trigger": trigger["name"], "target": target, "previsto": previsto,
                           "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    save_now()
    ok, why, argv, output = dispatch(plan["responder"], plan["line"], state, dsh_bin, timeout,
                                     target, hop)
    state.pop("disparando", None)  # o salto voltou: não é mais um salto em curso
    log_path = write_hop_log(hop_logs, trigger, plan, output) if (hop_logs is not None and output) else None
    if not ok:
        if argv is None:  # lado sem comando configurado: recusa, nao tentativa falha
            note("nao disparo: %s" % why)
            result.update(action="refuse", reason="comando", line=plan["line"], responder=plan["responder"])
        else:
            note("disparo falhou: %s (alvo %s, gatilho %s): %s" % (plan["responder"], target, trigger["name"], why))
            record_hop(hop_logs, plan, trigger, "falha-de-salto", why, log_path,
                       passos=passos_of(output), previsto=previsto)
            result.update(action="failed", reason=why, line=plan["line"], responder=plan["responder"])
        return result

    # o salto saiu com 0: a resposta tem de estar no registro ao fim. Se não está, o salto
    # rodou (conta), é registrado e avisado, e não é repetido: um lado escreve uma vez por número
    if target not in {e["name"] for e in scan(reviews)}:
        chain["count"] += 1
        chain["last_hop"] = {"round": trigger["round"], "trigger": trigger["name"], "responder": plan["responder"]}
        note("sem resposta: o salto saiu com 0 e nao gravou %s (gatilho %s); aviso, sem nova tentativa"
             % (target, trigger["name"]))
        record_hop(hop_logs, plan, trigger, "sem-resposta", "", log_path,
                   passos=passos_of(output), previsto=previsto)
        save_now()
        result.update(action="no-answer", reason="sem-resposta", line=plan["line"], responder=plan["responder"])
        return result

    # A frase de regra de arquivo nao casada vem com returncode 0. Se ficasse so
    # no hop log, ela sumiria do chat: o hop que gravou a R7-cc a carregou e ela
    # levou tres rodadas para aparecer.
    warning = "is not matched by file permission checks"
    stderr = (output or {}).get("stderr") or ""
    if plan["responder"] == "cc" and warning in stderr:
        line = next((text.strip() for text in stderr.splitlines() if warning in text), "")
        note("aviso no stderr do lado cc: %s" % line[:200])

    passos = passos_of(output)
    record_hop(hop_logs, plan, trigger, "salto", "", log_path, passos=passos, previsto=previsto)
    if passos is not None and previsto is not None and passos > 2 * previsto:
        note("salto %s: %d passos, previsto %g: fora do previsto" % (target, passos, previsto))
    chain["count"] += 1
    chain["last_hop"] = {"round": trigger["round"], "trigger": trigger["name"], "responder": plan["responder"]}
    save_now()
    note("salto %d: %s -> %s" % (chain["count"], trigger["name"], plan["line"]))
    result.update(action="dispatch", line=plan["line"], responder=plan["responder"], argv=argv)
    return result


def start_new_series(state_path: Path, reviews: Path) -> tuple[int, str]:
    """Abre uma série nova: o registro tem de estar vazio, e o estado anterior vai para o arquivo."""
    leftover = scan(reviews)
    if leftover:
        return 1, "nao abro a serie: o registro tem %d arquivo(s); apague a serie anterior antes" % len(leftover)
    archive_dir = state_path.parent / ".watcher-series"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived = archive_dir / ("estado-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    if state_path.exists():
        archived.write_text(state_path.read_text(encoding="utf-8"), encoding="utf-8")
    fresh = new_state()
    fresh["cc_argv"] = load_state(state_path).get("cc_argv")
    fresh["initialized"] = True  # registro vazio é a linha de base: qualquer arquivo depois dela é novo
    fresh["notices"] = ["serie nova: estado anterior em %s" % archived.name]
    save_state(state_path, fresh)
    return 0, "serie nova: estado anterior arquivado em %s" % archived


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lock_holder(lock: Path) -> int | None:
    """O pid que segura a trava, se ele ainda vive; trava de pid morto não segura nada."""
    try:
        holder = int(lock.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return holder if pid_alive(holder) else None


def monitor_alive(lock: Path) -> bool:
    """O monitor está vivo quando a trava é de um pid vivo. O marcador é proveniência, não autoridade."""
    return lock_holder(lock) is not None


def acquire_lock(lock: Path) -> bool:
    """Trava de criação exclusiva: o segundo monitor falha aqui, antes de tocar no estado.

    Uma trava de pid morto é retomada; uma de pid vivo recusa.
    """
    for _ in range(2):
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                holder = int(lock.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                holder = None
            if holder is not None and pid_alive(holder):
                return False
            lock.unlink(missing_ok=True)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        return True
    return False


def release_lock(lock: Path) -> None:
    """Sai com a trava só quando ela é do próprio processo."""
    try:
        if lock.read_text(encoding="utf-8").strip() == str(os.getpid()):
            lock.unlink()
    except OSError:
        pass


def watch(reviews: Path, state_path: Path, hop_logs: Path, *, dsh_bin: str = DSH_BIN,
          timeout: int = TIMEOUT, interval: float = POLL_SECONDS, max_ticks: int | None = None,
          sleep=time.sleep, lock_path: Path | None = None) -> int:
    """O monitor: consulta a pasta, e processa quando ela ficou igual numa consulta.

    Um salto por vez: a passada é síncrona, e a consulta seguinte só acontece depois dela.
    Um rascunho pendente (0000) mantém a passada rodando, para o P-d contar o tempo.
    A trava de criação exclusiva é tomada antes de qualquer leitura do estado.
    """
    lock = lock_path or state_path.parent / "monitor.lock"
    if not acquire_lock(lock):
        print("monitor ativo: outra trava segura %s; nada foi lido nem gravado" % lock.name)
        return 1
    try:
        return _watch_loop(reviews, state_path, hop_logs, dsh_bin=dsh_bin, timeout=timeout,
                           interval=interval, max_ticks=max_ticks, sleep=sleep)
    finally:
        release_lock(lock)


def _watch_loop(reviews: Path, state_path: Path, hop_logs: Path, *, dsh_bin: str, timeout: int,
                interval: float, max_ticks: int | None, sleep) -> int:
    marker = {"pid": os.getpid(), "since": time.strftime("%Y-%m-%dT%H:%M:%S")}
    state = load_state(state_path)
    state["monitor"] = marker
    save_state(state_path, state)
    previous = processed = None
    tick = 0
    try:
        while max_ticks is None or tick < max_ticks:
            state = load_state(state_path)  # relê: um comando feito no meio da sessão não é desfeito
            snapshot = {e["name"]: e["sha"] for e in scan(reviews)}
            stable = snapshot == previous
            if stable and (snapshot != processed or state.get("pending")):
                result = run_pass(reviews, state, dsh_bin=dsh_bin, timeout=timeout, hop_logs=hop_logs,
                                  persist=lambda current: save_state(state_path, current))
                save_state(state_path, state)
                for line in result["notices"]:
                    print(line, flush=True)
                processed = snapshot
            previous = snapshot
            tick += 1
            sleep(interval)
    finally:
        state = load_state(state_path)
        if state.get("monitor", {}).get("pid") == os.getpid():  # só apaga o próprio marcador
            state.pop("monitor")
            save_state(state_path, state)
    return 0


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
    parser.add_argument("--new-series", action="store_true")
    parser.add_argument("--monitor", action="store_true")
    parser.add_argument("--set-cc-cmd")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    state_path = Path(args.state)
    lock = state_path.parent / "monitor.lock"  # a autoridade sobre "há monitor vivo"
    state = load_state(state_path)

    if args.status:
        chain = state["chain"]
        print("registro: %d arquivo(s) no estado; cadeia: %d salto(s) desde o ultimo reset" % (
            len(state["seen"]), chain["count"]))
        if chain.get("last_hop"):
            print("ultimo salto: %s" % chain["last_hop"])
        for line in state["notices"][-5:]:
            print("  " + line)
        monitor = state.get("monitor")
        holder = lock_holder(lock)
        if holder is not None:
            print("monitor ativo pela trava (pid %s)" % holder)
        elif monitor:
            print("monitor marcado, sem processo (pid %s, desde %s)" % (monitor["pid"], monitor["since"]))
        if state.get("ambiguous"):
            print("ambiguidade pendente: %s" % ", ".join(state["ambiguous"]))
        index = Path(args.hop_logs) / "index.jsonl"
        if index.exists():
            for line in index.read_text(encoding="utf-8").splitlines()[-5:]:
                entry = json.loads(line)
                label = "salto" if entry["status"] == "salto" else "falha"
                print("  %s: %s (%s), gatilho %s, passos %s, previsto %s" % (
                    label, entry["target"], entry["status"], entry["trigger"],
                    entry.get("passos"), entry.get("previsto")))
        return 0

    if monitor_alive(lock) and (args.reset or args.set_cc_cmd or args.new_series):
        print("monitor ativo pela trava (pid %s): pare-o antes de mexer no estado" % lock_holder(lock))
        return 1

    if args.reset:
        previous = state["chain"]["count"]
        state["chain"]["count"] = 0
        state["chain"]["last_hop"] = None
        state["notices"] = (state["notices"] + [
            "reset manual: contador %d -> 0" % previous])[-NOTICES_KEPT:]
        save_state(state_path, state)
        print("contador zerado: o Markim disparou a mao")
        return 0

    if args.monitor:
        if monitor_alive(lock):
            print("monitor ativo pela trava (pid %s): ja ha um monitor nesta pasta" % lock_holder(lock))
            return 1
        return watch(Path(args.reviews), state_path, Path(args.hop_logs), dsh_bin=args.dsh_bin,
                     timeout=args.timeout)

    if args.new_series:
        code, message = start_new_series(state_path, Path(args.reviews))
        print(message)
        return code

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
    return 1 if result["action"] in ("refuse", "failed", "error", "no-answer") else 0


if __name__ == "__main__":
    sys.exit(main())
