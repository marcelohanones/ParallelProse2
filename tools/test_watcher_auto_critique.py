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
import json, os, sys
with open(os.environ["%s"], "w") as handle:
    json.dump(sys.argv[1:], handle)
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


def make_round(reviews, name, *, cites=None, to_markim="none", blocks="no", why=None,
               gap=None, sent_ok=True):
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
        })
        self.env.start()
        os.environ.pop("FAKE_EXIT", None)
        self.orig_reviews = chk.REVIEWS
        self.state = w.new_state()

    def tearDown(self):
        chk.REVIEWS = self.orig_reviews
        self.env.stop()
        self.tmp.cleanup()

    # -- helpers ---------------------------------------------------------

    def run_pass(self, **kwargs):
        kwargs.setdefault("dsh_bin", str(self.fake))
        kwargs.setdefault("timeout", 5)
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
                         "rodada aberta:  leia docs/reviews/R2-cc.md e responda em R2-dsh.md"])
        self.assertEqual(self.state["chain"]["count"], 1)

    def test_complete_pair_dispatches_the_next_round(self):
        self.baseline()
        self.state["chain"]["limit"] = 2
        self.state["cc_argv"] = [str(self.fake_cc)]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        sent = json.loads(self.log_cc.read_text())
        self.assertEqual(sent, ["par completo:   leia docs/reviews/R2-dsh.md e responda em R3-cc.md"])

    def test_addendum_never_triggers(self):
        self.baseline()
        make_round(self.reviews, "R1-dsh-nota.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "idle")
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

    def test_out_of_order_is_refused(self):
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
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", to_markim="M1", blocks="yes")
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
        self.state["chain"]["limit"] = 2
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
        self.state["chain"]["limit"] = 2
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

    def test_limit_refuses_the_second_hop(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        first = self.log.read_text()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertEqual(result["reason"], "trava")
        self.assertEqual(self.log.read_text(), first, "nao houve segundo disparo")
        self.assertEqual(self.state["chain"]["count"], 1)

    def test_escalation_after_three_receipt_chains(self):
        self.baseline()
        self.state["chain"].update({"count": 1, "limit": 1, "receipt": True, "receipt_run": 0})
        for name in ("R2-cc.md", "R3-cc.md", "R4-cc.md"):
            make_round(self.reviews, name, cites="R1-dsh.md")
            result = self.run_pass()
            self.assertEqual(result["action"], "refuse")
            self.assertEqual(result["reason"], "trava")
        self.assertEqual(self.state["chain"]["limit"], 2)
        self.assertEqual(self.state["chain"]["limit_source"], "regra")
        self.assertTrue(any("proxy" in n for n in self.state["notices"]))

    def test_discarded_message_lowers_the_limit(self):
        self.baseline()
        self.state["chain"].update({"limit": 2, "limit_source": "manual", "count": 1,
                                    "last_hop": {"round": 1, "trigger": "R1-cc.md", "responder": "dsh"}})
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md", sent_ok=False)
        result = self.run_pass()
        self.assertEqual(result["action"], "refuse")
        self.assertEqual(self.state["chain"]["limit"], 1)
        self.assertEqual(self.state["chain"]["limit_source"], "regra")

    def test_reset_zeroes_the_counter(self):
        w.save_state(self.state_path, self.state)
        self.state["chain"]["count"] = 2
        self.state["chain"]["limit"] = 2
        w.save_state(self.state_path, self.state)
        code = w.main(["--state", str(self.state_path), "--reset"])
        self.assertEqual(code, 0)
        self.assertEqual(w.load_state(self.state_path)["chain"]["count"], 0)

    def test_set_limit_records_manual_and_warns(self):
        w.save_state(self.state_path, self.state)
        code = w.main(["--state", str(self.state_path), "--set-limit", "2"])
        self.assertEqual(code, 0)
        loaded = w.load_state(self.state_path)
        self.assertEqual(loaded["chain"]["limit"], 2)
        self.assertEqual(loaded["chain"]["limit_source"], "manual")

    def test_status_prints_the_chain(self):
        self.state["chain"]["count"] = 1
        w.save_state(self.state_path, self.state)
        out = []
        with mock.patch("builtins.print", lambda *a, **k: out.append(" ".join(str(x) for x in a))):
            code = w.main(["--state", str(self.state_path), "--status"])
        self.assertEqual(code, 0)
        text = chr(10).join(out)
        self.assertIn("cadeia: 1 salto(s)", text)

    def test_limit_constant_matches_the_contract(self):
        contract = pathlib.Path(HERE).parent / "docs" / "auto_critique2.md"
        found = w.LIMIT_RE.search(contract.read_text(encoding="utf-8"))
        self.assertIsNotNone(found, "o contrato precisa dizer o default da trava")
        self.assertEqual(int(found.group(1)), w.DEFAULT_LIMIT)

    def test_receipt_proxy(self):
        self.assertTrue(w.is_receipt({"to-markim": "none", "blocks-advance": "no"}))
        self.assertFalse(w.is_receipt({"to-markim": "M1", "blocks-advance": "no"}))
        self.assertFalse(w.is_receipt({"to-markim": "none", "blocks-advance": "yes"}))

    # -- o registro fica intacto ----------------------------------------

    def test_hop_output_is_logged_outside_the_registry(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        logs = self.root / "hops"
        result = w.run_pass(self.reviews, self.state, dsh_bin=str(self.fake),
                            timeout=5, hop_logs=logs)
        self.assertEqual(result["action"], "dispatch")
        files = list(logs.glob("hop-*.json"))
        self.assertEqual(len(files), 1)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(record["line"],
                         "rodada aberta:  leia docs/reviews/R2-cc.md e responda em R2-dsh.md")
        self.assertIn("argv", record["output"])

    def test_state_is_saved_before_the_dispatch(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        marks = []

        def persist(state):
            marks.append(dict(state["seen"]))

        with mock.patch.object(w, "dispatch", side_effect=RuntimeError("interrompido")):
            with self.assertRaises(RuntimeError):
                w.run_pass(self.reviews, self.state, dsh_bin=str(self.fake), timeout=5,
                           persist=persist)
        self.assertTrue(marks, "persist nao foi chamado")
        self.assertIn("R2-cc.md", marks[-1], "o arquivo tem de estar gravado antes do disparo")

    def test_cc_command_takes_the_line_and_the_target(self):
        self.baseline()
        self.state["chain"]["limit"] = 2
        self.state["cc_argv"] = [str(self.fake_cc), "-p", "{line}", "--allowedTools",
                                 "Write(docs/reviews/{target})"]
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        self.run_pass()
        make_round(self.reviews, "R2-dsh.md", cites="R2-cc.md")
        result = self.run_pass()
        self.assertEqual(result["action"], "dispatch")
        self.assertEqual(json.loads(self.log_cc.read_text()), [
            "-p",
            "par completo:   leia docs/reviews/R2-dsh.md e responda em R3-cc.md",
            "--allowedTools",
            "Write(docs/reviews/R3-cc.md)",
        ])

    def test_the_watcher_never_writes_the_registry(self):
        self.baseline()
        make_round(self.reviews, "R2-cc.md", cites="R1-dsh.md")
        before = {p.name: p.read_bytes() for p in self.reviews.glob("*.md")}
        self.run_pass()
        after = {p.name: p.read_bytes() for p in self.reviews.glob("*.md")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
