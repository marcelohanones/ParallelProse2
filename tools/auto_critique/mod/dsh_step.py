#!/usr/bin/env python3
"""Ponte do mod auto_critique até o dsh. Usa dsh_api.py, na mesma pasta.

O id do chat não é guardado aqui: o mod o recebe do estado da sessão e o passa a cada chamada.

Comandos:
  send <arquivo> <chat>   envia o texto do arquivo ao chat indicado (session/prompt)
  read <chat>             uma consulta: devolve a resposta do dsh à última mensagem enviada, ou null
  log <texto>             acrescenta uma linha ao log do laço
  chats [filtro]          lista as sessões do dsh com id e título, opcionalmente filtradas pelo título
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsh_api as a  # noqa: E402

WORK = "/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime"
TOKEN = f"{WORK}/dsh_token.txt"
JAR = f"{WORK}/jar.txt"
LAST = f"{WORK}/app_last_sent.txt"
LOG = f"{WORK}/laco_mod.log"


def log(msg):
    os.makedirs(WORK, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def main():
    cmd = sys.argv[1]
    if cmd == "log":
        log(" ".join(sys.argv[2:]))
        print(json.dumps({"ok": True}))
        return
    a.auth(TOKEN, JAR)
    if cmd == "chats":
        flt = (sys.argv[2] if len(sys.argv) > 2 else "").lower()
        items = a.rpc(JAR, "session/list", {"_request": {}})["items"]
        lines = []
        for s in items:
            title = (s.get("projections", {}).get("values", {}) or {}).get("title") or "(sem título)"
            if flt and flt not in title.lower():
                continue
            lines.append(f"{s['sessionId']}  {title}")
        print("\n".join(lines[:30]) or "nenhum chat encontrado")
        return
    if cmd == "send":
        text = open(sys.argv[2], encoding="utf-8").read()
        chat = sys.argv[3] if len(sys.argv) > 3 else ""
        if not chat:
            print(json.dumps({"ok": False, "error": "chat não informado"}))
            return
        try:
            a.send_to_dsh(JAR, chat, text)
            with open(LAST, "w", encoding="utf-8") as f:
                f.write(text)
            log(f"enviado ao dsh ({len(text)} caracteres)")
            print(json.dumps({"ok": True}))
        except Exception as e:  # noqa: BLE001
            log(f"falha no envio: {e}")
            print(json.dumps({"ok": False, "error": str(e)}))
        return
    if cmd == "read":
        chat = sys.argv[2] if len(sys.argv) > 2 else ""
        sent = open(LAST, encoding="utf-8").read()
        needle = json.dumps(sent, ensure_ascii=False)[1:-1]
        eventos = [r["event"] for r in a.history(JAR, chat)]
        idx = None
        for i, e in enumerate(eventos):
            if e.get("type") == "user/message" and needle in json.dumps(e, ensure_ascii=False):
                idx = i
        reply = None
        if idx is not None:
            # A resposta final é a última mensagem de texto do turno, e só existe depois do turn/end.
            fim = next((j for j in range(idx + 1, len(eventos)) if eventos[j].get("type") == "turn/end"), None)
            if fim is not None:
                textos = [a.event_text(eventos[j]) for j in range(idx + 1, fim) if eventos[j].get("type") == "assistant/message"]
                textos = [t for t in textos if t]
                reply = textos[-1] if textos else None
        print(json.dumps({"reply": reply}))
        return
    print(json.dumps({"error": f"comando desconhecido: {cmd}"}))


if __name__ == "__main__":
    main()
