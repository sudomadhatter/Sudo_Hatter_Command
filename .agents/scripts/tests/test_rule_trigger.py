"""`.agents/hooks/rule-trigger.py` — the prompt-side half of rule activation.

Rules reach the agent two ways, and until this hook existed only one of them worked:

  * a **file** trigger — Claude Code reads `paths:` and loads the rule when a matching file is
    read. Six rules are path-scoped and `sync-agents.ps1` emits them into `.claude/rules/`.
  * an **intent** trigger — the operator says "the suite is red" and `reproduce-before-you-fix`
    should be in front of the agent BEFORE it starts guessing. No file is read, so `paths:` can
    never fire. Twelve rules carry a `triggers:` keyword list for exactly this, and nothing read
    it. This hook is what reads it.

`UserPromptSubmit` injects whatever the hook prints on stdout into the session as context, so the
output is a POINTER, never the rule body: three lines at most, naming the file and its one-line
description. Dragging a 40 KB rule into every prompt is the failure mode this is built to avoid.

⛔ **It fails open, always.** A hook that cannot parse a rule, cannot find the tree, or hits any
exception at all exits 0 and prints nothing. The rules still load by their normal mechanisms; this
only makes one of them earlier. A hook that blocks a prompt because a YAML block was malformed is a
worse defect than the one it exists to fix — the same law `.agents/hooks/INDEX.md` states for the
whole Claude-only layer.

Stdlib only, no pytest — same constraint as the rest of this suite.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "rule-trigger.py"


def run_hook(prompt: str, project_dir: Path) -> tuple[int, str]:
    """Invoke the hook exactly as Claude Code does: prompt JSON on stdin, cwd at the tree.

    `CLAUDE_PROJECT_DIR` is how `run-hook.sh` tells a hook where the tree is, so pointing it at a
    temp tree is the real resolution path, not a test-only back door.
    """
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    r = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": prompt}),
        capture_output=True, text=True, errors="replace", env=env, cwd=str(project_dir),
    )
    return r.returncode, (r.stdout or "")


def rule(dirpath: Path, name: str, triggers: list[str], desc: str = "") -> None:
    body = "---\n"
    body += f"name: {name}\n"
    body += f"description: {desc or (name + ' applies here')}\n"
    body += "trigger: model_decision\n"
    body += "triggers: [" + ", ".join(triggers) + "]\n"
    body += "---\n\n# " + name + "\n"
    (dirpath / f"{name}.md").write_text(body, encoding="utf-8")


def main() -> int:
    c = Cases("rule-trigger hook")

    # ── A · the real tree, the case the plan named ────────────────────────────────────────────
    # "the suite is red" does NOT contain the literal trigger "red suite". A substring matcher
    # misses it, and that phrasing is how an operator actually reports a broken suite. Matching is
    # therefore WORD-SET based: every word of the trigger must appear in the prompt, in any order.
    if c.block("A · 'the suite is red' points at reproduce-before-you-fix"):
        rc, out = run_hook("the suite is red", ROOT)
        c.check("A exits 0", rc == 0, f"rc={rc}")
        c.check("A names reproduce-before-you-fix", "reproduce-before-you-fix" in out, out.strip())

    if c.block("B · 'what's in progress on jira' points at jira"):
        rc, out = run_hook("what's in progress on jira", ROOT)
        c.check("B exits 0", rc == 0, f"rc={rc}")
        c.check("B names jira", "rules/jira.md" in out, out.strip())

    if c.block("C · an unrelated prompt says NOTHING"):
        rc, out = run_hook("write me a poem", ROOT)
        c.check("C exits 0", rc == 0, f"rc={rc}")
        c.check("C prints nothing (silence is the normal case)", out.strip() == "", out.strip())

    # ── D · fail-open: a rule the parser cannot read must never take the prompt down ──────────
    # ⛔ TWO fixtures, because one of them proves nothing on its own. `broken.md` has a mangled
    # trigger list, so it stays silent whether or not the fence guard works — a vacuous pin. The
    # one that bites is `unfenced.md`: a PERFECTLY GOOD trigger list with no closing `---`. That is
    # a file caught mid-edit, and it must stay silent, because half-parsed law read as whole law is
    # worse than no law. Delete the `end == -1` guard and only this second file catches it.
    if c.block("D · ⛔ a malformed rule file exits 0 and prints nothing"):
        with TempDir() as tmp:
            rules = tmp / ".agents" / "rules"
            rules.mkdir(parents=True)
            (rules / "broken.md").write_text(
                "---\nname: broken\ntriggers: [unclosed, list\n# no closing fence at all\n",
                encoding="utf-8")
            (rules / "unfenced.md").write_text(
                "---\nname: unfenced\ndescription: would match if it were parsed\n"
                "triggers: [red suite]\n\n# body starts with no closing fence\n",
                encoding="utf-8")
            rc, out = run_hook("the suite is red", tmp)
            c.check("D exits 0 on a malformed rule", rc == 0, f"rc={rc}")
            c.check("D prints nothing", out.strip() == "", out.strip())
            c.check("D an unfenced rule stays silent even though its triggers WOULD match",
                    "unfenced" not in out, out.strip())

    # ── E · no tree at all: still open ────────────────────────────────────────────────────────
    if c.block("E · ⛔ no .agents/rules/ at all exits 0 and prints nothing"):
        with TempDir() as tmp:
            rc, out = run_hook("the suite is red", tmp)
            c.check("E exits 0 with no rules dir", rc == 0, f"rc={rc}")
            c.check("E prints nothing", out.strip() == "", out.strip())

    # ── F · the cap. Injected context is charged to every prompt, so it is bounded ────────────
    if c.block("F · at most 3 pointers, however many rules match"):
        with TempDir() as tmp:
            rules = tmp / ".agents" / "rules"
            rules.mkdir(parents=True)
            for i in range(6):
                rule(rules, f"rule-{i}", ["widget"])
            rc, out = run_hook("the widget is broken", tmp)
            named = [ln for ln in out.splitlines() if "rules/rule-" in ln]
            c.check("F exits 0", rc == 0, f"rc={rc}")
            c.check("F caps at 3 pointers", len(named) <= 3, f"{len(named)} lines: {named}")
            c.check("F still points at something", len(named) >= 1, out.strip())

    # ── G · ranking. The rule matching MORE of the prompt wins the scarce slots ───────────────
    if c.block("G · more matched triggers ranks higher"):
        with TempDir() as tmp:
            rules = tmp / ".agents" / "rules"
            rules.mkdir(parents=True)
            rule(rules, "weak", ["widget"])
            rule(rules, "strong", ["widget", "sprocket", "flange"])
            for i in range(4):
                rule(rules, f"filler-{i}", ["widget"])
            rc, out = run_hook("the widget sprocket flange is broken", tmp)
            named = [ln for ln in out.splitlines() if "rules/" in ln]
            c.check("G exits 0", rc == 0, f"rc={rc}")
            c.check("G the 3-trigger rule survives the cap",
                    any("rules/strong.md" in ln for ln in named), out.strip())

    # ── H · a bare prompt on stdin (not JSON) is still read ───────────────────────────────────
    # Claude Code sends JSON, but `run-hook.sh` is a plain pipe and a hand-test types text. A
    # hook that only understands one of the two is a hook nobody can debug by hand.
    if c.block("H · plain-text stdin works, not only JSON"):
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
        r = subprocess.run([sys.executable, str(HOOK)], input="the suite is red",
                           capture_output=True, text=True, errors="replace", env=env,
                           cwd=str(ROOT))
        c.check("H exits 0", r.returncode == 0, f"rc={r.returncode}")
        c.check("H names reproduce-before-you-fix",
                "reproduce-before-you-fix" in (r.stdout or ""), (r.stdout or "").strip())

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
