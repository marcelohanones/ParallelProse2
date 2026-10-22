"""API local do dsh usada pelo mod auto_critique: autenticação, RPC, histórico e envio.

Extraído do api_loop.py, que era o laço independente. Só o que o mod usa ficou aqui.
"""
import json
import subprocess
import uuid

DSH = "http://127.0.0.1:3080"


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


def history(jar, sid, max_messages=200):
    """Últimos eventos do chat. A janela precisa cobrir o turno inteiro do dsh: com janela
    pequena, a mensagem enviada sai dela quando o dsh faz vários passos e a leitura falha."""
    items = rpc(jar, "session/list", {"_request": {}})["items"]
    seq = next(s for s in items if s["sessionId"] == sid)["projections"]["asOfSeq"]
    value = rpc(jar, "session/page", {"request": {
        "address": {"kind": "session", "sessionId": sid},
        "throughSeq": seq, "maxMessages": max_messages,
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
