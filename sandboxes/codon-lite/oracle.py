"""codon-lite: a small invented world with a hidden genetic code.

The investigator submits one sequence of characters and gets back one number.
Nothing else. It is not told what the characters mean, how they are grouped,
or what the number counts.

Underneath, the number is produced in two steps. A hidden rule turns the
sequence into a chain of two kinds of bead, and a fixed physical model folds
that chain and counts how many sticky beads end up touching. Both steps are
in `sealed/`, which the investigator never gets to see.

This is a DRY oracle: the rule was invented, not measured. That is a trade.
There is no biology in it, so nothing it finds is a discovery about nature.
In exchange, the sandbox author knows the exact right answer, which means an
investigator's claims can be graded rather than argued about.
"""

from typing import Any, Dict, List

from whybox.oracle import Oracle, Report, ValidationError, canary_block
from sealed.folding import best_fold_score, ceiling
from sealed.rules import WORLDS


class SandboxOracle(Oracle):
    kind = "dry"

    def __init__(self, directory: str, config: Dict[str, Any] = None):
        Oracle.__init__(self, directory, config)
        world_name = self.config.get("world", "single-position")
        if world_name not in WORLDS:
            raise ValueError("unknown world %r; available: %s"
                             % (world_name, ", ".join(sorted(WORLDS))))
        self.world = WORLDS[world_name]
        self.n_beads = int(self.config.get("n_beads", 12))
        self.length = self.n_beads * self.world.codon_length
        self.queries = 0

    # --- what the investigator is allowed to know ------------------------

    def describe(self) -> Dict[str, Any]:
        return {
            "alphabet": self.world.alphabet,
            "specimen_length": self.length,
            "specimens_per_round": 1,
            "report_fields": ["fitness"],
            "note": ("Submit one sequence of exactly %d characters from %s. "
                     "You will get back a single number. Higher is better. "
                     "Nothing else about this world is given to you."
                     % (self.length, "/".join(self.world.alphabet))),
        }

    def validate(self, specimen: Any) -> None:
        if not isinstance(specimen, str):
            raise ValidationError("a specimen must be a string of characters")
        if len(specimen) != self.length:
            raise ValidationError("a specimen must be exactly %d characters, got %d"
                                  % (self.length, len(specimen)))
        bad = sorted(set(specimen) - set(self.world.alphabet))
        if bad:
            raise ValidationError("characters not allowed in this world: %s"
                                  % ", ".join(bad))

    def measure(self, specimens: List[Any]) -> Report:
        if len(specimens) != 1:
            raise ValidationError("this world measures exactly one sequence per round")
        chain = self.world.to_chain(specimens[0])
        self.queries += 1
        return Report(scores={"fitness": float(best_fold_score(chain))})

    # --- for reviewers and the judge only --------------------------------

    def answer_key(self) -> Dict[str, Any]:
        return {
            "canary": canary_block(),
            "world": self.world.name,
            "rule": self.world.plain_english,
            "key_claims": self.world.key_claims,
            "codon_length": self.world.codon_length,
            "alphabet": self.world.alphabet,
            "n_beads": self.n_beads,
            "max_possible_fitness": ceiling(self.n_beads),
            "lookup_table": self.world.table(),
            "how_to_read_this": (
                "Compare these claims against the investigator's notebook. Reaching "
                "the maximum fitness is easy here: any sequence whose groups all map "
                "to sticky beads hits the ceiling, and random trial will find one "
                "within a few rounds. A high score therefore proves almost nothing. "
                "The question is whether the notebook states the grouping, the silent "
                "or interacting positions, and what the number counts."),
        }
