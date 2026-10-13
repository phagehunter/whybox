"""Tests for the example sandbox's own science.

A sandbox author should write tests like these: not "does the code run" but
"is the hidden rule actually the rule, and is the task actually hard in the
way I claim it is".
"""

import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX = os.path.join(REPO, "sandboxes", "codon-lite")
sys.path.insert(0, REPO)
sys.path.insert(0, SANDBOX)

from sealed.folding import best_fold_score, ceiling  # noqa: E402
from sealed.rules import WORLDS  # noqa: E402


class TestFolding(unittest.TestCase):
    def test_a_chain_with_no_sticky_beads_scores_zero(self):
        self.assertEqual(best_fold_score("PPPPPPPPPPPP"), 0)

    def test_an_all_sticky_chain_reaches_the_ceiling(self):
        self.assertEqual(best_fold_score("H" * 12), ceiling(12))

    def test_the_ceiling_is_what_the_answer_key_claims(self):
        self.assertEqual(ceiling(12), 6)

    def test_neighbors_along_the_chain_do_not_count_as_touching(self):
        # Two sticky beads side by side in the chain are always next to each
        # other, so counting them would give every chain free points.
        self.assertEqual(best_fold_score("HHPPPPPPPPPP"), 0)


class TestWorlds(unittest.TestCase):
    def test_single_position_ignores_the_first_character(self):
        world = WORLDS["single-position"]
        for first in world.alphabet:
            self.assertEqual(world.translate(first + "A"), "H")
            self.assertEqual(world.translate(first + "C"), "P")

    def test_paired_depends_on_both_characters(self):
        world = WORLDS["paired"]
        self.assertEqual(world.translate("AG"), "H")
        self.assertEqual(world.translate("AC"), "P")
        # Neither character alone predicts the bead.
        outcomes = {world.translate("A" + second) for second in world.alphabet}
        self.assertEqual(outcomes, {"H", "P"})

    def test_every_world_has_a_balanced_table(self):
        """Half sticky, half not, so the alphabet gives nothing away."""
        for name, world in WORLDS.items():
            table = world.table()
            sticky = sum(1 for value in table.values() if value == "H")
            self.assertEqual(sticky * 2, len(table), "%s is unbalanced" % name)

    def test_the_ceiling_is_easy_to_reach_by_accident(self):
        """The reason a high score proves nothing in this sandbox.

        A sequence of one repeated character hits the maximum in at least one
        world, so trial and error finds it within a handful of rounds.
        """
        world = WORLDS["single-position"]
        hits = [c for c in world.alphabet
                if best_fold_score(world.to_chain(c * 24)) == ceiling(12)]
        self.assertTrue(hits, "no single repeated character reaches the ceiling")


if __name__ == "__main__":
    unittest.main()
