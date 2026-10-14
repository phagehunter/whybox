/* whybox in the browser.

   The same world as the Python package: a sequence is read in groups, each
   group becomes one of two kinds of bead, the chain folds on a square grid,
   and the score counts how many sticky beads end up touching sticky beads.

   One honest warning, stated here and on the page itself. In a browser
   nothing is hidden. This file runs on your own machine and you can read it,
   which means the rule below is one keystroke away in developer tools. That
   is a property of browsers, not a flaw we overlooked. What the page protects
   instead is the thing that actually matters for an experiment: the rule
   cannot change while you play, and you cannot decide afterwards that you had
   it all along. The hash shown before your first test is what makes that
   checkable.

   This file is cross-checked against the Python version by a test in
   tests/test_browser_matches_python.py, so the two cannot drift apart
   silently. */

(function (root) {
  "use strict";

  var ALPHABET = "ACGT";
  var CODON_LENGTH = 2;
  var N_BEADS = 12;
  var SEQUENCE_LENGTH = N_BEADS * CODON_LENGTH;

  /* ---- the hidden rule ------------------------------------------------ */

  function translate(codon) {
    // The first character is ignored entirely. Only the second decides.
    return "AG".indexOf(codon.charAt(1)) >= 0 ? "H" : "P";
  }

  function toChain(sequence) {
    var chain = "";
    for (var i = 0; i + CODON_LENGTH <= sequence.length; i += CODON_LENGTH) {
      chain += translate(sequence.substr(i, CODON_LENGTH));
    }
    return chain;
  }

  var RULE_TEXT =
    "Read the sequence in non-overlapping groups of 2. Ignore the first " +
    "character of each group. The second character decides the bead: A or G " +
    "gives a sticky bead, C or T gives a non-sticky bead. Fold the chain of " +
    "beads on a square grid and count how many sticky beads touch other " +
    "sticky beads in the best possible fold.";

  var KEY_CLAIMS = [
    { claim: "read in groups of two",
      synonyms: ["groups of 2", "pairs of characters", "codon length 2",
                 "every two characters", "2-character", "in pairs",
                 "two at a time", "pairs of letters", "two letters",
                 "every two letters", "chunks of two", "blocks of two",
                 "two by two"] },
    { claim: "first position is silent",
      synonyms: ["first character is ignored", "position 1 does not matter",
                 "silent position", "odd positions do not matter",
                 "first one does not matter", "first letter does not matter",
                 "first letter is ignored", "only the second",
                 "second character decides", "second letter decides",
                 "every second letter", "every other letter",
                 "every other character", "the one before it is ignored",
                 "first is irrelevant", "first does not matter"] },
    { claim: "A or G gives a sticky bead",
      synonyms: ["a and g are h", "purines are h", "a g maps to h", "a or g",
                 "a and g", "purine", "a or g is sticky", "a and g are sticky",
                 "a or g are good"] },
    { claim: "score counts touching sticky pairs",
      synonyms: ["h h contacts", "hydrophobic contacts", "folding", "folds",
                 "fold", "number of contacts in the best fold", "touching pairs",
                 "sticky beads touching", "contacts", "touching", "adjacent",
                 "neighbours", "neighbors"] }
  ];

  /* ---- the folding physics -------------------------------------------- */

  var contactSets = null;

  function buildContactSets(nBeads) {
    // Every way to lay a chain of nBeads on graph paper without overlapping.
    // The first step is fixed to the right: rotating a layout cannot change
    // how many beads touch, so fixing it cuts the work by four for free.
    var walks = [];
    var path = [[0, 0], [1, 0]];
    var used = { "0,0": true, "1,0": true };
    var steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    function extend() {
      if (path.length === nBeads) {
        walks.push(path.slice());
        return;
      }
      var last = path[path.length - 1];
      for (var s = 0; s < steps.length; s++) {
        var x = last[0] + steps[s][0];
        var y = last[1] + steps[s][1];
        var key = x + "," + y;
        if (used[key]) continue;
        used[key] = true;
        path.push([x, y]);
        extend();
        path.pop();
        delete used[key];
      }
    }
    extend();

    var sets = [];
    for (var w = 0; w < walks.length; w++) {
      var walk = walks[w];
      var indexOf = {};
      for (var i = 0; i < walk.length; i++) {
        indexOf[walk[i][0] + "," + walk[i][1]] = i;
      }
      var pairs = [];
      var seen = {};
      for (i = 0; i < walk.length; i++) {
        var neighbors = [[walk[i][0] + 1, walk[i][1]], [walk[i][0], walk[i][1] + 1]];
        for (var n = 0; n < neighbors.length; n++) {
          var j = indexOf[neighbors[n][0] + "," + neighbors[n][1]];
          if (j === undefined) continue;
          if (Math.abs(i - j) <= 2) continue;
          var lo = Math.min(i, j), hi = Math.max(i, j);
          var pairKey = lo + ":" + hi;
          if (seen[pairKey]) continue;
          seen[pairKey] = true;
          pairs.push([lo, hi]);
        }
        seen = seen;
      }
      // Layouts with no contacts can never be the best fold.
      if (pairs.length) sets.push(pairs);
    }
    return sets;
  }

  function bestFoldScore(chain) {
    if (chain.indexOf("H") < 0) return 0;
    if (!contactSets) contactSets = buildContactSets(chain.length);
    var sticky = [];
    for (var i = 0; i < chain.length; i++) sticky.push(chain.charAt(i) === "H");
    var best = 0;
    for (var s = 0; s < contactSets.length; s++) {
      var pairs = contactSets[s];
      var total = 0;
      for (var p = 0; p < pairs.length; p++) {
        if (sticky[pairs[p][0]] && sticky[pairs[p][1]]) total++;
      }
      if (total > best) best = total;
    }
    return best;
  }

  function ceiling() {
    var allSticky = "";
    for (var i = 0; i < N_BEADS; i++) allSticky += "H";
    return bestFoldScore(allSticky);
  }

  /* ---- the public interface ------------------------------------------- */

  function validate(sequence) {
    if (sequence.length !== SEQUENCE_LENGTH) {
      return "A sequence must be exactly " + SEQUENCE_LENGTH +
             " characters. That one has " + sequence.length + ".";
    }
    for (var i = 0; i < sequence.length; i++) {
      if (ALPHABET.indexOf(sequence.charAt(i)) < 0) {
        return "This world only uses the characters A, C, G and T. " +
               "Yours contains " + sequence.charAt(i) + ".";
      }
    }
    return null;
  }

  function measure(sequence) {
    return bestFoldScore(toChain(sequence));
  }

  function randomSequence(rng) {
    var pick = rng || Math.random;
    var out = "";
    for (var i = 0; i < SEQUENCE_LENGTH; i++) {
      out += ALPHABET.charAt(Math.floor(pick() * ALPHABET.length));
    }
    return out;
  }

  function normalize(text) {
    return text.toLowerCase().replace(/[^a-z0-9 ]+/g, " ");
  }

  function gradeStatedRule(statement) {
    // The same shallow word matching the Python grader uses, with the same
    // weakness: a sentence containing these phrases and nothing else scores
    // full marks. The page says so rather than hiding it.
    var haystack = normalize(statement);
    var detail = [];
    var found = 0;
    for (var c = 0; c < KEY_CLAIMS.length; c++) {
      var claim = KEY_CLAIMS[c];
      var needles = [claim.claim].concat(claim.synonyms);
      var hit = false;
      for (var n = 0; n < needles.length; n++) {
        if (needles[n] && haystack.indexOf(normalize(needles[n])) >= 0) {
          hit = true;
          break;
        }
      }
      if (hit) found++;
      detail.push({ claim: claim.claim, found: hit });
    }
    return { found: found, total: KEY_CLAIMS.length, detail: detail };
  }

  var api = {
    ALPHABET: ALPHABET,
    SEQUENCE_LENGTH: SEQUENCE_LENGTH,
    N_BEADS: N_BEADS,
    RULE_TEXT: RULE_TEXT,
    KEY_CLAIMS: KEY_CLAIMS,
    toChain: toChain,
    measure: measure,
    validate: validate,
    ceiling: ceiling,
    randomSequence: randomSequence,
    gradeStatedRule: gradeStatedRule
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.whybox = api;
  }
})(typeof self !== "undefined" ? self : this);
