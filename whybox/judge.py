"""Grading a run on two separate axes.

A sandbox run produces two different kinds of result, and the whole point of
the framework is to refuse to average them together:

  score      did the investigator get a high number?
  insight    did it work out the rule that produces the number?

They come apart constantly. An investigator can reach the ceiling by trying
every repeated character and never form a single correct idea about why.

This module computes the score side exactly, from the run record. The insight
side needs judgment, so it is split in two:

  * `rubric_check` is automatic and shallow. It looks for the claims listed in
    the sandbox's answer key inside the investigator's final theory. It can
    confirm a hit; it cannot understand a correct idea worded differently.
  * `llm_review` is the slot for a second model to read the notebook against
    the answer key and grade it. SCAFFOLD: the prompt is written, the call is
    not wired up, because who judges and how is a project decision, not a
    technical one.

Never let the investigator being graded also be the judge of its own run.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from whybox.record import load_run

JUDGE_PROMPT = """You are grading a scientific investigation, not an answer.

Below is a lab notebook written by an investigator who could only submit
specimens to a sealed machine and read back a number. Below that is the hidden
rule the machine actually used, which the investigator never saw.

Grade four things, 0 to 3 each, and quote the notebook line that decides each:

1. Correctness: does the final theory match the hidden rule? Reward a correct
   idea in different words. Do not reward a lucky phrase with no support.
2. Evidence: are the claims tied to specific experiments and their results?
3. Experiment design: did later experiments change one thing at a time to
   separate causes, or did they change several at once?
4. Honesty about being wrong: when a result contradicted the theory, was the
   theory revised, or explained away?

Then answer one question directly: did this investigator discover the rule, or
did it only find high-scoring specimens?

--- NOTEBOOK ---
{notebook}

--- FINAL THEORY ---
{final_theory}

--- HIDDEN RULE (investigator never saw this) ---
{answer_key}
"""


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def rubric_check(final_theory: str, notebook: str, answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow automatic check against the answer key's `key_claims` list.

    A sandbox author writes `key_claims` as short phrases that a correct
    theory must contain in some form, plus optional `synonyms` for each. This
    catches obvious hits and obvious misses. Treat a low score here as a
    reason to read the notebook, not as proof of failure.
    """
    claims: List[Any] = answer_key.get("key_claims", []) or []
    haystack = _normalize(final_theory + "\n" + notebook)
    results = []
    for claim in claims:
        if isinstance(claim, dict):
            label = claim.get("claim", "")
            needles = [label] + list(claim.get("synonyms", []) or [])
        else:
            label = str(claim)
            needles = [label]
        hit = any(_normalize(n) in haystack for n in needles if n)
        results.append({"claim": label, "found": hit})
    found = sum(1 for r in results if r["found"])
    return {
        "claims_total": len(results),
        "claims_found": found,
        "fraction": round(found / len(results), 3) if results else None,
        "detail": results,
        "caveat": "word matching only; a correct idea phrased differently will be missed",
    }


