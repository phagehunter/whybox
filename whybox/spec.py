"""Reading a sandbox.yaml file.

Every sandbox folder has a sandbox.yaml that describes the sandbox in plain
terms: what a specimen looks like, what the report contains, and how many
rounds an investigator gets. The file is the contract. A person reading it
should understand what they are signing up for without opening any code.

We parse a deliberately small subset of YAML by hand so that the toolkit runs
with no third-party packages installed. Keys are `key: value`, lists are
`- item`, and nesting is two spaces. That is all a sandbox.yaml may use.
"""

import os
import re
from typing import Any, Dict, List, Optional


class SpecError(Exception):
    """The sandbox.yaml is missing something or says something impossible."""


def _coerce(text: str) -> Any:
    """Turn a bare YAML scalar into a Python value."""
    t = text.strip()
    if len(t) >= 2 and t[0] in "\"'" and t[-1] == t[0]:
        return t[1:-1]
    low = t.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "none", "~", ""):
        return None
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        pass
    return t


def _strip_comment(line: str) -> str:
    """Remove a trailing `# comment`, leaving quoted text alone."""
    if line.lstrip().startswith("#"):
        return ""
    cut = line.find(" #")
    return line[:cut] if cut >= 0 else line


def _meaningful_lines(text: str) -> List[Any]:
    """(indent, body) for each line that carries content."""
    out: List[Any] = []
    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        out.append((indent, line.strip()))
    return out


def _parse_block(lines: List[Any], index: int, indent: int) -> Any:
    """Read every line at `indent` into one dict or one list.

    Returns (value, index_of_first_line_that_does_not_belong).
    """
    if index < len(lines) and lines[index][1].startswith("- "):
        items: List[Any] = []
        while index < len(lines) and lines[index][0] == indent \
                and lines[index][1].startswith("- "):
            items.append(_coerce(lines[index][1][2:]))
            index += 1
        return items, index

    mapping: Dict[str, Any] = {}
    while index < len(lines) and lines[index][0] == indent:
        body = lines[index][1]
        if body.startswith("- "):
            break
        if ":" not in body:
            raise SpecError("line is neither a list item nor a key: %r" % body)
        key, _, value = body.partition(":")
        key, value = key.strip(), value.strip()
        index += 1
        if value == "":
            if index < len(lines) and lines[index][0] > indent:
                child, index = _parse_block(lines, index, lines[index][0])
                mapping[key] = child
            else:
                mapping[key] = None
        else:
            mapping[key] = _coerce(value)
    return mapping, index


def _parse_mini_yaml(text: str) -> Dict[str, Any]:
    """Parse the small YAML subset described in this module's docstring."""
    lines = _meaningful_lines(text)
    if not lines:
        return {}
    data, consumed = _parse_block(lines, 0, lines[0][0])
    if consumed != len(lines):
        raise SpecError("could not read line %d: %r"
                        % (consumed + 1, lines[consumed][1]))
    if not isinstance(data, dict):
        raise SpecError("the top level of sandbox.yaml must be key: value pairs")
    return data


class SandboxSpec(object):
    """Everything whybox needs to know about one sandbox."""

    def __init__(self, directory: str, data: Dict[str, Any]):
        self.directory = os.path.abspath(directory)
        self.data = data

        self.name = self._need("name")
        self.title = data.get("title", self.name)
        # Two parts, like 1-A. The NUMBER goes up when results stop being
        # comparable: the hidden rule changed, the report changed, the round
        # budget changed, or a bug fix moved the scores. The LETTER goes up
        # when only the interface changed, such as a renamed setting. Neither
        # ever resets. The distinction matters because "your old score is now
        # meaningless" and "your old command no longer runs" are different
        # emergencies, and a single version number cannot say which happened.
        self.version = str(data.get("version", "1-A"))
        match = re.match(r"^(\d+)-([A-Z]+)$", self.version)
        if not match:
            raise SpecError(
                "version must look like 1-A: a number for result-breaking "
                "changes and a letter for interface changes. Got %r. A version "
                "like 0.1.0 cannot say which kind of change happened."
                % self.version)
        self.version_results = int(match.group(1))
        self.version_interface = match.group(2)
        self.summary = data.get("summary", "")

        # wet  = a real physical experiment
        # damp = a computer model trained on real measurements
        # dry  = a rule the sandbox author invented
        self.oracle_kind = data.get("oracle_kind", "dry")
        if self.oracle_kind not in ("wet", "damp", "dry"):
            raise SpecError("oracle_kind must be wet, damp, or dry")

        self.oracle_module = data.get("oracle_module", "oracle")
        self.oracle_class = data.get("oracle_class", "SandboxOracle")

        self.rounds = int(data.get("rounds", 30))
        self.specimens_per_round = int(data.get("specimens_per_round", 1))
        self.instructions_file = data.get("instructions_file", "instructions.md")
        self.report_fields = data.get("report_fields", []) or []
        self.sealed_paths = data.get("sealed_paths", []) or ["sealed"]
        self.tags = data.get("tags", []) or []

    def _need(self, key: str) -> Any:
        if key not in self.data:
            raise SpecError("sandbox.yaml is missing required key %r" % key)
        return self.data[key]

    def instructions_path(self) -> str:
        return os.path.join(self.directory, self.instructions_file)

    def read_instructions(self) -> str:
        path = self.instructions_path()
        if not os.path.isfile(path):
            return ""
        with open(path) as handle:
            return handle.read()

    def __repr__(self) -> str:
        return "<SandboxSpec %s v%s (%s oracle)>" % (self.name, self.version, self.oracle_kind)


def load_spec(directory: str) -> SandboxSpec:
    """Read `directory/sandbox.yaml` and return a SandboxSpec."""
    path = os.path.join(directory, "sandbox.yaml")
    if not os.path.isfile(path):
        raise SpecError("no sandbox.yaml in %s" % directory)
    with open(path) as handle:
        text = handle.read()
    data = _parse_mini_yaml(text)
    return SandboxSpec(directory, data)
