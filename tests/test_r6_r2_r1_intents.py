"""Intent-routing enforcement tests for the R6-R2-R1 closure.

Executable (Node runtime) evaluation of the real dashboard source's
parseIntent(): the nine canonical catalogue questions must resolve to their
declared intents and equivalent free-form phrasings must keep their governed
meanings. Not a source-string assertion — runs the actual JS in a sandbox.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "app" / "dashboard-luna" / "js" / "dashboard.js"
NODE = shutil.which("node")

CATALOGUE = [
    ("Where should Phoenix prioritize cooling?", "priority"),
    ("Compare the three candidates.", "compare"),
    ("Why are these locations nearly tied?", "tie"),
    ("What was the weather that afternoon?", "weather"),
    ("Compare tree canopy.", "canopy"),
    ("Which candidates are near parks?", "parks"),
    ("Where did this evidence come from?", "evidence"),
    ("What can this analysis not tell me?", "unsupported"),
    ("Focus Candidate N.", "map"),
]

FREE_FORM = [
    ("show live data", "mode"),
    ("use live", "mode"),
    ("show replay", "mode"),
    ("Which trees would cool this area most?", "unsupported"),
    ("How many degrees would planting trees cool this street?", "unsupported"),
    ("Which tree cover do the top candidates have?", "canopy"),
    ("Are any candidates in mapped parks?", "parks"),
    ("Show candidate 2", "map"),
    ("Focus the map", "map"),
    ("Which hotspot is named by the evidence chain?", "evidence"),
    ("How close is the ranking?", "tie"),
    ("Compare the candidate values", "compare"),
    ("Which area has the hottest measured values?", "priority"),
]

RUNNER_TEMPLATE = """
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
const sandbox = {
  console,
  window: { addEventListener() {}, matchMedia: () => ({ matches: false }) },
  document: {},
  L: {},
};
vm.createContext(sandbox);
vm.runInContext(
  src + ';globalThis.__intentAnswer = Object.fromEntries(__QUESTIONS__.map((q) => [q, parseIntent(q).id]));',
  sandbox,
  { timeout: 5000 }
);
console.log(JSON.stringify(sandbox.__intentAnswer));
"""


def _routing(questions):
    assert NODE, "node unavailable — intent tests require a Node runtime"
    runner = RUNNER_TEMPLATE.replace("__QUESTIONS__", json.dumps(questions))
    completed = subprocess.run(
        [NODE, "-e", runner, str(JS)],
        capture_output=True, text=True, timeout=30, check=True)
    return json.loads(completed.stdout.strip().splitlines()[-1])


def test_catalogue_intent_routing():
    """Every canonical catalogue question reaches its declared intent."""
    routing = _routing([q for q, _ in CATALOGUE])
    for question, intent in CATALOGUE:
        assert routing[question] == intent, f"{question} -> {routing[question]}, expected {intent}"


def test_freeform_intent_preservation():
    """Equivalent free-form wording keeps its governed intent meaning."""
    routing = _routing([q for q, _ in FREE_FORM])
    for question, intent in FREE_FORM:
        assert routing[question] == intent, f"{question} -> {routing[question]}, expected {intent}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])