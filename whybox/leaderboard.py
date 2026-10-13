"""Turning a finished run into one comparable row.

A leaderboard for science sandboxes cannot be a single ranked column, because
the framework exists to say that one number hides the interesting part. Every
row therefore carries two results side by side and never a combination of
them:

    score    how high it got
    insight  how much of the hidden rule it actually stated

A row also carries the sandbox version, because a score from before the hidden
rule changed is not comparable to one from after. That is the rule that keeps
a leaderboard honest over time, and it is the one most likely to be forgotten.

SCAFFOLD: this produces and validates rows and appends them to a local file.
There is no server, no submission path, and no moderation. What a published
leaderboard needs beyond this is in docs/leaderboard.md.
"""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from whybox.judge import judge_run
from whybox.record import human_time, load_run

SCHEMA_VERSION = 1

REQUIRED_FIELDS = (
    "schema", "sandbox", "sandbox_version", "oracle_kind", "agent",
    "rounds_used", "best_score", "claims_found", "claims_total",
    "run_fingerprint", "submitted", "status", "n_runs", "selection_rule",
    "insight_graded_by", "toolkit_version",
)

#: A row scoring at or below this fraction of the sandbox ceiling is not
#: ranked by understanding at all. Without a floor, an investigator that runs
#: no experiment and writes a confident notebook tops a board sorted on
#: understanding. The number is deliberately low: this is a floor, not a bar.
MIN_SCORE_FRACTION_FOR_RANKING = 0.25


def _fingerprint(folder: str) -> str:
    """A short hash over the parts of a run that must not change after the fact.

    Not security. It means a resubmitted row can be checked against the run it
    claims to describe, and that an edited notebook shows up as a different
    run rather than a quietly improved one.
    """
    digest = hashlib.sha256()
    for name in ("rounds.jsonl", "notebook.md", "run.json"):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            with open(path, "rb") as handle:
                digest.update(handle.read())
    return digest.hexdigest()[:16]


def row_from_run(folder: str, sandbox_root: str = "sandboxes") -> Dict[str, Any]:
    run = load_run(folder)
    summary = run.get("summary") or {}
    if not summary:
        raise ValueError("%s has no run.json; it is not a finished run" % folder)

    verdict = run.get("judge") or judge_run(folder, write=False,
                                            sandbox_root=sandbox_root)
    insight = verdict.get("insight") or {}
    metadata = summary.get("metadata") or {}

    return {
        "schema": SCHEMA_VERSION,
        "sandbox": summary.get("sandbox"),
        "sandbox_version": metadata.get("sandbox_version"),
        "oracle_kind": metadata.get("oracle_kind"),
        "agent": summary.get("agent"),
        "rounds_used": summary.get("rounds_used"),

        # How many times this was run, and how the reported number was picked.
        # A best-of-twenty result and a single run are different claims, and a
        # board that cannot tell them apart rewards whoever ran it most.
        "n_runs": 1,
        "selection_rule": "single run",
        "best_score": summary.get("best_score"),

        "claims_found": insight.get("claims_found"),
        "claims_total": insight.get("claims_total"),
        # "rubric" means word matching, which an audit can fully satisfy with
        # no experiments at all. "model" and "human" mean something stronger.
        # These are not interchangeable and a table must not mix them silently.
        "insight_graded_by": "rubric",
        "grader_version": None,

        # So a reader can go and disbelieve this row.
        "status": "unverified",
        "submitter": None,
        "artifact_url": None,
        "human_in_loop": None,
        "contamination_declaration": None,

        "rule_commitment_sha256": metadata.get("rule_commitment_sha256"),
        "run_fingerprint": _fingerprint(folder),
        "toolkit_version": __import__("whybox").__version__,
        "submitted": human_time(),
    }