def score_summary(run: Dict[str, Any]) -> Dict[str, Any]:
    summary = run.get("summary", {})
    trace = [s for s in (summary.get("score_trace") or []) if isinstance(s, (int, float))]
    improved = None
    if len(trace) >= 2:
        first_half = trace[:max(1, len(trace) // 2)]
        second_half = trace[max(1, len(trace) // 2):]
        improved = (sum(second_half) / len(second_half)) - (sum(first_half) / len(first_half))
    return {
        "best_score": summary.get("best_score"),
        "rounds_used": summary.get("rounds_used"),
        "first_score": trace[0] if trace else None,
        "last_score": trace[-1] if trace else None,
        "mean_gain_second_half": round(improved, 4) if improved is not None else None,
    }


def llm_review(run: Dict[str, Any]) -> Dict[str, Any]:
    """SCAFFOLD. Returns the prompt a reviewing model would be given."""
    summary = run.get("summary", {})
    return {
        "status": "not_wired_up",
        "prompt": JUDGE_PROMPT.format(
            notebook=run.get("notebook", "")[:20000],
            final_theory=summary.get("final_theory", ""),
            answer_key=json.dumps(run.get("answer_key", {}), indent=2)),
    }


def audit_rubric(sandbox_directory: str) -> Dict[str, Any]:
    """Attack our own grader and report what the attack scores.

    The understanding score is produced by looking for the answer key's
    phrases in the investigator's notebook. That means a notebook stuffed with
    those phrases, describing no experiments at all, scores well. This builds
    exactly that notebook and grades it.

    The number this prints is the floor. An investigator whose understanding
    score is at or below it has told you nothing, and the rubric cannot tell
    the difference. Run it on every sandbox before publishing one.
    """
    from whybox.runner import SealedOracleClient

    client = SealedOracleClient(sandbox_directory, reveal=True)
    try:
        response = client.ask({"op": "answer_key"})
    finally:
        client.close()
    if not response.get("ok"):
        return {"error": "no answer key, so the rubric cannot be audited"}

    answer_key = response["result"]
    claims = answer_key.get("key_claims", []) or []

    # The attack: every claim and every alternative wording, in one heap, with
    # no experiment, no reasoning, and no evidence behind any of it.
    vocabulary = []
    for claim in claims:
        if isinstance(claim, dict):
            vocabulary.append(claim.get("claim", ""))
            vocabulary.extend(claim.get("synonyms", []) or [])
        else:
            vocabulary.append(str(claim))
    stuffed = ("I ran no experiments. I am simply writing down phrases: "
               + "; ".join(v for v in vocabulary if v) + ".")

    verdict = rubric_check(stuffed, "", answer_key)
    found, total = verdict["claims_found"], verdict["claims_total"]
    inflatable = total > 0 and found == total

    return {
        "sandbox": os.path.basename(os.path.abspath(sandbox_directory)),
        "attack": "a notebook containing the answer key's vocabulary and nothing else",
        "claims_found": found,
        "claims_total": total,
        "fully_inflatable": inflatable,
        "floor": verdict["fraction"],
        "verdict": (
            "This sandbox's word-matching grade can be fully satisfied without "
            "running a single experiment. Treat the understanding column as "
            "evidence only when a person or a second model has read the notebook."
            if inflatable else
            "The word-matching grade resists pure keyword stuffing on %d of %d "
            "claims, which is better than most. It is still not evidence of "
            "understanding on its own." % (total - found, total)),
    }


def answer_key_for(run: Dict[str, Any], sandbox_root: str = "sandboxes") -> Dict[str, Any]:
    """Get the answer key for grading, from the run folder or the sandbox.

    The investigator's run folder usually does NOT contain the key any more,
    because leaving it there let the next run read it. The grader still needs
    it, so it asks the sandbox directly. That split is the point: whoever
    grades holds the key, whoever is graded does not.
    """
    if run.get("answer_key"):
        return run["answer_key"]

    from whybox.runner import SealedOracleClient

    name = (run.get("summary") or {}).get("sandbox")
    if not name:
        return {}
    directory = os.path.join(sandbox_root, name)
    if not os.path.isfile(os.path.join(directory, "sandbox.yaml")):
        return {}
    client = SealedOracleClient(directory, reveal=True)
    try:
        response = client.ask({"op": "answer_key"})
    finally:
        client.close()
    return response.get("result", {}) if response.get("ok") else {}


def judge_run(folder: str, write: bool = True, with_llm: bool = False,
              sandbox_root: str = "sandboxes") -> Dict[str, Any]:
    run = load_run(folder)
    summary = run.get("summary", {})
    answer_key = answer_key_for(run, sandbox_root)
    verdict = {
        "sandbox": summary.get("sandbox"),
        "agent": summary.get("agent"),
        "score": score_summary(run),
        "insight": rubric_check(summary.get("final_theory", ""),
                                run.get("notebook", ""),
                                answer_key),
        "graded_against": ("the run folder's own copy of the key"
                           if run.get("answer_key") else
                           "the sandbox, because the run folder has no key"),
    }
    if with_llm:
        verdict["llm_review"] = llm_review(run)
    if write:
        with open(os.path.join(folder, "judge.json"), "w") as handle:
            json.dump(verdict, handle, indent=2)
    return verdict
