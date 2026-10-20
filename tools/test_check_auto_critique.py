#!/usr/bin/env python3
"""Tests for tools/check_auto_critique.py.

Each case builds a round file in a temporary directory and asserts what the
checker reports. The module's REVIEWS root is pointed at the temporary
directory so that a cited file resolves there. Run with:
    python3 tools/test_check_auto_critique.py
"""
from __future__ import annotations

import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_auto_critique as chk  # noqa: E402

FENCE = chk.BT * 3
TARGET = "R1-dsh.md"  # round below the checador key vigencia, so it needs no key


def build(path, *, gate=True, to_markim="none", blocks="no", why=None, why_blocking=None,
          footers=1, before_gate=(), after_footer=(), sent_override=None,
          checador=None, opening="_auto"):
    """Write a round file; return its canonical word count."""
    body = ["<!-- sent: 0000 palavras (LC_ALL=C wc -w neste arquivo) -->"]
    if checador is not None:
        body.append("checador: " + checador)
    if opening == "_auto":
        opening = "Segue a mensagem `" + (checador or TARGET).split()[0] + "`." if checador else None
    body.append("")
    if opening:
        body += [opening, ""]
    body += ["# Teste", "", "corpo com algumas palavras aqui.", ""]
    body += list(before_gate)
    if gate:
        body += [FENCE + "critique-gate", "round: R99", "from: cc",
                 "to-markim: " + to_markim, "blocks-advance: " + blocks]
        if why_blocking is not None:
            body.append("why-blocking: " + why_blocking)
        if why is not None:
            body.append("why-not-blocking: " + why)
        body += [FENCE, ""]
    for _ in range(footers):
        body += ["## Contagens", "- ok", ""]
    body += list(after_footer)
    text = chr(10).join(body) + chr(10)
    path.write_text(text, encoding="utf-8")
    actual = chk.word_count(path)
    replaced = text.replace("0000", str(actual if sent_override is None else sent_override))
    path.write_text(replaced, encoding="utf-8")
    return actual


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        self.orig_reviews = chk.REVIEWS
        chk.REVIEWS = self.dir

    def tearDown(self):
        chk.REVIEWS = self.orig_reviews
        self.tmp.cleanup()

    def rules(self, path):
        return {rule for rule, _ in chk.analyze(path)}

    def target(self, **kwargs):
        """A clean file below the key vigencia, so it reports zero findings."""
        p = self.dir / TARGET
        build(p, **kwargs)
        return p

    def subject(self, **kwargs):
        p = self.dir / "R90-cc.md"
        build(p, checador=TARGET + " \u2014 0 achado(s)", **kwargs)
        return p

    def test_valid_file_has_no_findings(self):
        self.target()
        self.assertEqual(chk.analyze(self.subject()), [])

    def test_section_before_gate_is_not_a_violation(self):
        self.target()
        p = self.subject(before_gate=["## Linha de disparo", "texto antes do gate"])
        self.assertEqual(chk.analyze(p), [])

    def test_section_after_footer_is_caught(self):
        self.target()
        p = self.subject(after_footer=["## Linha de disparo", "texto"])
        self.assertIn("gate-last", self.rules(p))

    def test_missing_gate_still_checks_sent(self):
        self.target()
        p = self.subject(gate=False, sent_override=999)
        found = self.rules(p)
        self.assertIn("gate-last", found)
        self.assertIn("sent", found, "arquivo truncado sem gate precisa ter a contagem cobrada")

    def test_two_footers(self):
        self.target()
        p = self.subject(footers=2)
        self.assertIn("single-footer", self.rules(p))

    def test_no_why_when_to_markim_is_not_none(self):
        self.target()
        p = self.subject(to_markim="C1", blocks="no", why=None)
        self.assertIn("gate-coherence", self.rules(p))

    def test_why_not_required_when_to_markim_is_none(self):
        self.target()
        p = self.subject(to_markim="none", blocks="no")
        self.assertNotIn("gate-coherence", self.rules(p))

    def test_wrong_sent_is_caught(self):
        self.target()
        p = self.dir / "R90-cc.md"
        actual = build(p, sent_override=1, checador=TARGET + " \u2014 0 achado(s)")
        self.assertIn("sent", self.rules(p))
        self.assertEqual(chk.word_count(p), actual)

    def test_checador_key_correct(self):
        self.target()
        p = self.subject()
        self.assertNotIn("checador", self.rules(p))

    def test_checador_key_wrong_number_is_caught(self):
        self.target()
        p = self.dir / "R90-cc.md"
        build(p, checador=TARGET + " \u2014 5 achado(s)")
        self.assertIn("checador", self.rules(p))

    def test_checador_key_missing_is_caught(self):
        self.target()
        p = self.dir / "R90-cc.md"
        build(p)
        self.assertIn("checador", self.rules(p))

    def test_opening_target_mismatch_is_caught(self):
        self.target()
        p = self.dir / "R90-cc.md"
        build(p, checador=TARGET + " \u2014 0 achado(s)",
              opening="Segue a mensagem `R41-cc.md`.")
        self.assertIn("opening", self.rules(p))

    def test_opening_with_several_targets_passes(self):
        self.target()
        p = self.dir / "R90-cc.md"
        build(p, checador=TARGET + " \u2014 0 achado(s)",
              opening="Segue as mensagens `R41-cc.md` e `" + TARGET + "`.")
        self.assertNotIn("opening", self.rules(p))

    def test_opening_missing_is_caught(self):
        self.target()
        p = self.dir / "R90-cc.md"
        build(p, checador=TARGET + " \u2014 0 achado(s)", opening=None)
        self.assertIn("opening", self.rules(p))

    def test_target_is_clean_at_depth_zero(self):
        # O alvo citado so era analisado em profundidade 1, onde a chave e a
        # abertura sao puladas. Este teste prende o alvo ao nome que o
        # comentario de TARGET diz: abaixo da vigencia da chave, limpo.
        self.assertEqual(chk.analyze(self.target()), [])

    def test_checador_key_absent_in_the_first_round(self):
        # A primeira mensagem de uma serie nao responde arquivo nenhum,
        # e por isso nao tem o que citar na chave.
        p = self.dir / "R1-cc.md"
        build(p)
        self.assertNotIn("checador", self.rules(p))

    def test_yes_without_label_is_incoherent(self):
        self.target()
        p = self.subject(to_markim="none", blocks="yes")
        self.assertIn("gate-coherence", self.rules(p))

    def test_yes_with_label_and_reason_is_coherent(self):
        self.target()
        p = self.subject(to_markim="M1", blocks="yes",
                         why_blocking="sem default: o conjunto nao roda o criterio")
        self.assertNotIn("gate-coherence", self.rules(p))

    def test_yes_without_why_blocking_is_caught(self):
        # Bloquear custa uma justificativa: por que a escolha nao tem default
        # e por que a observacao nao a corrige.
        self.target()
        p = self.subject(to_markim="M1", blocks="yes")
        self.assertIn("gate-coherence", self.rules(p))

    def test_hyphenated_addendum_is_a_round_file(self):
        self.assertIsNotNone(chk.FILE_RE.match("R1-dsh-log-de-execucao.md"),
                             "adendo com hifen precisa casar FILE_RE")
        p = self.dir / "R90-dsh-log-de-execucao.md"
        build(p)  # round 90, sem chave
        self.assertIn("checador", self.rules(p))

    def test_opening_must_come_before_the_title(self):
        self.target()
        p = self.subject(opening=None,
                         before_gate=["Segue a mensagem `" + TARGET + "`."])
        self.assertIn("opening", self.rules(p))

    def test_header_keys_read_the_first_block(self):
        p = self.dir / "R1-cc.md"
        p.write_text(
            "<!-- sent: 1 palavras (x) -->" + chr(10) +
            "gap: R1" + chr(10) +
            "checador: R1-cc.md \u2014 0 achado(s)" + chr(10) +
            chr(10) + "texto depois" + chr(10),
            encoding="utf-8")
        self.assertEqual(chk.header_keys(p), {"gap": "R1", "checador": "R1-cc.md \u2014 0 achado(s)"})

    def test_gate_keys_read_the_block(self):
        self.target()
        p = self.subject(to_markim="M1", blocks="no", why="respondidas")
        keys = chk.gate_keys(p)
        self.assertEqual(keys.get("to-markim"), "M1")
        self.assertEqual(keys.get("blocks-advance"), "no")

    def test_exceptions_block_is_read(self):
        contract = self.dir / "contract.md"
        contract.write_text(chr(10).join([
            "texto antes",
            "critique-exceptions",
            "R90-cc.md | sent | divergencia conhecida",
            "R90-cc.md | single-footer | outra",
            "critique-exceptions-end",
            "texto depois",
        ]), encoding="utf-8")
        loaded = chk.load_exceptions(contract)
        self.assertEqual(loaded["R90-cc.md"], {"sent", "single-footer"})

    def test_vigencia_numbers_match_the_contract(self):
        """Os numeros de rodada do codigo sao os que o contrato nomeia."""
        form, key = chk.contract_vigencia()
        self.assertEqual(form, chk.FIRST_ENFORCED_ROUND)
        self.assertEqual(key, chk.FIRST_CHECKER_KEY_ROUND)

    def test_word_count_forces_the_c_locale(self):
        """A funcao fixa LC_ALL=C em vez de herdar o ambiente de quem roda.

        Este teste existe porque o fixture abaixo depende de uma politica do
        Python: por padrao ele forca LC_CTYPE=UTF-8 nos filhos (PEP 538), e com
        isso o fixture pega a regressao ate em maquina sem locale instalado.
        Mas PYTHONCOERCECLOCALE=0 desliga essa coercao, os filhos herdam C, e o
        fixture passa verde sobre o defeito. Este mock nao depende disso.
        """
        p = self.dir / "R90-cc.md"
        p.write_text("x" + chr(10), encoding="utf-8")
        with mock.patch.object(chk.subprocess, "run") as run:
            run.return_value = mock.Mock(stdout="1 /dev/null" + chr(10))
            chk.word_count(p)
        env = run.call_args.kwargs.get("env") or run.call_args[1].get("env")
        self.assertEqual(env.get("LC_ALL"), "C", "word_count precisa passar LC_ALL=C ao wc")

    def test_word_count_uses_the_c_locale(self):
        """Fixture com "as" acentuado: o C conta um token, o UTF-8 conta dois.

        Pega a regressao no uso real, e pega em qualquer maquina por padrao,
        porque o Python coage LC_CTYPE=UTF-8 para os filhos. Ver o teste acima
        para o caso em que essa coercao esta desligada.
        """
        p = self.dir / "R90-cc.md"
        p.write_text("x " + chr(224) + "s y" + chr(10), encoding="utf-8")
        self.assertEqual(chk.word_count(p), 3)

    def test_contract_lists_every_rule(self):
        """O contrato e o codigo precisam listar as mesmas regras, na mesma ordem."""
        self.assertEqual(chk.contract_rule_ids(), list(chk.RULES))

    def test_every_rule_appears_in_the_code(self):
        import inspect
        src = inspect.getsource(chk)
        for rule in chk.RULES:
            self.assertIn(chr(34) + rule + chr(34), src, "regra %s nao aparece no codigo" % rule)

    def test_classify_exception_is_not_failure(self):
        label, reported = chk.classify(39, [("sent", "x")], {"sent"})
        self.assertEqual(label, "excecao")
        self.assertEqual(reported, [("sent", "x")])

    def test_classify_unlisted_is_failure(self):
        label, _ = chk.classify(39, [("sent", "x")], set())
        self.assertEqual(label, "FALHA")

    def test_classify_round_zero_is_history(self):
        # Rodada 0 e o nome fora do padrao: nao casa FILE_RE, e o checador
        # nao tem como situa-la na serie. Vai para historico, nao para falha.
        label, reported = chk.classify(0, [("sent", "x")], set())
        self.assertEqual(label, "historico")
        self.assertEqual(reported, [("sent", "x")])


