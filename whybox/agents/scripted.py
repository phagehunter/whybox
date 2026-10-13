"""Two investigators that do not think, for use as baselines."""

import random
from typing import Any, Dict, List, Optional

from whybox.agents.base import Agent


def _facts(agent: Agent):
    alphabet = agent.facts.get("alphabet", "ACGT")
    length = int(agent.facts.get("specimen_length", 24))
    return alphabet, length


class RandomAgent(Agent):
    """Submits a random specimen every round. The floor any method must clear."""

    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def propose(self, round_index: int, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        alphabet, length = _facts(self)
        specimen = "".join(self.rng.choice(alphabet) for _ in range(length))
        return {"specimens": [specimen],
                "rationale": "random guess, no hypothesis"}

    def conclude(self, history: List[Dict[str, Any]]) -> str:
        return "No theory. This investigator guesses and never looks at the results."


class HillClimbAgent(Agent):
    """Keeps the best specimen so far and changes one character at a time.

    This is pure optimization with no understanding. It is the comparison that
    makes a sandbox result interesting: an investigator that scores like this
    but cannot say why has not done science, it has done search.
    """

    name = "hillclimb"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
        self.best_specimen: Optional[str] = None
        self.best_score: Optional[float] = None

    def propose(self, round_index: int, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        alphabet, length = _facts(self)
        if self.best_specimen is None:
            specimen = "".join(self.rng.choice(alphabet) for _ in range(length))
            return {"specimens": [specimen], "rationale": "starting point, chosen at random"}
        position = self.rng.randrange(length)
        replacement = self.rng.choice(alphabet)
        chars = list(self.best_specimen)
        chars[position] = replacement
        return {"specimens": ["".join(chars)],
                "rationale": "changed position %d to %s on the best specimen so far"
                             % (position, replacement)}

    def observe(self, round_index: int, report: Dict[str, Any],
                history: List[Dict[str, Any]]) -> Optional[str]:
        scores = report.get("scores") or {}
        score = None
        for value in scores.values():
            score = float(value)
            break
        if score is None:
            return None
        submitted = history[-1]["specimens"][0]
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_specimen = submitted
            return "score %.4f beats the previous best; keeping this specimen." % score
        return "score %.4f does not beat %.4f; discarding the change." % (score, self.best_score)

    def conclude(self, history: List[Dict[str, Any]]) -> str:
        return ("No theory of the hidden rule. This investigator only kept whatever "
                "scored highest. Best score reached: %s." % self.best_score)
