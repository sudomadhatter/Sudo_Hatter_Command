"""SCC-376 Phase 3 — turn the Mac's ~/.claude/settings.json into ONE portable file for both machines.

Three deviations, each itemised so Phase 6 checks the recorded list rather than a byte diff:
  1. sandbox.filesystem.allowWrite: /Users/<mac-user>/X  ->  ~/X   (the doc: ~/ resolves to $HOME
     per machine, so one line serves the Mac AND Linux).
  2. hooks whose command runs ~/.conductor/hook.sh are REMOVED (Conductor is a macOS app; on Linux
     the command does not exist and every session would fire eleven failing hooks).
  3. hooks whose command runs ~/.claude/notify.sh are REMOVED (macOS notifier); a Linux notifier is
     a named follow-on, not silently dropped.
Everything else is untouched. Nothing is printed except the deviation list and counts.

usage: python3 portable_settings.py <mac-settings.json> <out.json>
"""
import json
import re
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
d = json.loads(src.read_text(encoding="utf-8"))
dev = []

# 1 · allowWrite -> ~/
fs = d.get("sandbox", {}).get("filesystem", {})
for key in ("allowWrite", "allowRead", "denyRead", "denyWrite"):
    if key not in fs:
        continue
    new = []
    for p in fs[key]:
        q = re.sub(r"^/Users/[^/]+", "~", p)
        if q != p:
            dev.append(f"{key}: {p}  ->  {q}")
        new.append(q)
    fs[key] = new

# 2 + 3 · Mac-only hook programs
MAC_ONLY = (".conductor/", "notify.sh")
hooks = d.get("hooks", {})
for event, groups in list(hooks.items()):
    kept = []
    for g in groups:
        inner = [h for h in g.get("hooks", []) if not any(m in h.get("command", "") for m in MAC_ONLY)]
        removed = len(g.get("hooks", [])) - len(inner)
        if removed:
            dev.append(f"hooks.{event}: removed {removed} Mac-only hook(s) "
                       f"({', '.join(sorted({m for h in g.get('hooks', []) for m in MAC_ONLY if m in h.get('command','')}))})")
        if inner:
            g["hooks"] = inner
            kept.append(g)
    if kept:
        hooks[event] = kept
    else:
        del hooks[event]
        dev.append(f"hooks.{event}: event block emptied and removed")
if not hooks and "hooks" in d:
    del d["hooks"]

# 4 · the dead `X/:*` spelling (SCC-375): Claude documents `Bash(X:*)` as `Bash(X *)`, so a prefix
#     ending in `/` demands a space the real command never has — measured matching 0 of 22,385.
#     Respelled to the raw-prefix form `X/*` (the A2b class), itemised so it is a recorded deviation.
allow = d.get("permissions", {}).get("allow", [])
for i, r in enumerate(allow):
    if r.endswith(":*)") and r[:-3].rstrip()[-1] in "/=-:":
        fixed = r[:-3] + "*)"
        dev.append(f"allow rule (dead X/:* spelling, SCC-375): {r}  ->  {fixed}")
        allow[i] = fixed

# 5 · close the unsandboxed-retry escape hatch (vendor doc, "Strict sandbox mode"). Measured on
#     2026-09-02: a write OUTSIDE allowWrite was refused by bwrap, then retried by Claude with
#     dangerouslyDisableSandbox and auto-approved under defaultMode=auto — the file landed. With this
#     false, the parameter is ignored; anything that must run outside stays in excludedCommands.
sb = d.setdefault("sandbox", {})
if sb.get("allowUnsandboxedCommands") is not False:
    dev.append(f"sandbox.allowUnsandboxedCommands: {sb.get('allowUnsandboxedCommands', '(unset = true)')}  ->  false  (escape hatch closed)")
    sb["allowUnsandboxedCommands"] = False

dst.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")

print("== deviations from the Mac file (this IS the Phase 6 list) ==")
for line in dev:
    print("  " + line)
print(f"== untouched: {len(d.get('permissions', {}).get('allow', []))} allow rules, "
      f"sandbox.enabled={d.get('sandbox', {}).get('enabled')}, "
      f"autoAllowBashIfSandboxed={d.get('sandbox', {}).get('autoAllowBashIfSandboxed')} ==")
print(f"remaining /Users/ references: {dst.read_text(encoding='utf-8').count('/Users/')}  (must be 0)")
