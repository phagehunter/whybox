"""The physics half of this world: how a chain folds, and how good the fold is.

This is a very old toy model of protein folding. A protein is simplified to a
string of two kinds of beads: H beads, which avoid water, and P beads, which
do not mind it. The chain is laid out on graph paper, one bead per square,
each bead next to the one before it, never doubling back onto a square it has
already used. Out of every possible layout, the chain settles into the one
with the most H beads sitting next to other H beads. The number of those
touching H pairs is the fitness.

The physics is identical in every world in this sandbox family. Only the
genetic half changes, which is what makes the worlds comparable.
"""

from typing import Dict, List, Tuple

Point = Tuple[int, int]
_CACHE: Dict[int, List[Tuple[Tuple[int, int], ...]]] = {}


def _self_avoiding_walks(n_beads: int) -> List[List[Point]]:
    """Every way to lay a chain of n_beads on graph paper without overlap.

    The first step is fixed to the right. Rotating the whole layout cannot
    change how many H beads touch, so fixing it cuts the work by four with no
    effect on the answer.
    """
    start: Point = (0, 0)
    second: Point = (1, 0)
    walks: List[List[Point]] = []
    path: List[Point] = [start, second]
    used = {start, second}

    def extend() -> None:
        if len(path) == n_beads:
            walks.append(list(path))
            return
        x, y = path[-1]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (x + dx, y + dy)
            if step in used:
                continue
            used.add(step)
            path.append(step)
            extend()
            path.pop()
            used.remove(step)

    extend()
    return walks


def contact_sets(n_beads: int) -> List[Tuple[Tuple[int, int], ...]]:
    """For each layout, which pairs of beads end up touching.

    Only pairs that are not neighbors along the chain count, because beads
    that are already joined are always touching and tell you nothing.
    """
    if n_beads in _CACHE:
        return _CACHE[n_beads]
    out: List[Tuple[Tuple[int, int], ...]] = []
    for walk in _self_avoiding_walks(n_beads):
        index_of = {point: i for i, point in enumerate(walk)}
        pairs: List[Tuple[int, int]] = []
        for i, (x, y) in enumerate(walk):
            for dx, dy in ((1, 0), (0, 1)):
                j = index_of.get((x + dx, y + dy))
                if j is not None and abs(i - j) > 2:
                    pairs.append((min(i, j), max(i, j)))
        out.append(tuple(sorted(set(pairs))))
    # Layouts with no contacts can never be the best fold, so drop them.
    out = [pairs for pairs in out if pairs]
    _CACHE[n_beads] = out
    return out


def best_fold_score(chain: str) -> int:
    """How many touching H-H pairs the best layout of this chain achieves."""
    n = len(chain)
    hydrophobic = [c == "H" for c in chain]
    if not any(hydrophobic):
        return 0
    best = 0
    for pairs in contact_sets(n):
        total = 0
        for i, j in pairs:
            if hydrophobic[i] and hydrophobic[j]:
                total += 1
        if total > best:
            best = total
    return best


def ceiling(n_beads: int) -> int:
    """The highest score any chain of this length could possibly reach."""
    return best_fold_score("H" * n_beads)
