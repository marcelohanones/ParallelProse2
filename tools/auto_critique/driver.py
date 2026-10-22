#!/usr/bin/env python3
"""Lado Claude do laço, pela CLI.

Recebe a resposta do dsh, chama `claude -p` numa sessão só (modo A: uma sessão
contínua, guardada em SESSION_FILE) e grava a mensagem entre marcadores em OUT_FILE.
Com --trigger, dispara hammerspoon://cctodsh, que é o contrato de entrada da perna dsh.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid

SESSION_FILE = "/tmp/cli_session_id.txt"
LOG_FILE = "/tmp/cli_driver_log.txt"
FLAG_FILE = "/tmp/loop_on"
OUT_FILE = "/tmp/cc_last_answer.txt"
# Fora do repositório: o CLI não carrega CLAUDE.md nem hooks do projeto.
WORK_DIR = "/private/tmp/critique_cli_work"
DEFAULT_CLAUDE_BIN = "/Users/marcelohanones/.local/bin/claude"

INSTRUCAO = (
    "Responda à mensagem abaixo. Escreva o texto que deve seguir para o outro "
    "interlocutor entre <<<MSG e MSG>>>, sem nada fora dos marcadores."
)
MSG_RE = re.compile(r"<<<MSG\s*(.*?)\s*MSG>>>", re.DOTALL)


def extract(text):
    """Devolve o trecho entre marcadores, ou None se faltar marcador ou se o trecho for vazio."""
    m = MSG_RE.search(text or "")
    if not m:
        return None
    body = m.group(1).strip()
    return body or None


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S") + " " + msg + "\n")


def session_args(new, dry_run):
    """Devolve (argumentos, uuid, é_nova). Só grava o arquivo da sessão fora do dry-run."""
    if new or not os.path.exists(SESSION_FILE):
        sid = str(uuid.uuid4())
        if not dry_run:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                f.write(sid)
        return ["--session-id", sid], sid, True
    with open(SESSION_FILE, encoding="utf-8") as f:
        sid = f.read().strip()
    return ["--resume", sid], sid, False


def call_claude(claude_bin, sess_args, prompt):
    # Sem ferramentas e sem servidores MCP: cada chamada vira uma única requisição ao modelo.
    cmd = [claude_bin, "-p", *sess_args, "--output-format", "json",
           "--tools", "", "--strict-mcp-config", prompt]
    r = subprocess.run(cmd, cwd=WORK_DIR, capture_output=True, text=True, timeout=600)
    try:
        data = json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        data = {}
    return r.returncode, data


def fail(motivo):
    log("FALHA: " + motivo + " (laço parado)")
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="arquivo com o texto que vai ao Claude")
    ap.add_argument("--claude-bin", default=DEFAULT_CLAUDE_BIN)
    ap.add_argument("--new-session", action="store_true", help="cria uma sessão nova em vez de retomar")
    ap.add_argument("--trigger", action="store_true", help="dispara hammerspoon://cctodsh ao gravar a saída")
    ap.add_argument("--dry-run", action="store_true", help="mostra o comando sem chamar o claude")
    a = ap.parse_args()

    os.makedirs(WORK_DIR, exist_ok=True)
    with open(a.input, encoding="utf-8") as f:
        text = f.read()
    sess_args, sid, nova = session_args(a.new_session, a.dry_run)
    prompt = INSTRUCAO + "\n\n" + text

    if a.dry_run:
        print("comando:", [a.claude_bin, "-p", *sess_args, "--output-format", "json", f"<prompt de {len(prompt)} caracteres>"])
        print("sessão:", sid, "(nova)" if nova else "(retomada)")
        return 0

    t0 = time.time()
    rc, data = call_claude(a.claude_bin, sess_args, prompt)
    wall = time.time() - t0
    log(
        f"chamada sid={sid} modo={'session-id' if nova else 'resume'} rc={rc} "
        f"is_error={data.get('is_error')} num_turns={data.get('num_turns')} "
        f"api_ms={data.get('duration_api_ms')} wall_s={wall:.1f}"
    )
    if rc != 0 or data.get("is_error", True) or "result" not in data:
        return fail("erro na chamada ao claude")

    msg = extract(data["result"])
    if msg is None:
        return fail("sem marcadores <<<MSG ... MSG>>> com conteúdo na resposta")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(msg)
    log(f"mensagem gravada ({len(msg)} caracteres)")

    if a.trigger:
        subprocess.run(["open", "-g", "hammerspoon://cctodsh"], check=False)
        log("cctodsh disparado")
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