class ContractStepFourCommand(unittest.TestCase):
    """T15: o comando do passo 4 troca o número no cabeçalho e no rodapé, sem tocar no corpo.

    O comando é lido do contrato, e não copiado: se o contrato mudar, o teste acompanha.
    """

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    V20 = "sed -i '' 's/0000/{n}/g' docs/reviews/R{n}-{lado}.md"
    HEADER = "<!-- sent: 0000 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->"
    FOOTER = "- **sent**: 0000 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído)."
    BODY_MARKER = "O passo 4 troca `0000` pelo número, e este corpo não muda."
    BODY_PROSE = "sent: 0000 palavras aparece aqui como prosa, numa linha que não é cabeçalho."

    def contract_command(self):
        text = (self.ROOT / "docs" / "auto_critique2.md").read_text(encoding="utf-8")
        step = next(line for line in text.splitlines() if "**Cabeçalho.**" in line)
        return re.search(r"Executa: `(sed [^`]+)`", step).group(1)

    def run_step_four(self, template, token):
        # token: o nome do placeholder do contador no comando, lido do próprio comando
        body = "\n".join(["# R9 — exemplo", "", self.BODY_MARKER, "", self.BODY_PROSE, ""])
        text = self.HEADER + "\n" + body + "\n## Contagens\n\n" + self.FOOTER + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "R9-cc.md"
            path.write_text(text, encoding="utf-8")
            cmd = template.replace("docs/reviews/R{n}-{lado}.md", str(path))
            cmd = cmd.replace("{%s}" % token, "1234")
            subprocess.run(shlex.split(cmd), check=True, capture_output=True)
            return path.read_text(encoding="utf-8").splitlines()

    def run_contract_command(self):
        command = self.contract_command()
        token = re.search(r"\\1 \{(\w+)\}", command).group(1)
        return self.run_step_four(command, token)

    def test_header_and_footer_get_the_count(self):
        lines = self.run_contract_command()
        self.assertEqual(lines[0], self.HEADER.replace("0000", "1234"))
        self.assertIn("- **sent**: 1234 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).", lines)

    def test_marker_in_backticks_survives(self):
        lines = self.run_contract_command()
        self.assertIn(self.BODY_MARKER, lines)

    def test_key_quoted_in_prose_survives(self):
        lines = self.run_contract_command()
        self.assertIn(self.BODY_PROSE, lines)

    def test_control_v20_command_does_touch_the_body(self):
        # controle: a v20 troca o marcador em qualquer lugar; se ela não tocasse o corpo,
        # o fixture não estaria provando nada
        lines = self.run_step_four(self.V20, "n")
        self.assertNotIn(self.BODY_MARKER, lines)


if __name__ == "__main__":
    unittest.main(verbosity=2)
