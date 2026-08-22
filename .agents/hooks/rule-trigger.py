#!/usr/bin/env python3
"""rule-trigger — put the right house rule in front of the agent BEFORE it starts guessing.

A `UserPromptSubmit` hook. Whatever it prints on stdout is injected into the session as context,
so what it prints is a **pointer** — the rule's path and its one-line description — never the rule
body. Three lines at most. Dragging a 40 KB protocol rule into every prompt is the failure mode
this exists to avoid, not a feature.

─── Why this file exists ──────────────────────────────────────────────────────────────────────
`.agents/rules/` reaches the agent two ways, and until now only one of them worked:

  * a **file** trigger — Claude Code reads `paths:` in a rule's frontmatter and loads that rule
    when a matching file is read. `sync-agents.ps1` emits the six path-scoped rules into
    `.claude/rules/` for exactly this.
  * an **intent** trigger — the operator types "the suite is red", and `reproduce-before-you-fix`
    should already be loaded when the agent forms its first thought. NO FILE IS READ, so `paths:`
    can never fire. Twelve rules carry a `triggers:` keyword list for this case and, before this
    hook, nothing on any platform read that list. Antigravity judges `description:` itself;
    Claude Code has no equivalent. This closes that half.

─── The matcher, and why it is not a substring search ─────────────────────────────────────────
A trigger matches when **every word in it appears in the prompt**, in any order. Order-independence
is the whole point: `reproduce-before-you-fix` lists `red suite`, and an operator writes "the suite
is red". A substring matcher misses that — which is to say it misses the phrasing people actually
use. Both sides are normalised the same way (lowercased, punctuation to spaces), so `what's next`
matches "what is next?" and "whats next".

Ranking is by number of distinct triggers matched, then by the longest single match, then by name
so two equal rules never reorder between runs. Only the top three print.

─── ⛔ It fails open. Always. ──────────────────────────────────────────────────────────────────
Any unreadable rule, missing tree, bad encoding, or unexpected exception → exit 0, print nothing.
The rules still load by their normal mechanisms; this only makes one of them earlier. A hook that
blocks a prompt because a YAML block was malformed is a worse defect than the one it fixes — the
same law `.agents/hooks/INDEX.md` states for the whole Claude-only layer, and the reason the `main`
write gate is a pure-`sh` git hook that depends on none of this.

Stdlib only, and launched through `run-hook.sh` so it probes `python3 → python → py` rather than
naming one machine's interpreter (the exit-127 class of bug, SCC-77).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

MAX_POINTERS = 3
"""Injected context is charged to EVERY prompt in the session. Three is the budget."""

DESC_CHARS = 150
"""A pointer is a signpost, not a summary. Longer descriptions are cut at a word boundary."""

_WORD = re.compile(r"[a-z0-9]+")


def words(text: str) -> list[str]:
    """Lowercase alphanumeric words. `what's next` and `whats next` normalise identically."""
    return _WORD.findall(text.lower())


def frontmatter(text: str) -> dict[str, str]:
    """The scalar lines of a leading `---` block, as raw strings.

    Deliberately not a YAML parser — stdlib only, and these files are hand-written in a fixed
    shape. NO CLOSING FENCE MEANS NO FRONTMATTER: returning `{}` is what makes a half-written rule
    file invisible to this hook instead of fatal to the prompt.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip()
    return out


def triggers_of(fm: dict[str, str]) -> list[str]:
    """The `triggers: [a, b c, d]` inline list. Anything else reads as no triggers."""
    raw = fm.get("triggers", "")
    if not (raw.startswith("[") and raw.endswith("]")):
        return []
    return [t.strip().strip("'\"") for t in raw[1:-1].split(",") if t.strip()]


def describe(fm: dict[str, str]) -> str:
    desc = " ".join(fm.get("description", "").split()).strip("'\"")
    if len(desc) <= DESC_CHARS:
        return desc
    return desc[:DESC_CHARS].rsplit(" ", 1)[0] + "…"


def repo_root() -> Path | None:
    """Where `.agents/rules/` lives, or None.

    ⛔ `CLAUDE_PROJECT_DIR` IS AUTHORITATIVE WHEN SET — no fallback behind it. `run-hook.sh` sets
    it, and in a worktree lane it is the ONLY thing that names the right tree. The first cut fell
    through to this file's own ancestors when the named tree had no rules, and a hook run against a
    tree with no `.agents/rules/` happily answered out of the lane it was installed in — a
    cross-tree read, the same class as the cwd-resets-to-main scar. Named tree, no rules, no
    output.

    Only when NOTHING names a tree do cwd and this file's ancestors get a say; the ancestor walk is
    what keeps a hand-run working from the `.claude/hooks/` mirror as well as from this master.
    """
    named = os.environ.get("CLAUDE_PROJECT_DIR")
    if named:
        return Path(named) if (Path(named) / ".agents" / "rules").is_dir() else None
    if (Path.cwd() / ".agents" / "rules").is_dir():
        return Path.cwd()
    for parent in Path(__file__).resolve().parents:
        if (parent / ".agents" / "rules").is_dir():
            return parent
    return None


def read_prompt() -> str:
    """Claude Code sends `{"prompt": "..."}` on stdin; a hand-test types bare text.

    Understanding only the JSON shape would make this hook impossible to debug by hand, which is
    how every other script in this tree is checked.
    """
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        return raw
    if isinstance(obj, dict):
        return str(obj.get("prompt", "") or "")
    return raw


def matches(rules_dir: Path, prompt: str) -> list[tuple[int, int, str, str]]:
    """(-hits, -longest, stem, description) for every rule whose triggers fire, best first.

    Negated so a plain ascending sort puts the strongest match first — no reverse-sort with a key
    that would then order names backwards too.
    """
    present = set(words(prompt))
    if not present:
        return []
    found = []
    for path in sorted(rules_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        try:
            fm = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        hits = [t for t in triggers_of(fm) if (w := words(t)) and present.issuperset(w)]
        if hits:
            found.append((-len(hits), -max(len(t) for t in hits), path.stem, describe(fm)))
    found.sort()
    return found


def main() -> int:
    root = repo_root()
    if root is None:
        return 0
    hits = matches(root / ".agents" / "rules", read_prompt())[:MAX_POINTERS]
    if not hits:
        return 0
    print("[house rules] this prompt matches standing law — read before you act:")
    for _, _, stem, desc in hits:
        print(f"  - .agents/rules/{stem}.md" + (f" — {desc}" if desc else ""))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:            # noqa: BLE001 — ⛔ fail open: never block a prompt
        raise SystemExit(0)
