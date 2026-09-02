"""SCC-376 Phase 3 — turn the Mac's ~/.claude/settings.json into ONE portable file for both machines.

Every deviation is itemised so Phase 6 checks the recorded list rather than a byte diff:
  1. sandbox.filesystem.*: /Users/<mac-user>/X  ->  ~/X   (the doc: ~/ resolves to $HOME per machine,
     so one line serves the Mac AND Linux).
  2. hooks: every /Users/<mac-user>/ path -> ~/. The Conductor hooks are KEPT, each guarded with
     `if [ -x ~/.conductor/hook.sh ]; then ...; fi` — they run exactly as before where Conductor is
     installed (the Mac) and are a silent no-op where it is not (Linux). The hook's exit code passes
     through the `if`, so nothing Conductor relies on changes.
  3. hooks: the two notifier hooks point at the PORTABLE ~/.claude/notify.sh — same events, same
     arguments, same timeout. The Mac's banner behaviour is folded into that script (2026-09-02).
  4. the dead `X/:*` spelling (SCC-375) respelled `X/*`.
  5. STRICT sandbox mode — NOT applied (operator ruling 2026-09-02); kept behind STRICT = False.
  6. the `git -C * <verb>` allow rules REMOVED (Phase 5): a wildcard before the subcommand approves
     any option at that position (-c, --exec-path run arbitrary commands); the house law bans the
     spelling and `cd <abs> && git <verb>` is judged per piece and already allowed.
Nothing else is touched. Nothing is printed except the deviation list and counts.

usage: python3 portable_settings.py <mac-settings.json> <out.json>
"""
import json
import re
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
d = json.loads(src.read_text(encoding="utf-8"))
dev = []
HOME_RE = re.compile(r"/Users/[^/\s'\"]+")

# 1 · sandbox filesystem paths -> ~/
fs = d.get("sandbox", {}).get("filesystem", {})
for key in ("allowWrite", "allowRead", "denyRead", "denyWrite"):
    if key not in fs:
        continue
    new = []
    for p in fs[key]:
        q = HOME_RE.sub("~", p, count=1) if p.startswith("/Users/") else p
        if q != p:
            dev.append(f"{key}: {p}  ->  {q}")
        new.append(q)
    fs[key] = new

# 2 + 3 · hooks: paths -> ~/ ; Conductor guarded ; notifier -> the portable script
CONDUCTOR = "~/.conductor/hook.sh"
NOTIFY = "~/.claude/notify.sh"
guarded, notif = 0, 0
for event, groups in d.get("hooks", {}).items():
    for g in groups:
        for h in g.get("hooks", []):
            cmd = h.get("command", "")
            new = HOME_RE.sub("~", cmd)
            if new.startswith(CONDUCTOR):
                new = f"if [ -x {CONDUCTOR} ]; then {new}; fi"
                guarded += 1
            elif new.startswith(NOTIFY):
                notif += 1
            if new != cmd:
                h["command"] = new
if guarded:
    dev.append(f"hooks: {guarded} Conductor hook(s) KEPT, path -> ~/, guarded "
               f"`if [ -x {CONDUCTOR} ]; then ...; fi` (runs as before where Conductor exists; silent no-op where it does not)")
if notif:
    dev.append(f"hooks: {notif} notifier hook(s) path -> {NOTIFY} — the PORTABLE notifier "
               f"(the Mac's banner behaviour folded in; ntfy on both machines; notify-send on Linux)")

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
#     dangerouslyDisableSandbox and auto-approved under defaultMode=auto — the file landed.
#     OPERATOR RULING 2026-09-02: NOT applied. The goal is an agent that works unattended on both
#     machines; the hatch never prompted anyone, and closing it trades a silent success for a silent
#     agent failure unless the fence is measured wide enough. The Mac's behaviour is the reference.
#     Strict mode is a FUTURE option whose entry condition is p3_battery.sh producing zero refusals.
STRICT = False
sb = d.setdefault("sandbox", {})
if STRICT and sb.get("allowUnsandboxedCommands") is not False:
    dev.append(f"sandbox.allowUnsandboxedCommands: {sb.get('allowUnsandboxedCommands', '(unset = true)')}  ->  false  (escape hatch closed)")
    sb["allowUnsandboxedCommands"] = False

# 6 · the `git -C * <verb>` rules (SCC-376 Phase 5). Claude's own warning on the project file: a
#     wildcard BEFORE the subcommand "approves any options inserted at that position … -c and
#     --exec-path can run arbitrary commands". command-shape.md rule 1 bans the spelling anyway;
#     `cd <abs> && git <verb>` is judged per piece and every verb here is already allowed that way.
dropped = [r for r in allow if re.match(r"Bash\(git -C \*", r)]
allow[:] = [r for r in allow if r not in dropped]
for r in dropped:
    dev.append(f"allow rule (git -C wildcard, SCC-376 Phase 5): {r}  ->  removed")

dst.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")

print("== deviations from the Mac file (this IS the Phase 6 list) ==")
for line in dev:
    print("  " + line)
print(f"== untouched: {len(d.get('permissions', {}).get('allow', []))} allow rules, "
      f"sandbox.enabled={d.get('sandbox', {}).get('enabled')}, "
      f"autoAllowBashIfSandboxed={d.get('sandbox', {}).get('autoAllowBashIfSandboxed')}, "
      f"hooks={ {k: len(v) for k, v in d.get('hooks', {}).items()} } ==")
print(f"remaining /Users/ references: {dst.read_text(encoding='utf-8').count('/Users/')}  (must be 0)")
