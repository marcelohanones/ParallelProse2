#!/usr/bin/env python3
"""Tests for tools/watcher_auto_critique.py.

Each case builds a registry in a temporary directory and asserts what the
watcher decides; the dsh is a fake that records its argv, so no test calls an
API. Run with:
    python3 tools/test_watcher_auto_critique.py
"""
from __future__ import annotations

import json
import os
import pathlib
import copy
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_auto_critique as chk  # noqa: E402
import watcher_auto_critique as w  # noqa: E402

FAKE = """#!/usr/bin/env python3
import json, os, re, sys, time
with open(os.environ["%s"], "w") as handle:
    json.dump(sys.argv[1:], handle)
if os.environ.get("FAKE_SLEEP"):
    time.sleep(float(os.environ["FAKE_SLEEP"]))
line = " ".join(sys.argv[1:])
found = re.search(r"responda em (?:docs/reviews/)?(R[0-9]+-[a-z]+\\.md)", line)
if found and os.environ.get("FAKE_REVIEWS") and not os.environ.get("FAKE_SILENT") and os.environ.get("FAKE_EXIT", "0") == "0":
    # o salto de verdade grava a resposta: o dsh falso faz o mesmo, numa rodada bem formada
    cited = re.search(r"leia (?:docs/reviews/)?(R[0-9]+-[a-z]+\\.md)", line)
    prev = cited.group(1) if cited else ""
    checker = ("checador: " + prev + " — 0 achado(s)\\n\\nSegue a mensagem " + prev + "\\n\\n") if prev else ""
    body = ("<!-- sent: 0000 palavras (x) -->\\n" + checker
            + "```critique-gate\\nround: R9\\nfrom: dsh\\nto-markim: none\\nblocks-advance: no\\n```\\n")
    with open(os.path.join(os.environ["FAKE_REVIEWS"], found.group(1)), "w") as handle:
        handle.write(body.replace("0000", str(len(body.split()))))
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


def make_round(reviews, name, *, cites=None, to_markim="none", blocks="no", why=None,
               why_blocking=None, gap=None, sent_ok=True):
    """A well-formed round file, except where a case asks it not to be."""
    path = pathlib.Path(reviews) / name
    round_no, side = name.split("-")[0], name.split("-")[1].split(".")[0]
    lines = ["<!-- sent: 0000 palavras (x) -->"]
    if gap:
        lines.append("gap: " + gap)
    if cites:
        lines.append("checador: %s \u2014 0 achado(s)" % cites)
        lines.append("Segue a mensagem `%s`." % cites)
    lines += ["", "# T", "", "corpo com algumas palavras.", ""]
    lines += ["```critique-gate", "round: " + round_no, "from: " + side,
              "to-markim: " + to_markim, "blocks-advance: " + blocks]
    if why_blocking:
        lines.append("why-blocking: " + why_blocking)
    if why:
        lines.append("why-not-blocking: " + why)
    lines += ["```", "", "## Contagens", "", "- **sent**: 0000 palavras"]
    text = chr(10).join(lines) + chr(10)
    path.write_text(text, encoding="utf-8")
    count = chk.word_count(path)
    path.write_text(text.replace("0000", str(count if sent_ok else count + 1)), encoding="utf-8")
    return path


class WatcherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.reviews = self.root / "reviews"
        self.reviews.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.log = self.root / "argv.json"
        self.log_cc = self.root / "argv-cc.json"
        self.state_path = self.root / "state.json"
        self.fake = self.root / "dsh"
        self.fake.write_text(FAKE % "FAKE_LOG", encoding="utf-8")
        self.fake.chmod(0o755)
        self.fake_cc = self.root / "claude"
        self.fake_cc.write_text(FAKE % "FAKE_CC_LOG", encoding="utf-8")
        self.fake_cc.chmod(0o755)
        self.env = mock.patch.dict(os.environ, {
            "HOME": str(self.home),
            "DSH_HOME": str(self.home / ".dsh"),
            "FAKE_LOG": str(self.log),
            "FAKE_CC_LOG": str(self.log_cc),
            "FAKE_REVIEWS": str(self.reviews),
        })
        self.env.start()
        os.environ.pop("FAKE_EXIT", None)
        os.environ.pop("FAKE_SILENT", None)
        os.environ.pop("FAKE_SLEEP", None)
        self.orig_reviews = chk.REVIEWS
        self.state = w.new_state()

    def tearDown(self):
        chk.REVIEWS = self.orig_reviews
        self.env.stop()
        self.tmp.cleanup()

    # -- helpers ---------------------------------------------------------

    def run_pass(self, **kwargs):
        kwargs.setdefault("dsh_bin", str(self.fake))
        kwargs.setdefault("timeout", 30)  # sob carga, cinco segundos estouravam o dsh falso
        return w.run_pass(self.reviews, self.state, **kwargs)

    def baseline(self):
        make_round(self.reviews, "R1-cc.md")
        make_round(self.reviews, "R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "baseline")
        return result

    def argv(self):
        self.assertTrue(self.log.exists(), "o dsh falso nao foi chamado")
        return json.loads(self.log.read_text())

    # -- passo 1: reconciliar -------------------------------------------

    def test_first_run_is_a_baseline_and_dispatches_nothing(self):
        result = self.baseline()
        self.assertFalse(self.log.exists())
        self.assertEqual(set(self.state["seen"]), {"R1-cc.md", "R1-dsh.md"})
        self.assertEqual(self.state["chain"]["count"], 0)

    def test_new_turn_file_dispatches_the_other_side(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertEqual(self.argv(), ["--profile", "headless", "--json",
                         "rodada aberta:  leia R2-cc.md e responda em R2-dsh.md"
                         + w.procedure_note("dsh")])
        self.assertEqual(self.state["chain"]["count"], 1)

    def test_complete_pair_dispatches_the_next_round(self):
        self.baseline()
        self.state["cc_argv"] = [str(self.fake_cc)]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        sent = json.loads(self.log_cc.read_text())
        self.assertEqual(sent, ["par completo:   leia docs/reviews/R2-dsh.md e responda em docs/reviews/R3-cc.md"
                                + w.procedure_note("cc")])

    def test_addendum_never_triggers(self):
        self.baseline()
        make_round(self.reviews, "R1-dsh-nota.md")
        result = self.run_pass()
        # marca e avisa (item 7), mas não dispara: o aviso é o que o antigo "idle" escondia
        self.assertEqual(result["action"], "notice")
        self.assertFalse(self.log.exists())

    def test_rewrite_is_not_a_new_message(self):
        self.baseline()
        path = self.reviews / "R1-cc.md"
        path.write_text(path.read_text(encoding="utf-8") + chr(10) + "riscado" + chr(10), encoding="utf-8")
        result = self.run_pass()
        self.assertEqual(result["action"], "notice")
        self.assertFalse(self.log.exists())
        self.assertTrue(any("reescrito" in n for n in result["notices"]))

    def test_more_than_one_new_file_is_ambiguous(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        make_round(self.reviews, "R3-cc.md", cites="R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "ambiguous")
        self.assertFalse(self.log.exists())

    def test_complete_pair_arriving_together_collapses_on_the_citation(self):
        # T2 (item 6): o par chega junto; o último escritor é o que cita o outro, e dispara uma vez
        self.state["initialized"] = True
        self.state["cc_argv"] = [str(self.fake_cc)]
        make_round(self.reviews, "R1-cc.md")
        make_round(self.reviews, "R1-dsh.md", cites="R1-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertFalse(self.log.exists(), "o dsh não foi chamado: o par responde pelo primeiro, o cc")
        self.assertIn("responda em docs/reviews/R2-cc.md", self.log_cc.read_text())
        self.assertEqual(set(self.state["seen"]), {"R1-cc.md", "R1-dsh.md"}, "o par inteiro fica visto")
        self.assertEqual(self.state["chain"]["count"], 1)

    def test_pair_without_citation_is_ambiguous_and_dispatches_nothing(self):
        # T2: sem citação, o watcher não escolhe o último
        self.state["initialized"] = True
        make_round(self.reviews, "R1-cc.md")
        make_round(self.reviews, "R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "ambiguous")
        self.assertFalse(self.log.exists())
        self.assertFalse(self.log_cc.exists())

    def test_addendum_alone_is_marked_and_noticed_never_dispatched(self):
        # T11 (item 7): adendo sozinho não é turno, mas é marcado e avisado; nada dispara
        self.baseline()
        make_round(self.reviews, "R1-cc-assunto.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "notice")
        self.assertFalse(self.log.exists(), "o adendo não disparou")
        self.assertIn("R1-cc-assunto.md", self.state["seen"])
        self.assertTrue(any("R1-cc-assunto.md" in n for n in result["notices"]))
        again = self.run_pass()
        self.assertEqual(again["action"], "idle", "o adendo não repete o aviso")

    def test_failed_hop_is_recorded_named_and_not_retried(self):
        # T4 (item 8): saída diferente de zero: uma invocação, registro com rodada e alvo, sem repetição
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        os.environ["FAKE_EXIT"] = "3"
        hops = self.root / "hops"
        result = self.run_pass(hop_logs=hops)
        self.assertEqual(result["action"], "failed")
        self.assertEqual(self.state["chain"]["count"], 0)
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["status"], "falha-de-salto")
        self.assertEqual(entries[0]["target"], "R2-dsh.md")
        self.assertEqual(entries[0]["trigger"], "R2-cc.md")
        self.assertTrue(any("R2-dsh.md" in n and "R2-cc.md" in n for n in result["notices"]))
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 1, "uma invocação")
        self.run_pass(hop_logs=hops)
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 1, "a passada seguinte não repete o salto")

    def test_timed_out_hop_is_recorded_and_not_retried(self):
        # T5 (item 8): timeout conta como falha de salto, e não é repetido
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        os.environ["FAKE_SLEEP"] = "5"
        hops = self.root / "hops"
        result = self.run_pass(hop_logs=hops, timeout=1)
        self.assertEqual(result["action"], "failed")
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(entries[-1]["status"], "falha-de-salto")
        self.assertIn("timeout", entries[-1]["reason"])
        self.run_pass(hop_logs=hops, timeout=1)
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 1, "sem nova tentativa")

    def test_hop_that_exits_zero_without_an_answer_is_recorded(self):
        # T6 (item 8): saída zero sem a resposta no registro é sem-resposta; o salto rodou, então conta
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        os.environ["FAKE_SILENT"] = "1"
        hops = self.root / "hops"
        result = self.run_pass(hop_logs=hops)
        self.assertEqual(result["action"], "no-answer")
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(entries[-1]["status"], "sem-resposta")
        self.assertEqual(entries[-1]["target"], "R2-dsh.md")
        self.assertEqual(self.state["chain"]["count"], 1)
        self.run_pass(hop_logs=hops)
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 1, "sem nova tentativa")

    def test_status_reads_the_failure_index(self):
        # o --status mostra as falhas gravadas no índice, com rodada e alvo
        hops = self.root / "hops"
        hops.mkdir()
        (hops / "index.jsonl").write_text(json.dumps({"round": 2, "target": "R2-dsh.md",
            "trigger": "R2-cc.md", "status": "falha-de-salto", "reason": "saiu com 3"}) + "\n", encoding="utf-8")
        w.save_state(self.state_path, self.state)
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            code = w.main(["--state", str(self.state_path), "--status", "--hop-logs", str(hops)])
        self.assertEqual(code, 0)
        self.assertTrue(any("R2-dsh.md" in line and "falha-de-salto" in line for line in out))

    def test_registry_is_scanned_in_round_order_not_name_order(self):
        # T12: R2 vem antes de R10, pelo número da rodada e não pelo texto do nome
        make_round(self.reviews, "R10-cc.md")
        make_round(self.reviews, "R2-cc.md")
        self.assertEqual([e["name"] for e in w.scan(self.reviews)], ["R2-cc.md", "R10-cc.md"])

    def test_out_of_order_is_refused(self):
        os.environ.pop("FAKE_REVIEWS", None)  # o dsh falso não grava: o caso é a ordem
        self.baseline()
        make_round(self.reviews, "R3-cc.md", cites="R1-dsh.md")
        self.run_pass()  # R3 e unico novo: dispara
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertEqual(result["reason"], "fora de ordem")

    # -- passo 2 e 3: checar e decidir ----------------------------------

    def test_checker_failure_refuses_the_hop(self):
        self.baseline()
        path = make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", sent_ok=False)
        before = path.read_text(encoding="utf-8")
        result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertEqual(result["reason"], "FALHA")
        self.assertFalse(self.log.exists())
        self.assertEqual(path.read_text(encoding="utf-8"), before, "a mensagem fica intacta")

    def test_gate_with_question_holds(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", to_markim="M1", blocks="yes",
                   why_blocking="sem default: o conjunto de permissoes nao roda o criterio")
        result = self.run_pass()
        self.assertEqual(result["action"], "hold")
        self.assertEqual(result["reason"], "blocks-advance")
        self.assertFalse(self.log.exists())

    def test_answered_gate_dispatches(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", to_markim="M1",
                   blocks="no", why="respondidas no passa")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")

    def test_gap_closes_the_turn_and_resets_the_counter(self):
        self.baseline()
        self.state["chain"]["count"] = 1
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", gap="R2")
        result = self.run_pass()
        self.assertEqual(result["action"], "hold")
        self.assertEqual(result["reason"], "gap")
        self.assertEqual(self.state["chain"]["count"], 0)
        self.assertFalse(self.log.exists())

    def test_analyze_is_called_on_the_trigger_only(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        seen, real = [], chk.analyze

        def spy(path, _depth=0):
            if _depth == 0:
                seen.append(pathlib.Path(path).name)
            return real(path, _depth)

        with mock.patch.object(chk, "analyze", spy):
            self.run_pass()
        self.assertEqual(seen, ["R2-cc.md"])

    # -- passo 4: disparar ----------------------------------------------

    def test_nonzero_exit_is_not_a_hop(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        os.environ["FAKE_EXIT"] = "3"
        result = self.run_pass()
        self.assertEqual(result["action"], "failed")
        self.assertEqual(self.state["chain"]["count"], 0)

    def test_preflight_refuses_before_dispatch(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        blocked = self.root / "blocked"
        blocked.mkdir()
        blocked.chmod(0o500)
        os.environ["DSH_HOME"] = str(blocked / ".dsh")
        try:
            result = self.run_pass()
        finally:
            blocked.chmod(0o700)
        self.assertEqual(result["action"], "refuse")
        self.assertEqual(result["reason"], "preflight")
        self.assertFalse(self.log.exists())

    def test_cc_dispatch_does_not_need_the_dsh_home(self):
        self.baseline()
        self.state["cc_argv"] = [str(self.fake_cc), "-p", "{line}"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        blocked = self.root / "blocked2"
        blocked.mkdir()
        blocked.chmod(0o500)
        os.environ["DSH_HOME"] = str(blocked / ".dsh")
        try:
            result = self.run_pass()
        finally:
            blocked.chmod(0o700)
        self.assertEqual(result["action"], "dispatch")
        self.assertTrue(self.log_cc.exists())

    def test_cc_side_without_command_refuses(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()  # dsh responde
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertIn("cc", result["notices"][0])

    def test_dry_run_dispatches_nothing(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        result = self.run_pass(dry_run=True)
        self.assertEqual(result["action"], "dry-run")
        self.assertFalse(self.log.exists())
        self.assertEqual(self.state["chain"]["count"], 0)

    def test_dry_run_leaves_the_state_file_identical(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        w.save_state(self.state_path, self.state)
        before = self.state_path.read_bytes()
        w.main(["--state", str(self.state_path), "--reviews", str(self.reviews),
                "--hop-logs", str(self.root / "hops"), "--dry-run"])
        self.assertEqual(self.state_path.read_bytes(), before)
        self.assertFalse(self.log.exists())

    def test_dry_run_never_calls_persist(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        before = copy.deepcopy(self.state)
        spy = mock.Mock()
        result = self.run_pass(dry_run=True, persist=spy)
        self.assertEqual(result["action"], "dry-run")
        spy.assert_not_called()
        self.assertEqual(self.state, before)

    # -- passo 5: contar ------------------------------------------------

    def test_the_second_hop_dispatches(self):
        # A Regra 5 diz que o salto nao pede autorizacao: o contador relata,
        # nao impede. O segundo salto tem de sair.
        self.baseline()
        self.state["cc_argv"] = [str(self.fake_cc), "-p", "{line}"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        first = self.log.read_text()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertTrue(self.log_cc.exists(), "houve segundo disparo, e foi para o lado cc")
        self.assertEqual(self.log.read_text(), first, "o lado dsh nao foi chamado de novo")
        self.assertEqual(self.state["chain"]["count"], 2)

    def test_the_counter_only_reports(self):
        # Nenhuma chave de limite sobrevive no estado: o contador e registro.
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        self.assertNotIn("limit", self.state["chain"])
        self.assertNotIn("receipt_run", self.state["chain"])
        self.assertEqual(self.state["chain"]["count"], 1)

    def test_residual_chain_keys_are_dropped_on_save(self):
        # T13: um estado com o porteiro que a v17 tirou carrega sem erro, e sai sem os campos
        self.state["chain"].update({"count": 3, "limit": 1, "limit_source": "contrato",
                                    "receipt": False, "receipt_run": 0})
        w.save_state(self.state_path, self.state)
        loaded = w.load_state(self.state_path)
        self.assertEqual(loaded["chain"]["count"], 3)
        w.save_state(self.state_path, loaded)
        saved = json.loads(self.state_path.read_text(encoding="utf-8"))
        for key in ("limit", "limit_source", "receipt", "receipt_run"):
            self.assertNotIn(key, saved["chain"], "resíduo %s sobreviveu à gravação" % key)
        self.assertEqual(saved["chain"]["count"], 3)

    def test_new_series_archives_the_old_state_and_starts_empty(self):
        # T7: a série anterior fica arquivada, e a primeira mensagem da série nova dispara
        self.state["seen"] = {"R1-cc.md": "velho", "R1-dsh.md": "velho"}
        self.state["initialized"] = True
        self.state["chain"]["count"] = 2
        self.state["cc_argv"] = [str(self.fake_cc)]
        w.save_state(self.state_path, self.state)
        code = w.main(["--state", str(self.state_path), "--reviews", str(self.reviews), "--new-series"])
        self.assertEqual(code, 0)
        archived = list((self.root / ".watcher-series").glob("estado-*.json"))
        self.assertEqual(len(archived), 1, "o estado anterior foi arquivado")
        self.assertIn("R1-dsh.md", archived[0].read_text(encoding="utf-8"))
        self.state = w.load_state(self.state_path)
        self.assertEqual(self.state["seen"], {})
        self.assertEqual(self.state["chain"]["count"], 0)
        self.assertEqual(self.state["cc_argv"], [str(self.fake_cc)])
        make_round(self.reviews, "R1-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertFalse(any("reescrito" in n for n in result["notices"]))

    def test_new_series_refuses_a_registry_that_still_has_files(self):
        make_round(self.reviews, "R1-cc.md")
        code = w.main(["--state", str(self.state_path), "--reviews", str(self.reviews), "--new-series"])
        self.assertEqual(code, 1)
        self.assertFalse((self.root / ".watcher-series").exists(), "nada foi arquivado")

    def test_draft_with_the_marker_waits_and_is_not_marked(self):
        # T1 (item 5): cabeçalho com 0000 é rascunho: não entra em seen, não é FALHA, não dispara
        self.baseline()
        (self.reviews / "R2-cc.md").write_text("<!-- sent: 0000 palavras -->\n# R2\n", encoding="utf-8")
        result = self.run_pass()
        self.assertEqual(result["action"], "pending")
        self.assertFalse(self.log.exists(), "o rascunho nao disparou")
        self.assertNotIn("R2-cc.md", self.state["seen"])
        self.assertFalse(any(n.startswith("FALHA") for n in result["notices"]))
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertEqual(self.state["chain"]["count"], 1, "disparou uma vez, depois da troca")

    def test_draft_over_fifteen_minutes_warns_and_does_not_refuse(self):
        # P-d: o marcador por mais de 15 min é aviso, não FALHA e não silêncio
        self.baseline()
        (self.reviews / "R2-cc.md").write_text("<!-- sent: 0000 palavras -->\n# R2\n", encoding="utf-8")
        self.state["pending"] = {"R2-cc.md": {"since": w.time.time() - 16 * 60, "warned": False}}
        result = self.run_pass()
        self.assertEqual(result["action"], "pending")
        self.assertTrue(any("15 min" in n for n in result["notices"]))
        self.assertFalse(any(n.startswith("FALHA") for n in result["notices"]))

    def test_interrupted_hop_is_noticed_and_never_redispatched(self):
        # T3 (item 9): a marca e o registro "disparando" vão na mesma gravação, antes do subprocesso;
        # no reinício o salto aparece como interrompido, e nada dispara de novo
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        hops = self.root / "hops"
        saved = []

        def persist(state):
            saved.append(json.loads(json.dumps(state)))

        with mock.patch.object(w, "dispatch", side_effect=RuntimeError("queda simulada")):
            with self.assertRaises(RuntimeError):
                self.run_pass(hop_logs=hops, persist=persist)
        self.assertIn("R2-cc.md", saved[-1]["seen"], "a marca foi gravada")
        self.assertIn("disparando", saved[-1], "o registro do salto foi gravado na mesma vez")
        self.state = saved[-1]
        result = self.run_pass(hop_logs=hops)
        self.assertFalse(self.log.exists(), "nenhum disparo no reinício")
        self.assertTrue(any("interrompido" in n for n in result["notices"]), result["notices"])
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(entries[-1]["status"], "salto-interrompido")
        self.assertNotIn("disparando", self.state)

    def test_a_hop_that_returns_clears_the_record(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertNotIn("disparando", self.state)

    def steps_probe(self, steps, extra_stdout=""):
        """Um dsh falso que imprime `steps` passos de modelo no stdout JSON e grava a resposta."""
        probe = self.root / "dsh-steps"
        lines = ['{"type":"status","phase":"step_start","turn":1,"step":%d}' % (i + 1) for i in range(steps)]
        body = "\n".join(lines + [extra_stdout]) + "\n"
        probe.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "sys.stdout.write(%r)\n"
            "open(%r, 'w').write('<!-- sent: 1 palavras -->\\n')\n"
            % (body, str(self.reviews / "R2-dsh.md")), encoding="utf-8")
        probe.chmod(0o755)
        return probe

    def test_steps_are_counted_from_the_hop_json(self):
        # T16 (item 10): conta os passos de modelo (step_start) do stdout JSON; texto puro é sem base
        jsonl = ('{"type":"status","phase":"step_start"}\n{"type":"text","text":"x"}\n'
                 '{"type":"status","phase":"step_start"}\n')
        self.assertEqual(w.count_steps(jsonl), 2)
        self.assertIsNone(w.count_steps("texto puro, sem JSON\n"))

    def test_prediction_is_the_median_of_all_measured_hops_from_three(self):
        hops = self.root / "hops"
        hops.mkdir()
        index = hops / "index.jsonl"
        self.assertIsNone(w.predicted_steps(hops, "dsh"), "sem índice, sem base")
        rows = [{"responder": "dsh", "passos": n, "status": "salto"} for n in (10, 30, 20)]
        index.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual(w.predicted_steps(hops, "dsh"), 20)
        self.assertIsNone(w.predicted_steps(hops, "cc"), "o cc não tem base própria")
        index.write_text("".join(json.dumps(r) + "\n" for r in rows[:2]), encoding="utf-8")
        self.assertIsNone(w.predicted_steps(hops, "dsh"), "duas medidas ainda não são base")

    def test_hop_records_its_steps_and_is_sem_base_without_history(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        hops = self.root / "hops"
        probe = self.steps_probe(3)
        result = self.run_pass(dsh_bin=str(probe), hop_logs=hops)
        self.assertEqual(result["action"], "dispatch")
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(entries[-1]["status"], "salto")
        self.assertEqual(entries[-1]["passos"], 3)
        self.assertIsNone(entries[-1]["previsto"], "sem base: primeira medição")

    def test_a_hop_over_double_the_prediction_is_noticed(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        hops = self.root / "hops"
        hops.mkdir()
        rows = [{"responder": "dsh", "passos": 10, "status": "salto"} for _ in range(3)]
        (hops / "index.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        probe = self.steps_probe(25)
        result = self.run_pass(dsh_bin=str(probe), hop_logs=hops)
        self.assertEqual(result["action"], "dispatch")
        self.assertTrue(any("fora do previsto" in n for n in result["notices"]), result["notices"])

    def run_monitor(self, ticks, on_tick, hops):
        """O monitor por ticks: on_tick roda entre uma consulta e a próxima, no lugar do sono."""
        return w.watch(self.reviews, self.state_path, hops, dsh_bin=str(self.fake), timeout=30,
                       interval=0, max_ticks=ticks, sleep=lambda _: on_tick())

    def prepare_monitor(self):
        self.state["initialized"] = True
        self.state["cc_argv"] = [str(self.fake_cc)]
        w.save_state(self.state_path, self.state)

    def test_monitor_chains_three_hops_and_stops_at_a_silent_one(self):
        # T8 (item 11): a pasta é o start: R1-cc dispara, a resposta dispara a seguinte, e o salto
        # sem resposta encerra a cadeia; três invocações, nenhuma extra
        self.prepare_monitor()
        hops = self.root / "hops"
        make_round(self.reviews, "R1-cc.md")

        def on_tick():
            if (self.reviews / "R2-cc.md").exists():
                os.environ["FAKE_SILENT"] = "1"

        self.run_monitor(12, on_tick, hops)
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 3)
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual([e["status"] for e in entries], ["salto", "salto", "sem-resposta"])

    def test_gate_with_a_question_holds_until_the_next_file_is_written(self):
        # T9 (item 11): gate yes não dispara; a resposta escrita depois libera a cadeia
        self.prepare_monitor()
        hops = self.root / "hops"
        make_round(self.reviews, "R1-cc.md", to_markim="D1", blocks="yes", why_blocking="a escolha e do Markim")
        self.run_monitor(6, lambda: None, hops)
        self.assertFalse(list(hops.glob("hop-*.json")) if hops.exists() else [], "o gate segurou")
        make_round(self.reviews, "R1-dsh.md", cites="R1-cc.md")
        os.environ["FAKE_SILENT"] = "1"
        self.run_monitor(6, lambda: None, hops)
        self.assertEqual(len(list(hops.glob("hop-*.json"))), 1, "a resposta liberou um salto")

    def test_monitor_waits_for_a_stable_registry_before_processing(self):
        # o monitor só processa quando a pasta ficou igual numa consulta; enquanto muda, espera
        self.prepare_monitor()
        runs_at_tick = []
        real = w.run_pass

        def counting(*args, **kwargs):
            runs_at_tick.append(1)
            return real(*args, **kwargs)

        def on_tick():
            n = len(sleeps)
            sleeps.append(n)
            if n < 3:
                (self.reviews / ("R9-cc-nota-%s.md" % "abc"[n])).write_text("nota\n", encoding="utf-8")

        sleeps = []
        with mock.patch.object(w, "run_pass", counting):
            self.run_monitor(6, on_tick, self.root / "hops")
        self.assertEqual(len(runs_at_tick), 1, "uma passada, só depois da pasta parar de mudar")

    def test_procedure_note_names_no_version_and_no_step_list(self):
        # item 12: a nota é uma segunda cópia do procedimento; sem versão e sem lista, ela não envelhece
        note = w.procedure_note("cc")
        self.assertNotRegex(note, r"v\d+")
        self.assertNotIn("leitura em lote", note)
        self.assertIn("docs/auto_critique2.md", note)
        self.assertIn("Não investigue o ambiente.", note)

    def test_monitor_rereads_the_state_each_tick(self):
        # 3.1: uma edição do estado no meio da sessão é respeitada pelo monitor, e não desfeita
        self.prepare_monitor()
        hops = self.root / "hops"
        make_round(self.reviews, "R1-cc.md")

        def on_tick():
            if not getattr(on_tick, "done", False):
                on_tick.done = True
                state = w.load_state(self.state_path)
                state["chain"]["count"] = 99
                w.save_state(self.state_path, state)

        self.run_monitor(6, on_tick, hops)
        hops_done = len(list(hops.glob("hop-*.json")))
        self.assertGreaterEqual(hops_done, 1)
        self.assertEqual(w.load_state(self.state_path)["chain"]["count"], 99 + hops_done,
                         "a edição sobreviveu aos disparos")

    def test_state_commands_refuse_while_a_live_monitor_holds_the_state(self):
        # 3.1: --reset, --set-cc-cmd e --new-series recusam com o monitor vivo (pid desta sessão)
        (self.root / "monitor.lock").write_text(str(os.getpid()), encoding="utf-8")
        self.state["monitor"] = {"pid": os.getpid(), "since": "agora"}
        self.state["chain"]["count"] = 4
        w.save_state(self.state_path, self.state)
        base = ["--state", str(self.state_path), "--reviews", str(self.reviews)]
        self.assertEqual(w.main(base + ["--reset"]), 1)
        self.assertEqual(w.main(base + ["--set-cc-cmd", "claude -p"]), 1)
        self.assertEqual(w.main(base + ["--new-series"]), 1)
        self.assertEqual(w.load_state(self.state_path)["chain"]["count"], 4, "nada foi desfeito")

    def test_count_steps_is_none_without_a_step_start(self):
        # 3.2: um JSON sem step_start não é medição de passo
        self.assertIsNone(w.count_steps('{"type":"status","phase":"other"}\n'))
        self.assertIsNone(w.count_steps('{"type":"text","text":"x"}\n'))

    def test_failed_hops_do_not_feed_the_prediction(self):
        # 3.3: a base da previsão é só de saltos que deram resposta
        hops = self.root / "hops"
        hops.mkdir()
        rows = [{"responder": "dsh", "passos": n, "status": "salto"} for n in (10, 10, 10)]
        rows += [{"responder": "dsh", "passos": 1, "status": "falha-de-salto"} for _ in range(2)]
        rows += [{"responder": "dsh", "passos": 1, "status": "sem-resposta"} for _ in range(2)]
        (hops / "index.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual(w.predicted_steps(hops, "dsh"), 10)

    def test_interrupted_hop_keeps_the_declared_prediction(self):
        # 3.5: o salto interrompido grava a previsão que foi declarada antes do disparo
        self.baseline()
        hops = self.root / "hops"
        self.state["disparando"] = {"hop": "R2-dsh", "round": 2, "responder": "dsh",
                                    "trigger": "R2-cc.md", "target": "R2-dsh.md", "previsto": 45}
        self.run_pass(hop_logs=hops)
        entries = [json.loads(line) for line in (hops / "index.jsonl").read_text().splitlines()]
        self.assertEqual(entries[-1]["status"], "salto-interrompido")
        self.assertEqual(entries[-1]["previsto"], 45)

    def test_status_flags_a_monitor_whose_process_is_gone(self):
        # 5.2: um marcador preso, sem trava viva, não é anunciado como monitor ativo
        self.state["monitor"] = {"pid": 999999, "since": "antes"}
        w.save_state(self.state_path, self.state)
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            w.main(["--state", str(self.state_path), "--status", "--hop-logs", str(self.root / "h")])
        self.assertTrue(any("sem trava" in line for line in out), out)
        self.assertFalse(any("monitor ativo" in line for line in out), out)

    def test_ambiguity_stays_visible_until_the_registry_changes(self):
        # 5.3: três arquivos novos ficam no --status até o registro mudar
        self.baseline()
        for name in ("R2-cc.md", "R3-cc.md", "R4-cc.md"):
            make_round(self.reviews, name)
        self.run_pass()
        w.save_state(self.state_path, self.state)
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            w.main(["--state", str(self.state_path), "--status", "--hop-logs", str(self.root / "h")])
        self.assertTrue(any("ambiguidade" in line for line in out), out)
        (self.reviews / "R4-cc.md").unlink()
        self.run_pass()
        self.assertNotIn("ambiguous", self.state)

    def test_second_monitor_is_refused_while_one_is_alive(self):
        # 1.1 da R8-dsh: um segundo --monitor não sobe com o primeiro vivo
        (self.root / "monitor.lock").write_text(str(os.getpid()), encoding="utf-8")
        self.state["monitor"] = {"pid": os.getpid(), "since": "agora"}
        w.save_state(self.state_path, self.state)
        code = w.main(["--state", str(self.state_path), "--reviews", str(self.reviews),
                       "--hop-logs", str(self.root / "hops"), "--monitor"])
        self.assertEqual(code, 1)

    def test_a_monitor_clears_only_its_own_marker(self):
        # 1.1: o marcador de outro monitor sobrevive à saída deste
        self.prepare_monitor()
        other = os.getppid()

        def on_tick():
            state = w.load_state(self.state_path)
            state["monitor"] = {"pid": other, "since": "outro"}
            w.save_state(self.state_path, state)

        self.run_monitor(2, on_tick, self.root / "hops")
        self.assertEqual(w.load_state(self.state_path).get("monitor", {}).get("pid"), other)

    def test_a_live_lock_refuses_a_second_monitor(self):
        # 3.4 da R13-dsh: uma trava viva recusa o monitor, antes de qualquer leitura do estado
        (self.root / "monitor.lock").write_text(str(os.getppid()), encoding="utf-8")
        code = w.watch(self.reviews, self.state_path, self.root / "hops", max_ticks=1, sleep=lambda _: None,
                       lock_path=self.root / "monitor.lock")
        self.assertEqual(code, 1)
        self.assertTrue((self.root / "monitor.lock").exists(), "a trava de outro não é removida")

    def test_a_dead_lock_is_taken_over_and_removed_on_exit(self):
        lock = self.root / "monitor.lock"
        lock.write_text("999999", encoding="utf-8")
        code = w.watch(self.reviews, self.state_path, self.root / "hops", max_ticks=1, sleep=lambda _: None,
                       lock_path=lock)
        self.assertEqual(code, 0)
        self.assertFalse(lock.exists(), "a trava própria sai na saída")

    def test_a_live_lock_alone_refuses_the_state_commands(self):
        # 3.2 da R14-dsh: a trava é a autoridade; sem marcador, uma trava viva já recusa o comando
        (self.root / "monitor.lock").write_text(str(os.getppid()), encoding="utf-8")
        self.state["chain"]["count"] = 4
        w.save_state(self.state_path, self.state)
        base = ["--state", str(self.state_path), "--reviews", str(self.reviews)]
        self.assertEqual(w.main(base + ["--reset"]), 1)
        self.assertEqual(w.load_state(self.state_path)["chain"]["count"], 4)

    def test_status_names_the_lock_as_the_source(self):
        (self.root / "monitor.lock").write_text(str(os.getppid()), encoding="utf-8")
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            w.main(["--state", str(self.state_path), "--status", "--hop-logs", str(self.root / "h")])
        self.assertTrue(any("pela trava" in line for line in out), out)

    def cwd_probe(self, name):
        """Um disparo falso que grava o diretorio de trabalho em que foi chamado."""
        out = self.root / (name + ".cwd")
        probe = self.root / name
        probe.write_text("#!/usr/bin/env python3\nimport os\nopen(%r, 'w').write(os.getcwd())\n" % str(out),
                         encoding="utf-8")
        probe.chmod(0o755)
        return probe, out

    def test_dsh_hop_runs_in_the_reviews_folder(self):
        # o dsh escreve em docs/reviews/: o processo dele começa lá, e o watcher diz isso
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        probe, out = self.cwd_probe("dsh-cwd")
        result = self.run_pass(dsh_bin=str(probe))
        self.assertIn(result["action"], ("dispatch", "no-answer"))
        self.assertEqual(pathlib.Path(out.read_text()).resolve(), self.reviews.resolve())

    def test_cc_hop_runs_in_the_repository_root(self):
        # o cc roda na raiz do repositório, porque o comando aprovado dele escreve em caminhos de lá
        self.baseline()
        probe, out = self.cwd_probe("cc-cwd")
        self.state["cc_argv"] = [str(probe)]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        result = self.run_pass()
        self.assertIn(result["action"], ("dispatch", "no-answer"))  # o probe não grava resposta
        self.assertEqual(pathlib.Path(out.read_text()).resolve(), w.ROOT.resolve())

    def test_procedure_note_points_to_the_contract_from_each_side(self):
        self.assertIn("../auto_critique2.md", w.procedure_note("dsh"))
        self.assertIn("docs/auto_critique2.md", w.procedure_note("cc"))
        self.assertNotIn("../", w.procedure_note("cc"))

    def test_preflight_refuses_danger_full_access(self):
        # o modo sem cerca não dispara o dsh: a cerca é o que a mudança de cwd promete
        with mock.patch.dict(os.environ, {"DSH_PERMISSION_MODE": "danger-full-access"}):
            ok, why = w.preflight()
        self.assertFalse(ok)
        self.assertIn("danger-full-access", why)

    def test_dsh_hop_is_refused_under_danger_full_access(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        with mock.patch.dict(os.environ, {"DSH_PERMISSION_MODE": "danger-full-access"}):
            result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertFalse(self.log.exists(), "o dsh não foi chamado")

    def test_index_records_the_effective_mode_of_a_dsh_hop(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        hops = self.root / "hops"
        with mock.patch.dict(os.environ):
            os.environ.pop("DSH_PERMISSION_MODE", None)
            self.run_pass(hop_logs=hops)
        entry = json.loads((hops / "index.jsonl").read_text().splitlines()[-1])
        self.assertEqual(entry["modo"], "workspace-write")

    def test_reset_zeroes_the_counter_and_leaves_a_notice(self):
        w.save_state(self.state_path, self.state)
        self.state["chain"]["count"] = 2
        w.save_state(self.state_path, self.state)
        code = w.main(["--state", str(self.state_path), "--reset"])
        self.assertEqual(code, 0)
        loaded = w.load_state(self.state_path)
        self.assertEqual(loaded["chain"]["count"], 0)
        self.assertTrue(any("reset manual: contador 2 -> 0" in n for n in loaded["notices"]))

    def test_status_prints_the_chain(self):
        self.state["chain"]["count"] = 1
        w.save_state(self.state_path, self.state)
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            code = w.main(["--state", str(self.state_path), "--status"])
        self.assertEqual(code, 0)
        text = chr(10).join(out)
        self.assertIn("cadeia: 1 salto(s)", text)

    def test_the_contract_says_the_hop_needs_no_authorization(self):
        # A correspondencia contrato <-> codigo, na direcao nova: se o contrato
        # voltar a prometer uma trava, este teste falha antes de o codigo mudar.
        contract = pathlib.Path(HERE).parent / "docs" / "auto_critique2.md"
        text = contract.read_text(encoding="utf-8")
        self.assertIn("Não há trava e não há reset", text)
        self.assertNotIn("O default é", text)
        self.assertFalse(hasattr(w, "DEFAULT_LIMIT"), "o codigo nao deve ter limite")

    # -- o registro fica intacto ----------------------------------------

    def test_hop_output_is_logged_outside_the_registry(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        logs = self.root / "hops"
        result = w.run_pass(self.reviews, self.state, dsh_bin=str(self.fake),
                            timeout=30, hop_logs=logs)
        self.assertEqual(result["action"], "dispatch")
        files = list(logs.glob("hop-*.json"))
        self.assertEqual(len(files), 1)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(record["line"],
                         "rodada aberta:  leia R2-cc.md e responda em R2-dsh.md")
        self.assertIn("argv", record["output"])

    def test_state_is_saved_before_the_dispatch(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        marks = []

        def persist(state):
            marks.append(dict(state["seen"]))

        with mock.patch.object(w, "dispatch", side_effect=RuntimeError("interrompido")):
            with self.assertRaises(RuntimeError):
                w.run_pass(self.reviews, self.state, dsh_bin=str(self.fake), timeout=30,
                           persist=persist)
        self.assertTrue(marks, "persist nao foi chamado")
        self.assertIn("R2-cc.md", marks[-1], "o arquivo tem de estar gravado antes do disparo")

    def test_cc_command_takes_the_line_and_the_target(self):
        self.baseline()
        self.state["cc_argv"] = [str(self.fake_cc), "-p", "{line}", "--allowedTools",
                                 "Write(docs/reviews/{target})"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertEqual(json.loads(self.log_cc.read_text()), [
            "-p",
            "par completo:   leia docs/reviews/R2-dsh.md e responda em docs/reviews/R3-cc.md" + w.procedure_note("cc"),
            "--allowedTools",
            "Write(docs/reviews/R3-cc.md)",
        ])

    def test_cc_permission_warning_becomes_a_notice(self):
        self.baseline()
        warn = self.root / "claude-warn"
        warn.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "sys.stderr.write('Permission allow rule (--allowed-tools): "
            "Write(docs/reviews/R3-cc.md) is not matched by file permission checks\\n')\n"
            "open(%r, 'w').write('resposta\\n')\n" % str(self.reviews / "R3-cc.md"),
            encoding="utf-8")
        warn.chmod(0o755)
        self.state["cc_argv"] = [str(warn), "-p", "{line}"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertTrue(any("is not matched by file permission checks" in n
                            for n in result["notices"]), result["notices"])

    def test_hop_env_names_the_round_and_responder(self):
        self.baseline()
        seen = self.root / "hop-env.txt"
        probe = self.root / "claude-env"
        probe.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "open(%r, 'w').write(os.environ.get('WATCHER_HOP', ''))\n" % str(seen)
            + "open(%r, 'w').write('resposta\\n')\n" % str(self.reviews / "R3-cc.md"),
            encoding="utf-8")
        probe.chmod(0o755)
        self.state["cc_argv"] = [str(probe), "-p", "{line}"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertEqual(seen.read_text(), "R3-cc")

    def test_the_watcher_never_writes_the_registry(self):
        os.environ.pop("FAKE_REVIEWS", None)  # o dsh falso não grava: o watcher é que não pode
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        before = {p.name: p.read_bytes() for p in self.reviews.glob("*.md")}
        self.run_pass()
        after = {p.name: p.read_bytes() for p in self.reviews.glob("*.md")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
