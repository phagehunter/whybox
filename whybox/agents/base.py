"""The investigator interface."""

from typing import Any, Dict, List, Optional


class Agent(object):
    name = "agent"

    def begin(self, spec: Any, instructions: str, public_facts: Dict[str, Any],
              rounds: int) -> None:
        """Called once, before the first round."""
        self.spec = spec
        self.instructions = instructions
        self.facts = public_facts
        self.rounds = rounds

    def propose(self, round_index: int, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return the specimens to submit this round, and why."""
        raise NotImplementedError

    def observe(self, round_index: int, report: Dict[str, Any],
                history: List[Dict[str, Any]]) -> Optional[str]:
        """React to the report. Return notebook text, or nothing."""
        return None

    def conclude(self, history: List[Dict[str, Any]]) -> str:
        """State the final theory of how the hidden system works."""
        return ""
