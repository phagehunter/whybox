"""Tests for the toolkit itself. Run with: python -m pytest -q (or unittest).

These are deliberately about the things that would silently ruin a sandbox:
the answer key leaking, a malformed specimen being accepted, the loop losing
a round. They are not about the science in any particular sandbox.
"""

import json
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from whybox.agents.scripted import HillClimbAgent, RandomAgent  # noqa: E402
from whybox.judge import judge_run, rubric_check  # noqa: E402
from whybox.runner import Runner, SealedOracleClient  # noqa: E402
from whybox.spec import SpecError, load_spec  # noqa: E402

SANDBOX = os.path.join(REPO, "sandboxes", "codon-lite")


class TestSpec(unittest.TestCase):
    def test_reads_the_example_manifest(self):
        spec = load_spec(SANDBOX)
        self.assertEqual(spec.name, "codon-lite")
        self.assertEqual(spec.oracle_kind, "dry")
        self.assertEqual(spec.data["oracle_config"]["world"], "single-position")
        self.assertIn("fitness", spec.report_fields)

    def test_rejects_a_folder_with_no_manifest(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertRaises(SpecError, load_spec, empty)


class TestSealedWall(unittest.TestCase):
    """The wall is the whole framework. If it leaks, nothing else matters."""

    def test_answer_key_is_refused_during_a_run(self):
        client = SealedOracleClient(SANDBOX, reveal=False)
        try:
            response = client.ask({"op": "answer_key"})
            self.assertFalse(response["ok"])
            self.assertEqual(response["kind"], "sealed")
            self.assertNotIn("silent", json.dumps(response).lower())
        finally:
            client.close()

    def test_answer_key_is_available_afterwards(self):
        client = SealedOracleClient(SANDBOX, reveal=True)
        try:
            response = client.ask({"op": "answer_key"})
            self.assertTrue(response["ok"])
            self.assertIn("key_claims", response["result"])
        finally:
            client.close()

    def test_report_contains_only_the_promised_numbers(self):
        client = SealedOracleClient(SANDBOX, reveal=False)
        try:
            facts = client.ask({"op": "describe"})["result"]
            specimen = "AA" * (facts["specimen_length"] // 2)
            report = client.ask({"op": "measure", "specimens": [specimen]})["result"]
            self.assertEqual(list(report["scores"]), ["fitness"])
            self.assertNotIn("extras", report)
        finally:
            client.close()

    def test_malformed_specimens_are_rejected(self):
        client = SealedOracleClient(SANDBOX, reveal=False)
        try:
            for bad in ["", "ZZZZ", "A" * 7]:
                response = client.ask({"op": "measure", "specimens": [bad]})
                self.assertFalse(response["ok"], "accepted a bad specimen: %r" % bad)
                self.assertEqual(response["kind"], "validation")
        finally:
            client.close()


class TestLoop(unittest.TestCase):
    def test_a_short_run_produces_a_complete_record(self):
        spec = load_spec(SANDBOX)
        with tempfile.TemporaryDirectory() as runs:
            summary = Runner(spec, HillClimbAgent(seed=3), runs_root=runs,
                             rounds=6, quiet=True).run()
            self.assertEqual(summary["rounds_used"], 6)
            self.assertEqual(summary["status"], "complete")
            folder = [os.path.join(runs, d) for d in os.listdir(runs)][0]
            for name in ("run.json", "rounds.jsonl", "notebook.md", "answer_key.json"):
                self.assertTrue(os.path.isfile(os.path.join(folder, name)), name)
            with open(os.path.join(folder, "rounds.jsonl")) as handle:
                self.assertEqual(len([ln for ln in handle if ln.strip()]), 6)

    def test_the_baseline_scores_well_and_understands_nothing(self):
        """The result the whole framework exists to make visible."""
        spec = load_spec(SANDBOX)
        with tempfile.TemporaryDirectory() as runs:
            summary = Runner(spec, HillClimbAgent(seed=1), runs_root=runs,
                             rounds=25, quiet=True).run()
            folder = [os.path.join(runs, d) for d in os.listdir(runs)][0]
            verdict = judge_run(folder, write=False)
            self.assertGreaterEqual(summary["best_score"], 3.0)
            self.assertEqual(verdict["insight"]["claims_found"], 0)

    def test_random_investigator_also_runs(self):
        spec = load_spec(SANDBOX)
        with tempfile.TemporaryDirectory() as runs:
            summary = Runner(spec, RandomAgent(seed=0), runs_root=runs,
                             rounds=4, quiet=True).run()
            self.assertEqual(summary["rounds_used"], 4)


class TestJudge(unittest.TestCase):
    def test_rubric_finds_a_claim_phrased_differently(self):
        key = {"key_claims": [{"claim": "first position is silent",
                               "synonyms": ["position 1 does not matter"]}]}
        hit = rubric_check("I showed position 1 does not matter at all.", "", key)
        self.assertEqual(hit["claims_found"], 1)
        miss = rubric_check("The sequence is read backwards.", "", key)
        self.assertEqual(miss["claims_found"], 0)


if __name__ == "__main__":
    unittest.main()


class TestLeaderboard(unittest.TestCase):
    """A row has to carry both results and the sandbox version, or it is not
    comparable with anything and must be refused."""

    def _finished_run(self, runs_root):
        spec = load_spec(SANDBOX)
        Runner(spec, HillClimbAgent(seed=2), runs_root=runs_root,
               rounds=5, quiet=True).run()
        return [os.path.join(runs_root, d) for d in os.listdir(runs_root)][0]

    def test_a_row_carries_score_and_insight_side_by_side(self):
        from whybox.leaderboard import row_from_run, validate_row
        with tempfile.TemporaryDirectory() as runs:
            row = row_from_run(self._finished_run(runs))
            self.assertEqual(validate_row(row), [])
            self.assertIn("best_score", row)
            self.assertIn("claims_found", row)
            self.assertNotIn("overall", row)  # never a single combined number

    def test_a_row_without_a_sandbox_version_is_refused(self):
        from whybox.leaderboard import append_row, row_from_run
        with tempfile.TemporaryDirectory() as runs:
            row = row_from_run(self._finished_run(runs))
            row["sandbox_version"] = None
            with self.assertRaises(ValueError):
                append_row(row, os.path.join(runs, "results.jsonl"))

    def test_the_fingerprint_changes_if_the_notebook_is_edited(self):
        from whybox.leaderboard import row_from_run
        with tempfile.TemporaryDirectory() as runs:
            folder = self._finished_run(runs)
            before = row_from_run(folder)["run_fingerprint"]
            with open(os.path.join(folder, "notebook.md"), "a") as handle:
                handle.write("\nand then I understood everything.\n")
            self.assertNotEqual(before, row_from_run(folder)["run_fingerprint"])

    def test_the_table_sorts_by_insight_before_score(self):
        from whybox.leaderboard import render_table
        rows = [
            {"sandbox": "x", "sandbox_version": "1", "agent": "optimizer",
             "best_score": 9.0, "claims_found": 0, "claims_total": 4},
            {"sandbox": "x", "sandbox_version": "1", "agent": "scientist",
             "best_score": 4.0, "claims_found": 3, "claims_total": 4},
        ]
        table = render_table(rows)
        self.assertLess(table.index("scientist"), table.index("optimizer"))


class TestAnswerKeyDoesNotLeak(unittest.TestCase):
    """The leak that matters in practice, and the fix for it.

    The sealed wall is pointless if an earlier run of the same sandbox wrote
    the rule to disk where the next run can read it.
    """

    def _run(self, runs_root, reveal):
        spec = load_spec(SANDBOX)
        Runner(spec, HillClimbAgent(seed=5), runs_root=runs_root, rounds=4,
               quiet=True, reveal_key=reveal).run()
        return [os.path.join(runs_root, d) for d in os.listdir(runs_root)][0]

    def test_an_agent_run_leaves_no_answer_key_behind(self):
        with tempfile.TemporaryDirectory() as runs:
            folder = self._run(runs, reveal=False)
            self.assertFalse(os.path.exists(os.path.join(folder, "answer_key.json")))

    def test_a_person_still_gets_to_see_the_rule(self):
        with tempfile.TemporaryDirectory() as runs:
            folder = self._run(runs, reveal=True)
            self.assertTrue(os.path.exists(os.path.join(folder, "answer_key.json")))

    def test_grading_still_works_without_a_key_in_the_run_folder(self):
        with tempfile.TemporaryDirectory() as runs:
            folder = self._run(runs, reveal=False)
            verdict = judge_run(folder, write=False,
                                sandbox_root=os.path.join(REPO, "sandboxes"))
            self.assertEqual(verdict["insight"]["claims_total"], 4)

    def test_the_commitment_is_recorded_and_is_not_the_rule(self):
        with tempfile.TemporaryDirectory() as runs:
            folder = self._run(runs, reveal=False)
            with open(os.path.join(folder, "run.json")) as handle:
                summary = json.load(handle)
            commitment = summary["metadata"]["rule_commitment_sha256"]
            self.assertEqual(len(commitment), 64)
            self.assertNotIn("silent", commitment.lower())


class TestGraderAudit(unittest.TestCase):
    def test_the_audit_proves_the_word_matching_grade_is_inflatable(self):
        """We publish this attack rather than waiting for someone to find it."""
        from whybox.judge import audit_rubric

        result = audit_rubric(SANDBOX)
        self.assertEqual(result["claims_found"], result["claims_total"])
        self.assertTrue(result["fully_inflatable"])


class TestRankingRules(unittest.TestCase):
    def test_a_confident_notebook_with_no_score_is_not_ranked(self):
        from whybox.leaderboard import is_rankable

        freeloader = {"best_score": 0.0, "claims_found": 4, "claims_total": 4}
        worker = {"best_score": 5.0, "claims_found": 2, "claims_total": 4}
        self.assertFalse(is_rankable(freeloader, ceiling=6.0))
        self.assertTrue(is_rankable(worker, ceiling=6.0))

    def test_the_tie_break_prefers_a_reproduced_row(self):
        from whybox.leaderboard import sort_key

        tie = {"claims_found": 2, "claims_total": 4, "best_score": 5.0,
               "rounds_used": 10, "insight_graded_by": "rubric"}
        unverified = dict(tie, status="unverified")
        reproduced = dict(tie, status="reproduced")
        self.assertGreater(sort_key(reproduced), sort_key(unverified))

    def test_the_tie_break_prefers_a_human_grade_over_word_matching(self):
        from whybox.leaderboard import sort_key

        tie = {"claims_found": 2, "claims_total": 4, "best_score": 5.0,
               "rounds_used": 10, "status": "unverified"}
        self.assertGreater(sort_key(dict(tie, insight_graded_by="human")),
                           sort_key(dict(tie, insight_graded_by="rubric")))


class TestVersionFormat(unittest.TestCase):
    def test_an_old_style_version_is_refused_with_an_explanation(self):
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "codon-lite")
            shutil.copytree(SANDBOX, copy)
            path = os.path.join(copy, "sandbox.yaml")
            with open(path) as handle:
                text = handle.read()
            import re as _re
            swapped = _re.sub(r"(?m)^version:.*$", "version: 0.1.0", text)
            self.assertIn("version: 0.1.0", swapped,
                          "the test could not find a version line to replace")
            with open(path, "w") as handle:
                handle.write(swapped)
            with self.assertRaises(SpecError) as caught:
                load_spec(copy)
            self.assertIn("1-A", str(caught.exception))
