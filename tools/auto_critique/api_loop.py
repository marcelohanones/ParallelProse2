#!/usr/bin/env python3
"""Laço Claude <-> dsh pela API local do dsh (sem clipboard, foco ou botão Copy).

Lado Claude: driver.py (claude -p --resume, sessão única).
Entrada no dsh: session/prompt.  Saída do dsh: session/page (texto completo do assistente).
Precisa do token de lançamento do `dsh web`, guardado num arquivo de uso pessoal.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid

DSH = "http://127.0.0.1:3080"
HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.path.join(HERE, "driver.py")
OUT_FILE = "/tmp/cc_last_answer.txt"  # o driver grava aqui a mensagem do Claude
WORK = "/private/tmp/critique_cli_work"
LOG = os.path.join(WORK, "api_loop.log")


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def auth(token_file, jar):
    """Troca o token de lançamento por cookie de sessão. O token não é impresso."""
    with open(token_file, encoding="utf-8") as f:
        token = f.read().strip()
    subprocess.run(["curl", "-s", "-m", "10", "-c", jar, "-o", "/dev/null", f"{DSH}/?token={token}"], check=True)


def rpc(jar, method, args):
    body = {"type": "client-request", "rpcId": str(uuid.uuid4()), "method": method, "payload": {"args": args}}
    out = subprocess.run(
        ["curl", "-s", "-m", "30", "-b", jar, "-H", "content-type: application/json",
         "-X", "POST", f"{DSH}/api/{method}", "-d", json.dumps(body)],
        capture_output=True, text=True,
    ).stdout
    res = json.loads(out).get("result", {})
    if not res.get("ok"):
        raise RuntimeError(f"{method}: {res.get('error', {}).get('code')}")
    return res["value"]


def history(jar, sid):
    items = rpc(jar, "session/list", {"_request": {}})["items"]
    seq = next(s for s in items if s["sessionId"] == sid)["projections"]["asOfSeq"]
    value = rpc(jar, "session/page", {"request": {
        "address": {"kind": "session", "sessionId": sid},
        "throughSeq": seq, "maxMessages": 4,
        "turnWindow": {"minMessages": 1, "minTurns": 1},
    }})
    return value["records"]


def event_text(e):
    msg = (e.get("data") or {}).get("message") or {}
    parts = [c.get("text", "") for c in msg.get("content", []) if c.get("type") == "text"]
    return "\n".join(p for p in parts if p)


def send_to_dsh(jar, sid, text):
    rid = str(uuid.uuid4())
    rpc(jar, "session/prompt", {"request": {
        "requestId": rid, "sessionId": sid, "mode": "queue",
        "content": [{"type": "text", "text": text}],
    }})
    return rid


def wait_reply(jar, sid, sent, timeout=180):
    """Espera a resposta do assistente que vem depois da mensagem enviada."""
    t0 = time.time()
    needle = json.dumps(sent, ensure_ascii=False)[1:-1]  # forma escapada, como aparece no JSON do histórico
    while time.time() - t0 < timeout:
        recs = history(jar, sid)
        idx = None
        for i, r in enumerate(recs):
            e = r["event"]
            if e.get("type") == "user/message" and needle in json.dumps(e, ensure_ascii=False):
                idx = i
        if idx is not None:
            for r in recs[idx + 1:]:
                e = r["event"]
                if e.get("type") == "assistant/message":
                    txt = event_text(e)
                    if txt:
                        return txt, e.get("time") / 1000.0
        time.sleep(1)
    return None, None


def claude_reply(input_text, rnd):
    path = os.path.join(WORK, f"api_in_{rnd}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(input_text)
    t0 = time.time()
    r = subprocess.run([sys.executable, "-I", DRIVER, "--input", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"driver falhou: {r.stdout[-200:]} {r.stderr[-200:]}")
    with open(OUT_FILE, encoding="utf-8") as f:
        return f.read(), t0, time.time()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--max-rounds", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    jar = os.path.join(WORK, "jar.txt")
    auth(a.token_file, jar)
    log(f"inicio: sessao {a.session_id}, limite {a.max_rounds} rodadas, sem clipboard/Copy")

    claude_in = "Responda com uma frase curta sobre o laço entre Claude e dsh."
    for rnd in range(1, a.max_rounds + 1):
        msg, c0, c1 = claude_reply(claude_in, rnd)
        log(f"rodada {rnd}: Claude respondeu em {c1 - c0:.1f}s, {len(msg)} caracteres")
        t_send = time.time()
        send_to_dsh(jar, a.session_id, msg)
        log(f"rodada {rnd}: mensagem aceita pelo dsh em {time.time() - t_send:.2f}s")
        reply, t_avail = wait_reply(jar, a.session_id, msg)
        if reply is None:
            log(f"rodada {rnd}: sem resposta do dsh em 180s, parando")
            break
        t_read = time.time()
        log(f"rodada {rnd}: dsh respondeu; leitura {t_read - t_avail:.2f}s depois da disponibilidade; {len(reply)} caracteres")
        if rnd == a.max_rounds:
            log("limite atingido: sem nova chamada ao Claude")
            break
        claude_in = reply
    log("fim")


if __name__ == "__main__":
    main()
