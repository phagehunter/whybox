"""The genetic half of this world: how a sequence becomes a chain of beads.

HIDDEN. The investigator is never told any of this. It is not told that the
sequence is read in fixed-size groups, that the groups map to two kinds of
bead, or that any position inside a group is ignored.

Each world below is one invented set of genetic rules. The physics in
folding.py stays the same across all of them, so a difference in what an
investigator discovers is a difference in the genetics, not the chemistry.

Adding a world is the main way to extend this sandbox. A world is three
things: an alphabet, how many characters make one group, and a function from
a group to H or P.
"""

from typing import Callable, Dict, List

ALPHABET = "ACGT"


def _single_position(codon: str) -> str:
    """Only the second character counts. The first is along for the ride.

    Why this is interesting: an investigator that changes one character at a
    time will see half its changes do nothing at all. The honest conclusion
    is that a position is silent. The tempting wrong conclusion is that the
    machine is noisy.
    """
    return "H" if codon[1] in "AG" else "P"


def _paired(codon: str) -> str:
    """The two characters only mean something together.

    H when both characters fall in the same family, A/G or C/T. Neither
    character predicts the result on its own, so an investigator that insists
    on per-character effects will build a theory that keeps breaking.
    """
    first_family = codon[0] in "AG"
    second_family = codon[1] in "AG"
    return "H" if first_family == second_family else "P"


class World(object):
    def __init__(self, name: str, alphabet: str, codon_length: int,
                 translate: Callable[[str], str], plain_english: str,
                 key_claims: List[Dict[str, object]]):
        self.name = name
        self.alphabet = alphabet
        self.codon_length = codon_length
        self.translate = translate
        self.plain_english = plain_english
        self.key_claims = key_claims

    def to_chain(self, sequence: str) -> str:
        step = self.codon_length
        return "".join(self.translate(sequence[i:i + step])
                       for i in range(0, len(sequence) - step + 1, step))

    def table(self) -> Dict[str, str]:
        """The full lookup table, for the answer key only."""
        from itertools import product
        return {"".join(combo): self.translate("".join(combo))
                for combo in product(self.alphabet, repeat=self.codon_length)}


WORLDS: Dict[str, World] = {
    "single-position": World(
        name="single-position",
        alphabet=ALPHABET,
        codon_length=2,
        translate=_single_position,
        plain_english=(
            "The sequence is read in non-overlapping groups of 2 characters. "
            "Inside each group the FIRST character is ignored entirely. The "
            "second character decides the bead: A or G gives a sticky (H) bead, "
            "C or T gives a non-sticky (P) bead. The chain of beads is then "
            "folded on a square grid, and the score is the number of sticky "
            "beads touching other sticky beads in the best possible fold."),
        key_claims=[
            {"claim": "read in groups of two",
             "synonyms": ["groups of 2", "pairs of characters", "codon length 2",
                          "every two characters", "2-character"]},
            {"claim": "first position is silent",
             "synonyms": ["first character is ignored", "position 1 does not matter",
                          "odd positions do not matter", "silent position"]},
            {"claim": "A or G gives a sticky bead",
             "synonyms": ["A and G are H", "purines are H", "A/G maps to H"]},
            {"claim": "score counts touching sticky pairs",
             "synonyms": ["H-H contacts", "hydrophobic contacts", "folding",
                          "number of contacts in the best fold"]},
        ]),
    "paired": World(
        name="paired",
        alphabet=ALPHABET,
        codon_length=2,
        translate=_paired,
        plain_english=(
            "The sequence is read in non-overlapping groups of 2 characters. "
            "Neither character decides the bead by itself. The group gives a "
            "sticky (H) bead when both characters are in the same family, "
            "A/G or C/T, and a non-sticky (P) bead when they are in different "
            "families. The chain is folded as in every world here, and the "
            "score is the number of sticky beads touching sticky beads."),
        key_claims=[
            {"claim": "read in groups of two",
             "synonyms": ["groups of 2", "pairs of characters", "codon length 2"]},
            {"claim": "the two characters interact",
             "synonyms": ["depends on the combination", "not additive",
                          "neither character alone", "joint effect", "interaction"]},
            {"claim": "same family gives a sticky bead",
             "synonyms": ["both purines or both pyrimidines", "AG or CT together",
                          "matching pair is H"]},
            {"claim": "score counts touching sticky pairs",
             "synonyms": ["H-H contacts", "hydrophobic contacts", "folding"]},
        ]),
}
