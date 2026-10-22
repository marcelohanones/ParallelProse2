"""Gate mecânico do modo CRITIQUE: checagens C1 a C5 como funções puras, mais a camada de I/O.

C6, C7 e C8 foram retiradas por enquanto: as regras delas ainda são suposição, e voltam
ao desenho depois de testes reais. Ver docs/proposta_gate_critique.md, seções 3 a 5.

Nada nas funções puras lê arquivo, roda processo ou chama API. A camada de I/O, no fim
do arquivo, é a única que toca nos arquivos da rodada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass

CAMPOS = ("brief", "alvo", "tipo", "criterio", "pedido", "material")
TIPOS = ("critica", "pergunta")
SEPARADOR = "---"
# Marcadores da mensagem entre harnesses: o conteúdo vem entre <<<MSG e MSG>>>.
MSG_RE = re.compile(r"<<<MSG\s*(.*?)\s*MSG>>>", re.DOTALL)


@dataclass(frozen=True)
class Veredito:
    """resultado: aceita | recusa | estaciona | encerra."""

    resultado: str
    check: str = ""
    motivo: str = ""


@dataclass(frozen=True)
class Envelope:
    brief_path: str
    brief_sha: str
    alvo: str
    tipo: str
    criterio: str
    pedido: str
    material: str
    corpo: str


def c1_envelope(texto: str) -> tuple[Envelope | None, Veredito | None]:
    """C1: marcadores <<<MSG ... MSG>>>, envelope completo na ordem da seção 3, e a linha --- antes do corpo."""
    m = MSG_RE.search(texto or "")
    if not m:
        return None, Veredito("recusa", "C1", "falta o bloco <<<MSG ... MSG>>>")
    linhas = m.group(1).split("\n")
    if SEPARADOR not in linhas:
        return None, Veredito("recusa", "C1", "falta a linha ---")
    i = linhas.index(SEPARADOR)
    campos: dict[str, str] = {}
    ordem: list[str] = []
    for linha in linhas[:i]:
        if not linha.strip():
            continue
        chave, dois_pontos, valor = linha.partition(":")
        chave = chave.strip()
        if not dois_pontos or chave not in CAMPOS:
            return None, Veredito("recusa", "C1", f"linha inválida: {linha!r}")
        campos[chave] = valor.strip()
        ordem.append(chave)
    faltando = [c for c in CAMPOS if c not in campos]
    if faltando:
        return None, Veredito("recusa", "C1", "campos faltando: " + ", ".join(faltando))
    if tuple(ordem) != CAMPOS:
        return None, Veredito("recusa", "C1", "campos fora da ordem")
    if campos["tipo"] not in TIPOS:
        return None, Veredito("recusa", "C1", "tipo deve ser 'critica' ou 'pergunta'")
    caminho, separador, sha = campos["brief"].rpartition(" sha256:")
    if not separador or not caminho:
        return None, Veredito("recusa", "C1", "brief sem caminho ou sha256")
    corpo = "\n".join(linhas[i + 1:])
    envelope = Envelope(
        brief_path=caminho,
        brief_sha=sha,
        alvo=campos["alvo"],
        tipo=campos["tipo"],
        criterio=campos["criterio"],
        pedido=campos["pedido"],
        material=campos["material"],
        corpo=corpo,
    )
    return envelope, None


def c2_brief(env: Envelope, sha_arquivo: str, estado: dict) -> Veredito | None:
    """C2: o brief do envelope é o do estado, e o sha256 bate com o arquivo em disco."""
    if estado["brief"]["path"] != env.brief_path:
        return Veredito("recusa", "C2", "caminho do brief diferente do estado")
    if env.brief_sha != sha_arquivo or estado["brief"]["sha256"] != sha_arquivo:
        return Veredito("recusa", "C2", "brief mudou: sha256 do arquivo não bate")
    return None


def c3_alvo(env: Envelope, estado: dict) -> Veredito | None:
    """C3: o alvo é o primeiro nó aberto, na ordem da árvore. Sem nó aberto, a rodada encerra."""
    abertos = [n for n in sorted(estado["nos"], key=lambda n: n["ordem"]) if n["aberto"]]
    if not abertos:
        return Veredito("encerra", "C3", "árvore sem nó aberto")
    if env.alvo != abertos[0]["id"]:
        return Veredito("estaciona", "C3", f"alvo {env.alvo} não é o primeiro aberto ({abertos[0]['id']})")
    return None


def c4_pedido(env: Envelope) -> Veredito | None:
    """C4: um único pedido. Aproximação mecânica: no máximo uma pergunta (um '?')."""
    if not env.pedido.strip():
        return Veredito("recusa", "C4", "pedido vazio")
    if env.pedido.count("?") > 1:
        return Veredito("recusa", "C4", "mais de uma pergunta no pedido")
    return None


def c5_criterio(env: Envelope, estado: dict) -> Veredito | None:
    """C5: crítica cita um critério existente no nó alvo; pergunta não cita critério ('-')."""
    if env.tipo == "pergunta":
        if env.criterio != "-":
            return Veredito("recusa", "C5", "pergunta não deve citar critério")
        return None
    if env.criterio == "-":
        return Veredito("estaciona", "C5", "crítica sem critério")
    no = next((n for n in estado["nos"] if n["id"] == env.alvo), None)
    ids = {c["id"] for c in no["criterios"]} if no else set()
    if env.criterio not in ids:
        return Veredito("estaciona", "C5", f"critério {env.criterio} não existe no nó {env.alvo}")
    return None


def checar(texto: str, estado: dict, sha_arquivo: str) -> Veredito:
    """Roda C1 a C5 na ordem da proposta. Devolve o primeiro veredito que não é aceita."""
    env, erro = c1_envelope(texto)
    if erro is not None:
        return erro
    for veredito in (
        c2_brief(env, sha_arquivo, estado),
        c3_alvo(env, estado),
        c4_pedido(env),
        c5_criterio(env, estado),
    ):
        if veredito is not None:
            return veredito
    return Veredito("aceita")


def rodada_atual(historico: list[dict]) -> int:
    """Número da próxima rodada: uma a mais que as mensagens aceitas. Recusas não contam."""
    return sum(1 for h in historico if h["resultado"] == "aceita") + 1


# --- Camada de I/O: lê a rodada dos arquivos, chama checar e registra o veredito. ---

REPO = "/Users/marcelohanones/Developer/personal/ParallelProse2"
ESTADO_PADRAO = f"{REPO}/tools/auto_critique/estado.json"
HISTORICO_PADRAO = f"{REPO}/docs/critique/rodadas.jsonl"
ESTACIONADOS_PADRAO = f"{REPO}/docs/critique/estacionados.jsonl"


def _ler_jsonl(caminho: str) -> list[dict]:
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def _anexar(caminho: str, registro: dict) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def _sha256(caminho: str) -> str:
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def contexto(estado_p: str) -> dict:
    """Dados da rodada que o mod passa aos harnesses a cada turno: brief, sha256 atual e alvo.

    O sha256 é o do arquivo em disco, o mesmo que o C2 confere. O alvo é o primeiro nó aberto.
    """
    with open(estado_p, encoding="utf-8") as f:
        estado = json.load(f)
    abertos = [n for n in sorted(estado["nos"], key=lambda n: n["ordem"]) if n["aberto"]]
    return {
        "ok": True,
        "brief": estado["brief"]["path"],
        "sha256": _sha256(os.path.join(REPO, estado["brief"]["path"])),
        "alvo": abertos[0]["id"] if abertos else "-",
    }


def verificar(arquivo: str, direcao: str, estado_p: str, historico_p: str, estacionados_p: str) -> tuple[Veredito, int]:
    """Lê a rodada dos arquivos, roda C1 a C5 e registra o veredito.

    Sem estado.json, recusa (fail-closed): o gate não decide sem a árvore.
    """
    if not os.path.exists(estado_p):
        return Veredito("recusa", "GATE", "estado da rodada ausente: tools/auto_critique/estado.json"), 0
    with open(estado_p, encoding="utf-8") as f:
        estado = json.load(f)
    historico = _ler_jsonl(historico_p)
    with open(arquivo, encoding="utf-8") as f:
        texto = f.read()
    sha = _sha256(os.path.join(REPO, estado["brief"]["path"]))
    veredito = checar(texto, estado, sha)
    rodada = rodada_atual(historico)
    _anexar(historico_p, {
        "rodada": rodada,
        "direcao": direcao,
        "resultado": veredito.resultado,
        "check": veredito.check,
        "motivo": veredito.motivo,
    })
    if veredito.resultado == "estaciona":
        _anexar(estacionados_p, {"rodada": rodada, "origem": direcao, "check": veredito.check, "motivo": veredito.motivo})
    return veredito, rodada


def main(argv: list[str]) -> int:
    """CLI: `gate.py check <arquivo>` e `gate.py contexto`. Imprime JSON; check só devolve 0 para aceita."""
    ap = argparse.ArgumentParser(prog="gate.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("arquivo")
    c.add_argument("--direcao", default="claude-para-dsh", choices=["claude-para-dsh", "dsh-para-claude"])
    c.add_argument("--estado", default=ESTADO_PADRAO)
    c.add_argument("--historico", default=HISTORICO_PADRAO)
    c.add_argument("--estacionados", default=ESTACIONADOS_PADRAO)
    x = sub.add_parser("contexto")
    x.add_argument("--estado", default=ESTADO_PADRAO)
    args = ap.parse_args(argv)
    if args.cmd == "contexto":
        try:
            print(json.dumps(contexto(args.estado), ensure_ascii=False))
        except Exception as e:  # noqa: BLE001 - o mod trata ok=false, sem derrubar o laço
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 0
    try:
        veredito, rodada = verificar(args.arquivo, args.direcao, args.estado, args.historico, args.estacionados)
    except Exception as e:  # noqa: BLE001 - fail-closed: qualquer erro de leitura recusa
        veredito, rodada = Veredito("recusa", "GATE", f"erro no gate: {e}"), 0
    print(json.dumps({
        "resultado": veredito.resultado,
        "check": veredito.check,
        "motivo": veredito.motivo,
        "rodada": rodada,
    }, ensure_ascii=False))
    return 0 if veredito.resultado == "aceita" else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
