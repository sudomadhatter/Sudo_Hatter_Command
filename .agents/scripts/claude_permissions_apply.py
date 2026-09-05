#!/usr/bin/env python3
"""Push the tracked Claude allow list into user scope and widen the sandbox — the ONE file an agent
cannot write (SCC-415). The Claude sibling of `antigravity_permissions_apply.py` and
`zoo_permissions_apply.py`: the operator runs it once per machine, after `/smh-llm-approvals`
has rendered the source.

Usage (python3 on Linux/Mac, python on the PC):
    python3 .agents/scripts/claude_permissions_apply.py --status   # read-only, safe anytime
    python3 .agents/scripts/claude_permissions_apply.py --apply    # write ~/.claude/settings.json
    python3 .agents/scripts/claude_permissions_apply.py --apply --prune
                                          # also DELETE user rows the tracked list does not carry

WHY THIS EXISTS WHEN THE TRACKED FILE IS ALREADY LIVE
-----------------------------------------------------
`<repo>/.claude/settings.json` is rendered from `.agents/permissions/families.json` and Claude
reads it directly — inside THIS repo. It does not reach a session opened in a project checkout or a
project worktree, which reads THAT repo's tracked file plus the machine's user scope,
`~/.claude/settings.json`. So a row harvested in the lobby holds in the lobby and nowhere else
until it is also in user scope. That is the merge `--apply` does.

`~/.claude/settings.json` also carries the `sandbox` block. With `autoAllowBashIfSandboxed: true`
a command that can run INSIDE the sandbox is auto-approved and never prompts, so the fix for a
command that escalates is to widen what the sandbox permits. `--apply` adds the tool-cache paths
every gate run touches to `sandbox.filesystem.allowWrite`.

⛔ AN AGENT CANNOT RUN `--apply`. Claude Code's auto-mode classifier refuses every write to
`~/.claude/settings.json` unconditionally — an agent widening its own sandbox or its own
permissions is the exact thing that guard exists to prevent, and reshaping the edit does not help
(measured 2026-09-05: three refusals, identically). So this script is the operator's, like the
other two applies. `/smh-llm-approvals` ends by printing the `--apply` line for him to run.

⛔ IT NEVER TOUCHES `sandbox.excludedCommands`. Excluding a command REMOVES it from the sandbox,
so it loses the `autoAllowBashIfSandboxed` auto-approval and needs a permission prompt instead —
the opposite of the fix. Operator ruling 2026-09-05, verbatim: "those are exclude commands. that
does nothing to help me why are you excluding anything the whole point is to make this so I dont
have to approve them." `test_claude_permissions_apply` pins that key byte-identical across an apply.

⛔ `allow` ROWS ONLY. The door never reads or writes a deny list (`/smh-llm-approvals` law), and a
merge that touched `deny`/`ask` would talk over a decision the operator recorded by hand.

Additive by default (SCC-414: one earlier apply on another platform deleted 58 of the operator's
own grants and he believed his approvals "don't seem to store"). `--prune` is the opt-in that
replaces. Backs the user file up once as `settings.json.scc-backup`. Idempotent — a second
`--apply` changes nothing and says so.

Stdlib only. Exit 0 on success (including "nothing to do"); 2 when a file that IS there does not
parse or cannot be read — it always says which.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERED = REPO_ROOT / ".claude" / "settings.json"
USER = Path.home() / ".claude" / "settings.json"

# The tool caches a gate run writes. None holds a secret; all are outside the repo, which is why a
# sandboxed run that touches one had to escalate before this.
WANTED_WRITE_PATHS = ["~/.cache", "~/.npm", "~/.local/share", "~/.config"]


def _load(path: Path, *, absent_ok: bool) -> dict:
    if not path.exists():
        if absent_ok:
            return {}
        raise ValueError(f"{path} does not exist")
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path} could not be read - {exc}") from exc
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not readable JSON - {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def _allow(data: dict) -> list[str]:
    rows = (data.get("permissions") or {}).get("allow") or []
    return [r for r in rows if isinstance(r, str)]


def plan(rendered: Path = RENDERED, user: Path = USER) -> dict:
    """What --apply WOULD do. Pure: reads both files, writes nothing."""
    tracked = _load(rendered, absent_ok=False)
    current = _load(user, absent_ok=True)
    t_rows, u_rows = _allow(tracked), _allow(current)
    to_add = [r for r in t_rows if r not in set(u_rows)]
    user_only = [r for r in u_rows if r not in set(t_rows)]
    have_paths = ((current.get("sandbox") or {}).get("filesystem") or {}).get("allowWrite") or []
    paths_to_add = [p for p in WANTED_WRITE_PATHS if p not in have_paths]
    return {
        "rendered": str(rendered), "user": str(user), "user_exists": user.exists(),
        "tracked_rows": len(t_rows), "user_rows": len(u_rows),
        "to_add": to_add, "user_only": user_only, "paths_to_add": paths_to_add,
    }


def apply(rendered: Path = RENDERED, user: Path = USER, prune: bool = False) -> dict:
    """Merge tracked allow rows into user scope and widen allowWrite. Returns what changed."""
    p = plan(rendered, user)
    current = _load(user, absent_ok=True)
    excluded_before = json.dumps((current.get("sandbox") or {}).get("excludedCommands"))

    perms = current.setdefault("permissions", {})
    allow = perms.get("allow")
    if not isinstance(allow, list):
        allow = []
    allow = [r for r in allow if isinstance(r, str)]
    allow.extend(p["to_add"])
    if prune:
        allow = [r for r in allow if r not in set(p["user_only"])]
    perms["allow"] = allow

    fs = current.setdefault("sandbox", {}).setdefault("filesystem", {})
    paths = fs.get("allowWrite")
    if not isinstance(paths, list):
        paths = []
    paths.extend(p["paths_to_add"])
    fs["allowWrite"] = paths

    excluded_after = json.dumps((current.get("sandbox") or {}).get("excludedCommands"))
    assert excluded_before == excluded_after, "excludedCommands must never change here"

    changed = bool(p["to_add"] or p["paths_to_add"] or (prune and p["user_only"]))
    backup = user.with_suffix(".json.scc-backup")
    made_backup = False
    if changed:
        user.parent.mkdir(parents=True, exist_ok=True)
        if user.exists() and not backup.exists():
            shutil.copy2(user, backup)
            made_backup = True
        user.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**p, "changed": changed, "pruned": p["user_only"] if prune else [],
            "backup": str(backup), "backup_written_now": made_backup}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--status", action="store_true", help="read-only report (default)")
    ap.add_argument("--apply", action="store_true", help="write the merge into the user-scope file")
    ap.add_argument("--prune", action="store_true",
                    help="with --apply: also DELETE user-scope rows the tracked list does not carry")
    ap.add_argument("--rendered", type=Path, default=RENDERED, help="override the tracked list (tests)")
    ap.add_argument("--user", type=Path, default=USER, help="override the user-scope file (tests)")
    a = ap.parse_args(argv)

    try:
        r = apply(a.rendered, a.user, prune=a.prune) if a.apply else plan(a.rendered, a.user)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    print(f"tracked : {r['rendered']}  ({r['tracked_rows']} allow rows)")
    print(f"user    : {r['user']}  ({r['user_rows']} allow rows{'' if r['user_exists'] else ', absent - will be created'})")
    verb = "added" if a.apply else "to add"
    print(f"allow   : {len(r['to_add'])} row(s) {verb} to user scope"
          + (f"; {len(r['user_only'])} user-only row(s) {'PRUNED' if a.prune and a.apply else 'kept'}" if r["user_only"] else ""))
    for row in r["to_add"]:
        print(f"  + {row}")
    print(f"sandbox : {len(r['paths_to_add'])} allowWrite path(s) {verb}"
          + (": " + ", ".join(r["paths_to_add"]) if r["paths_to_add"] else ""))
    if a.apply:
        if r["changed"]:
            print(f"backup  : {r['backup']} ({'written now' if r['backup_written_now'] else 'kept, already existed'})")
            print("wrote   : " + r["user"])
            print("next    : restart the Claude session (or reload the window) for it to take effect.")
        else:
            print("status  : already in sync - nothing written.")
    elif r["to_add"] or r["paths_to_add"]:
        print("next    : python3 .agents/scripts/claude_permissions_apply.py --apply   (PC: python)")
    else:
        print("status  : in sync - user scope already carries every tracked row and every sandbox path.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
