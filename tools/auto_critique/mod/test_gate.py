"""Testes das checagens C1 a C5 do gate e da camada de contexto. Sem API; arquivos só em pasta temporária."""
import json
import os
import tempfile
import unittest

from gate import (
    CAMPOS,
    c1_envelope,
    c2_brief,
    c3_alvo,
    c4_pedido,
    c5_criterio,
    checar,
    contexto,
    rodada_atual,
)

SHA = "a" * 64


def estado(**over):
    base = {
        "brief": {"path": "docs/ingest.md", "sha256": SHA},
        "orcamento_rodadas": 6,
        "sem_mudanca_limite": 2,
        "nos": [
            {"id": "N1", "ordem": 1, "aberto": False, "criterios": [{"id": "N1.c1"}]},
            {"id": "N2", "ordem": 2, "aberto": True, "criterios": [{"id": "N2.c1"}, {"id": "N2.c2"}]},
            {"id": "N3", "ordem": 3, "aberto": True, "criterios": [{"id": "N3.c1"}]},
        ],
    }
    base.update(over)
    return base


def mensagem(corpo="estado do entregável: alterado\ncriterio: N2.c1 cumprido: não\n", **campos):
    valores = {
        "brief": f"docs/ingest.md sha256:{SHA}",
        "alvo": "N2",
        "tipo": "critica",
        "criterio": "N2.c1",
        "pedido": "Você confirma o critério?",
        "material": "M1",
    }
    valores.update(campos)
    cabecalho = "\n".join(f"{c}: {valores[c]}" for c in CAMPOS)
    return f"<<<MSG\n{cabecalho}\n---\n{corpo}MSG>>>"


def pergunta(**campos):
    """Mensagem do tipo pergunta: sem critério por padrão, marcado com '-'."""
    campos.setdefault("criterio", "-")
    return mensagem(tipo="pergunta", **campos)


class C1Envelope(unittest.TestCase):
    def test_envelope_valido(self):
        env, erro = c1_envelope(mensagem())
        self.assertIsNone(erro)
        self.assertEqual(env.alvo, "N2")
        self.assertEqual(env.tipo, "critica")
        self.assertEqual(env.brief_sha, SHA)

    def test_sem_marcadores_recusa(self):
        sem = mensagem().replace("<<<MSG\n", "").replace("MSG>>>", "")
        v = c1_envelope(sem)[1]
        self.assertEqual((v.resultado, v.check), ("recusa", "C1"))
        self.assertIn("<<<MSG", v.motivo)

    def test_campo_faltando(self):
        texto = mensagem().replace("material: M1\n", "")
        self.assertEqual(c1_envelope(texto)[1].check, "C1")

    def test_tipo_faltando(self):
        texto = mensagem().replace("tipo: critica\n", "")
        self.assertIn("tipo", c1_envelope(texto)[1].motivo)

    def test_tipo_invalido(self):
        self.assertIn("tipo", c1_envelope(mensagem(tipo="sugestão"))[1].motivo)

    def test_campos_fora_da_ordem(self):
        texto = (
            "<<<MSG\n"
            "alvo: N2\n"
            f"brief: docs/ingest.md sha256:{SHA}\n"
            "tipo: critica\n"
            "criterio: N2.c1\n"
            "pedido: x\n"
            "material: M1\n"
            "---\nc\n"
            "MSG>>>"
        )
        self.assertIn("ordem", c1_envelope(texto)[1].motivo)

    def test_sem_separador(self):
        self.assertIn("---", c1_envelope("<<<MSG\nalvo: N2\nMSG>>>")[1].motivo)

    def test_brief_sem_sha(self):
        texto = mensagem(brief="docs/ingest.md")
        self.assertIn("sha256", c1_envelope(texto)[1].motivo)


class C2Brief(unittest.TestCase):
    def test_sha_igual_passa(self):
        env, _ = c1_envelope(mensagem())
        self.assertIsNone(c2_brief(env, SHA, estado()))

    def test_sha_do_arquivo_mudou_recusa(self):
        env, _ = c1_envelope(mensagem())
        v = c2_brief(env, "b" * 64, estado())
        self.assertEqual((v.resultado, v.check), ("recusa", "C2"))


class C3Alvo(unittest.TestCase):
    def test_primeiro_aberto_passa(self):
        env, _ = c1_envelope(mensagem(alvo="N2"))
        self.assertIsNone(c3_alvo(env, estado()))

    def test_segundo_aberto_estaciona(self):
        env, _ = c1_envelope(mensagem(alvo="N3", criterio="N3.c1"))
        v = c3_alvo(env, estado())
        self.assertEqual((v.resultado, v.check), ("estaciona", "C3"))

    def test_arvore_sem_nó_aberto_encerra(self):
        fechado = estado(nos=[{"id": "N1", "ordem": 1, "aberto": False, "criterios": []}])
        env, _ = c1_envelope(mensagem(alvo="N1"))
        self.assertEqual(c3_alvo(env, fechado).resultado, "encerra")


