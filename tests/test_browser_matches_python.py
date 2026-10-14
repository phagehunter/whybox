"""The browser page and the Python package must agree about the hidden rule.

The page at the project's website reimplements the codon-lite world in
JavaScript, because a browser cannot run the Python oracle in a separate
process. Two implementations of one rule is a maintenance trap: they drift,
nobody notices, and a student is then graded against a different world from
the one the toolkit documents.

This test closes the trap. It runs the JavaScript under node and compares its
answers with Python's on a spread of sequences, including the edge cases that
matter: all one character, alternating pairs, and chains with no sticky beads
at all. It is skipped, not failed, where node is unavailable.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "sandboxes", "codon-lite"))

from sealed.folding import best_fold_score, ceiling  # noqa: E402
from sealed.rules import WORLDS  # noqa: E402

SCRIPT = """
const w = require(process.argv[1]);
const sequences = JSON.parse(process.argv[2]);
const out = sequences.map(s => w.measure(s));
console.log(JSON.stringify({scores: out, ceiling: w.ceiling(),
                            length: w.SEQUENCE_LENGTH}));
"""


class TestBrowserRuleMatchesPython(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        cls.bundle = os.path.join(REPO, "assets", "whybox.js")
        if not cls.node:
            raise unittest.SkipTest("node is not installed; cannot check the browser rule")
        if not os.path.isfile(cls.bundle):
            raise unittest.SkipTest("no browser bundle to check")

    def _javascript(self, sequences):
        result = subprocess.run(
            [self.node, "-e", SCRIPT, self.bundle, json.dumps(sequences)],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(result.returncode, 0,
                         "node failed:\n%s" % result.stderr)
        return json.loads(result.stdout)

    def test_the_two_implementations_agree(self):
        world = WORLDS["single-position"]
        rng = random.Random(20261014)
        alphabet = world.alphabet

        sequences = ["".join(rng.choice(alphabet) for _ in range(24))
                     for _ in range(80)]
        sequences += [
            "A" * 24,          # every group sticky: the ceiling, found by accident
            "C" * 24,          # nothing sticky at all
            "CA" * 12,         # first character varies, score should not move
            "AC" * 12,         # shifted by one, score should collapse
            "AGAGAGAGAGAGAGAGAGAGAGAG",
            "TTTTTTTTTTTTTTTTTTTTTTTT",
        ]

        reported = self._javascript(sequences)
        self.assertEqual(reported["length"], 24)
        self.assertEqual(reported["ceiling"], ceiling(12))

        mismatches = []
        for sequence, js_score in zip(sequences, reported["scores"]):
            py_score = best_fold_score(world.to_chain(sequence))
            if py_score != js_score:
                mismatches.append((sequence, py_score, js_score))

        self.assertEqual(mismatches, [],
                         "the browser rule and the Python rule disagree")

    def test_the_silent_position_really_is_silent_in_both(self):
        """The finding the whole sandbox turns on, checked in both languages."""
        pairs = [("AA" * 12, "CA" * 12), ("AG" * 12, "TG" * 12)]
        flat = [s for pair in pairs for s in pair]
        scores = self._javascript(flat)["scores"]
        self.assertEqual(scores[0], scores[1])
        self.assertEqual(scores[2], scores[3])


if __name__ == "__main__":
    unittest.main()


class TestBothGradersAgree(unittest.TestCase):
    """The grader in the browser and the grader in Python must say the same thing.

    A student who plays on the website and then runs the toolkit should not
    get two different verdicts on the same sentence.
    """

    PHRASINGS = [
        "I could not work it out.",
        "Something about pairs of characters mattering.",
        "Every second letter decides it and the one before it is ignored.",
        ("It reads two letters at a time, the first does not matter, A or G "
         "is sticky, and the score counts how many sticky ones end up "
         "touching after it folds."),
        ("read in groups of two; first position is silent; A or G gives a "
         "sticky bead; score counts touching sticky pairs"),
    ]

    GRADE_SCRIPT = """
const w = require(process.argv[1]);
const texts = JSON.parse(process.argv[2]);
console.log(JSON.stringify(texts.map(t => w.gradeStatedRule(t).found)));
"""

    def test_the_two_graders_give_the_same_counts(self):
        node = shutil.which("node")
        bundle = os.path.join(REPO, "assets", "whybox.js")
        if not node or not os.path.isfile(bundle):
            raise unittest.SkipTest("node or the browser bundle is unavailable")

        from whybox.judge import rubric_check
        from whybox.runner import SealedOracleClient

        client = SealedOracleClient(os.path.join(REPO, "sandboxes", "codon-lite"),
                                    reveal=True)
        try:
            answer_key = client.ask({"op": "answer_key"})["result"]
        finally:
            client.close()

        result = subprocess.run(
            [node, "-e", self.GRADE_SCRIPT, bundle, json.dumps(self.PHRASINGS)],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(result.returncode, 0, result.stderr)
        js_counts = json.loads(result.stdout)

        py_counts = [rubric_check(text, "", answer_key)["claims_found"]
                     for text in self.PHRASINGS]
        self.assertEqual(py_counts, js_counts,
                         "the browser grader and the Python grader disagree")

    def test_a_correct_rule_in_plain_words_is_not_scored_zero(self):
        """The failure that matters most for a student.

        Keyword matching punishes someone who understood the system and said
        so in their own words. A student told they scored zero for a correct
        answer learns the wrong lesson, and it is worse than the opposite
        failure of rewarding a stuffed notebook.
        """
        from whybox.judge import rubric_check
        from whybox.runner import SealedOracleClient

        client = SealedOracleClient(os.path.join(REPO, "sandboxes", "codon-lite"),
                                    reveal=True)
        try:
            answer_key = client.ask({"op": "answer_key"})["result"]
        finally:
            client.close()

        plain = ("It reads two letters at a time, the first does not matter, "
                 "A or G is sticky, and the score counts how many sticky ones "
                 "end up touching after it folds.")
        self.assertEqual(rubric_check(plain, "", answer_key)["claims_found"], 4)