def validate_row(row: Dict[str, Any]) -> List[str]:
    """Return the reasons this row cannot go on a leaderboard."""
    problems: List[str] = []
    for field in REQUIRED_FIELDS:
        if row.get(field) in (None, ""):
            problems.append("missing %s" % field)
    if row.get("status") not in (None, "unverified", "reproduced", "flagged"):
        problems.append("status must be unverified, reproduced, or flagged")
    if row.get("insight_graded_by") not in (None, "rubric", "model", "human"):
        problems.append("insight_graded_by must be rubric, model, or human")
    if row.get("schema") != SCHEMA_VERSION:
        problems.append("row uses schema %s, this toolkit writes %s"
                        % (row.get("schema"), SCHEMA_VERSION))
    if not row.get("sandbox_version"):
        problems.append("no sandbox version, so this score cannot be compared "
                        "with any other")
    return problems


def append_row(row: Dict[str, Any], path: str) -> None:
    problems = validate_row(row)
    if problems:
        raise ValueError("this row cannot be published:\n  - %s"
                         % "\n  - ".join(problems))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a") as handle:
        handle.write(json.dumps(row) + "\n")


def read_table(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def is_rankable(row: Dict[str, Any], ceiling: Optional[float] = None) -> bool:
    """Has this row earned the right to be ranked by understanding?

    Sorting on understanding puts the softest measurement in the system in the
    rank position, which invites a confident notebook backed by no work. A row
    must clear a low score floor before its understanding counts.
    """
    score = row.get("best_score")
    if score is None:
        return False
    if ceiling:
        return float(score) >= MIN_SCORE_FRACTION_FOR_RANKING * float(ceiling)
    return float(score) > 0


def sort_key(row: Dict[str, Any]):
    """The published tie-break, in order.

    Written down because an undefined secondary sort quietly becomes the real
    ranking, and anything that ranks will eventually be gamed.
    """
    found = row.get("claims_found") or 0
    total = row.get("claims_total") or 1
    strength = {"human": 2, "model": 1, "rubric": 0}.get(
        row.get("insight_graded_by"), 0)
    verified = 1 if row.get("status") == "reproduced" else 0
    return (
        found / total,                      # 1. understanding, as a fraction
        verified,                           # 2. reproduced beats unverified
        strength,                           # 3. a human grade beats word matching
        float(row.get("best_score") or 0),  # 4. then score
        -int(row.get("rounds_used") or 0),  # 5. then fewer rounds used
    )


def render_table(rows: List[Dict[str, Any]], ceiling: Optional[float] = None) -> str:
    """A plain text table, grouped by sandbox version.

    Rows from different versions are never interleaved, because a score from
    before the hidden rule changed cannot be compared with one from after.
    """
    if not rows:
        return "(no results yet)"

    # Grouped by the version NUMBER, not the whole version. A letter bump
    # means the interface changed and the scores did not, so splitting 1-A
    # from 1-B would be the opposite of what the version is saying.
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        version = str(row.get("sandbox_version", "?"))
        number = version.split("-")[0]
        key = "%s, results version %s" % (row.get("sandbox", "?"), number)
        groups.setdefault(key, []).append(row)

    header = "%-12s %-10s %7s %9s %-12s %s" % (
        "investigator", "runs", "score", "insight", "graded by", "status")
    lines: List[str] = []
    for key in sorted(groups):
        lines.append("")
        lines.append("%s" % key)
        lines.append(header)
        lines.append("-" * len(header))
        ranked = sorted(groups[key], key=sort_key, reverse=True)
        for row in ranked:
            mark = "" if is_rankable(row, ceiling) else "  (unranked: score floor)"
            lines.append("%-12s %-10s %7s %6s/%-2s %-12s %s%s" % (
                row.get("agent", "?"),
                "%s, %s" % (row.get("n_runs", "?"), row.get("selection_rule", "?")),
                row.get("best_score", "?"),
                row.get("claims_found", "?"), row.get("claims_total", "?"),
                row.get("insight_graded_by", "?"),
                row.get("status", "?"), mark))
    lines.append("")
    lines.append("Sorted by understanding, then reproduced over unverified, then "
                 "grade strength, then score, then fewer rounds used.")
    lines.append("A high score beside a low understanding column is the result "
                 "this framework exists to show.")
    return "\n".join(lines)