class C4Pedido(unittest.TestCase):
    def test_uma_pergunta_passa(self):
        env, _ = c1_envelope(mensagem(pedido="Você confirma?"))
        self.assertIsNone(c4_pedido(env))

    def test_duas_perguntas_recusa(self):
        env, _ = c1_envelope(mensagem(pedido="Confirma? Revisa?"))
        self.assertEqual(c4_pedido(env).check, "C4")

    def test_pedido_vazio_recusa(self):
        env, _ = c1_envelope(mensagem(pedido="  "))
        self.assertEqual(c4_pedido(env).check, "C4")


class C5Criterio(unittest.TestCase):
    def test_critica_com_criterio_do_alvo_passa(self):
        env, _ = c1_envelope(mensagem(criterio="N2.c2"))
        self.assertIsNone(c5_criterio(env, estado()))

    def test_critica_com_criterio_de_outro_nó_estaciona(self):
        env, _ = c1_envelope(mensagem(criterio="N3.c1"))
        self.assertEqual(c5_criterio(env, estado()).resultado, "estaciona")

    def test_critica_sem_criterio_estaciona(self):
        env, _ = c1_envelope(mensagem(criterio="-"))
        v = c5_criterio(env, estado())
        self.assertEqual((v.resultado, v.check), ("estaciona", "C5"))
        self.assertIn("sem critério", v.motivo)

    def test_pergunta_sem_criterio_passa(self):
        env, _ = c1_envelope(pergunta())
        self.assertIsNone(c5_criterio(env, estado()))

    def test_pergunta_com_criterio_recusa(self):
        env, _ = c1_envelope(pergunta(criterio="N2.c1"))
        v = c5_criterio(env, estado())
        self.assertEqual((v.resultado, v.check), ("recusa", "C5"))


class Checar(unittest.TestCase):
    def test_critica_valida_e_aceita(self):
        self.assertEqual(checar(mensagem(), estado(), SHA).resultado, "aceita")

    def test_pergunta_valida_e_aceita(self):
        self.assertEqual(checar(pergunta(), estado(), SHA).resultado, "aceita")

    def test_brief_errado_para_antes_das_outras_checagens(self):
        self.assertEqual(checar(mensagem(), estado(), "b" * 64).check, "C2")

    def test_ordem_de_execucao_c3_antes_de_c5(self):
        v = checar(mensagem(alvo="N3", criterio="N9.c9"), estado(), SHA)
        self.assertEqual(v.check, "C3")

    def test_sem_marcadores_recusa_em_c1(self):
        self.assertEqual(checar("texto solto", estado(), SHA).check, "C1")


class Rodada(unittest.TestCase):
    def test_conta_so_aceitas(self):
        historico = [
            {"resultado": "aceita"},
            {"resultado": "recusa"},
            {"resultado": "aceita"},
        ]
        self.assertEqual(rodada_atual(historico), 3)

    def test_primeira_rodada_e_a_um(self):
        self.assertEqual(rodada_atual([]), 1)


class Contexto(unittest.TestCase):
    def test_devolve_brief_sha_e_primeiro_aberto(self):
        with tempfile.TemporaryDirectory() as d:
            brief = os.path.join(d, "brief.md")
            with open(brief, "w", encoding="utf-8") as f:
                f.write("brief")
            caminho = os.path.join(d, "estado.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump({"brief": {"path": brief, "sha256": SHA}, "nos": [
                    {"id": "N1", "ordem": 1, "aberto": False, "criterios": []},
                    {"id": "N2", "ordem": 2, "aberto": True, "criterios": []}]}, f)
            out = contexto(caminho)
        self.assertEqual(out["alvo"], "N2")
        self.assertEqual(out["brief"], brief)
        self.assertEqual(len(out["sha256"]), 64)

    def test_sem_nó_aberto_devolve_traco(self):
        with tempfile.TemporaryDirectory() as d:
            brief = os.path.join(d, "brief.md")
            with open(brief, "w", encoding="utf-8") as f:
                f.write("brief")
            caminho = os.path.join(d, "estado.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump({"brief": {"path": brief, "sha256": SHA}, "nos": []}, f)
            self.assertEqual(contexto(caminho)["alvo"], "-")


if __name__ == "__main__":
    unittest.main()
