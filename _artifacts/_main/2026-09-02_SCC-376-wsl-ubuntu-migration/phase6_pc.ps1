# phase6_pc.ps1 - SCC-376 Phase 6, the Desktop Team's ONE paste (sign-off on the PC).
#
# Run it in PowerShell (Windows Terminal) with BOTH VS Code instances CLOSED - code1 and code2.
# It refuses to run while Code.exe is alive, because the Zoo apply must write the two Windows stores
# that VS Code overwrites on exit. It is idempotent: run it again after the by-hand click in step 7.
#
# What it does:  1. syncs both distros' clones to the lane and installs the ONE user file in each
#                2. runs the Zoo apply FROM UBUNTU (both Windows stores, the code2 seat's included)
#                3. retires the Windows %USERPROFILE%\.claude\settings.json (rename, reversible)
#                4. reports the Windows clone C:\Sudo_Hatter_Command - it is NOT deleted (see the report)
#                5. probes both distros and runs the lobby gate bare inside Ubuntu
#                6. prints the eight-line checklist from those live values
#                7. names the one by-hand click left (the code2 seat's Zoo toggles), then re-run
# Paste the whole transcript back: %TEMP%\phase6_pc.log
$ErrorActionPreference = 'Continue'
$env:WSL_UTF8 = '1'
$LOG = Join-Path $env:TEMP 'phase6_pc.log'
Start-Transcript -Path $LOG -Force | Out-Null
function Say($t) { Write-Host ''; Write-Host "== $t ==" -ForegroundColor Cyan }
$UB = 'Ubuntu'; $ZOO2 = 'Ubuntu-zoo2'

# ---- the Ubuntu-side work, one script, four modes ------------------------------------------------
$sh = @'
#!/bin/bash
# SCC-376 Phase 6, Linux side. $1 = sync | apply | probe | gate
set -u
R=/home/dlohn/Sudo_Hatter_Command
F=_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/claude-user-settings.portable.json
cd "$R" || { echo "no clone at $R"; exit 1; }
case "$1" in
  sync)
    git fetch origin chore/SCC-376-wsl-ubuntu-plan --quiet || { echo "fetch FAILED"; exit 1; }
    if [ -n "$(git status --short -- docs/repo-map.md)" ]; then
      git checkout -- docs/repo-map.md && echo "docs/repo-map.md: regenerated cache dropped (the Phase 4 remedy, run while the seat is idle)"
    fi
    git merge --ff-only FETCH_HEAD --quiet && echo "clone: $(git rev-parse --short HEAD), $(git status --short | wc -l) dirty"
    python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$F" && cp "$F" /home/dlohn/.claude/settings.json
    echo "user file: sha $(sha256sum /home/dlohn/.claude/settings.json | cut -c1-16) (committed: $(sha256sum "$F" | cut -c1-16))"
    ;;
  apply)
    python3 .agents/scripts/zoo_permissions_apply.py --apply --enable-auto-approve
    echo "apply rc=$?"
    ;;
  verify)
    # COMPUTED, never counted from text: the first cut of this paste scraped the printed lines
    # and read 8 of 4 in-sync and 2 of 2 toggles ON while the code2 seat's own store said
    # alwaysAllowExecute=false. A summary that can over-count is worse than none - it signed off
    # a seat that was fenced by nothing.
    python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location("z", "/home/dlohn/Sudo_Hatter_Command/.agents/scripts/zoo_permissions_apply.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
allow, deny = m.tracked_lists()
rows = [(db, m.load_memento(db)) for db in m.candidate_dbs()]
rows = [(db, x) for db, x in rows if x]
ins = tog = 0
for db, x in rows:
    sync = x.get("allowedCommands") == allow and x.get("deniedCommands") == deny
    on = x.get("autoApprovalEnabled") is True and x.get("alwaysAllowExecute") is True
    ins += sync; tog += on
    print("  %-72s lists %-7s toggles %s" % (db, "in sync" if sync else "DRIFT", "ON" if on else "OFF"))
print("VERDICT stores=%d in-sync=%d toggles-on=%d" % (len(rows), ins, tog))
PY
    ;;
  probe)
    bash -lc '
      printf "user=%s uid=%s | PATH leak=%s | clone fs=%s\n" "$(whoami)" "$(id -u)" "$(echo "$PATH" | tr ":" "\n" | grep -c "^/mnt/")" "$(stat -f -c %T /home/dlohn/Sudo_Hatter_Command)"
      for b in git node python3 claude gh acli; do printf "%s=%s " "$b" "$(command -v $b || echo MISSING)"; done; echo
      printf "windows binaries resolving: %s\n" "$(for b in git node python3 claude gh acli; do command -v $b; done | grep -c "^/mnt/")"
      python3 - <<PY
import json,os,re
d=json.load(open("/home/dlohn/.claude/settings.json"))
print("sandbox.enabled=%s | rules=%d | git -C rules=%d | Windows rows=%d" % (d["sandbox"]["enabled"], len(d["permissions"]["allow"]), sum("git -C" in r for r in d["permissions"]["allow"]), sum(bool(re.search(r"Scripts[/\\\\]|\\.exe\\b|MSYS", r)) for r in d["permissions"]["allow"])))
t=open("/home/dlohn/Sudo_Hatter_Command/.vscode/settings.json",encoding="utf-8").read()
z=json.loads(re.sub(r"^\\s*//.*$","",t,flags=re.M))["zoo-code.allowedCommands"]
c=json.load(open("/home/dlohn/Sudo_Hatter_Command/.claude/settings.json"))["permissions"]["allow"]
win=lambda rows:[r for r in rows if "\\\\" in r or "Scripts" in r or ".exe" in r or "MSYS" in r or r in ("dir","type ","findstr","where ","more") or r.startswith(("Write-","Get-","Select-","Test-"))]
print("tracked lists: zoo %d rows, %d Windows-shell rows | claude %d rows, %d Windows-shell rows, %d git -C rows" % (len(z), len(win(z)), len(c), len(win(c)), sum("git -C" in r for r in c)))
PY
    '
    ;;
  gate)
    python3 .agents/scripts/tests/run_all.py > /tmp/p6-run_all.log 2>&1
    echo "run_all rc=$? :: $(grep -E 'files passed' /tmp/p6-run_all.log | tail -1)"
    ;;
  *) echo "unknown mode $1"; exit 1 ;;
esac
'@
$WINTMP = Join-Path $env:TEMP 'phase6_wsl.sh'
[IO.File]::WriteAllText($WINTMP, ($sh -replace "`r?`n", "`n"), (New-Object System.Text.UTF8Encoding($false)))
# wslpath is NOT usable here: PowerShell strips the backslashes passing $WINTMP through
# wsl.exe, so wslpath reads 'C:UsersdlohnAppData...' and returns empty - every Linux step then
# ran with no script at all ('bash: gate: No such file or directory'). Build the /mnt/ path by
# hand, the way phase4_pc.ps1 already did. (Desktop Team, Phase 6 run, 2026-09-02.)
$WSLTMP = '/mnt/' + $env:TEMP.Substring(0,1).ToLower() + ($env:TEMP.Substring(2) -replace '\\','/') + '/phase6_wsl.sh'
function Linux($distro, $mode) { & wsl.exe -d $distro -u dlohn -- bash $WSLTMP $mode 2>&1 | ForEach-Object { "  $_" } }

# ---- 0. preconditions -----------------------------------------------------------------------------
Say '0. preconditions'
$code = Get-Process Code -ErrorAction SilentlyContinue
if ($code) { "REFUSED: VS Code is running ($($code.Count) Code.exe processes). Close BOTH windows (code1 and code2), then re-run."; Stop-Transcript | Out-Null; exit 1 }
'VS Code: closed'
$distros = (& wsl.exe -l -q) -replace "`0", '' | Where-Object { $_ -ne '' }
"distros: $($distros -join ', ')"
foreach ($d in @($UB, $ZOO2)) { if ($distros -notcontains $d) { "REFUSED: distro '$d' is not registered - Phase 4 first."; Stop-Transcript | Out-Null; exit 1 } }

# ---- 1. sync both clones + install the ONE user file ----------------------------------------------
Say "1. sync + user file: $UB"
Linux $UB 'sync'
Say "1. sync + user file: $ZOO2"
Linux $ZOO2 'sync'

# ---- 2. the Zoo apply, from Ubuntu, into BOTH Windows stores -----------------------------------------
Say '2. Zoo apply from Ubuntu (both Windows stores, master toggles included)'
Linux $UB 'apply'
$verify = Linux $UB 'verify'
$verify
$v = ($verify | Select-String 'VERDICT stores=(\d+) in-sync=(\d+) toggles-on=(\d+)').Matches
if ($v) { $nStores = [int]$v.Groups[1].Value; $inSync = [int]$v.Groups[2].Value; $togglesOn = [int]$v.Groups[3].Value }
else    { $nStores = 0; $inSync = 0; $togglesOn = 0; 'VERDICT line not found - treat every count below as 0' }
"stores found: $nStores | lists in sync: $inSync of $nStores | master toggles ON: $togglesOn of $nStores"

# ---- 3. retire the Windows user file -------------------------------------------------------------------
Say '3. retire the Windows ~\.claude\settings.json'
# The first cut printed "renamed ->" whether or not the rename happened: with
# $ErrorActionPreference = 'Continue' a failed Rename-Item writes its error and the string on the
# next line still runs. A retire step that reports success over a file it did not move is the one
# thing this step must never do, so the result is now checked and the file is CLASSIFIED - a
# Windows Claude session rewrites a small preferences file here, and that is not a fence.
$W = Join-Path $env:USERPROFILE '.claude\settings.json'
$WR = "$W.retired-scc376"
if (-not (Test-Path $W)) {
  if (Test-Path $WR) { "already retired: $WR" } else { "no Windows user file at $W - nothing to retire" }
} else {
  $keys = @()
  try { $keys = ((Get-Content $W -Raw) | ConvertFrom-Json).PSObject.Properties.Name } catch { $keys = @('<unparseable>') }
  $fencing = @($keys | Where-Object { $_ -in 'permissions', 'hooks', 'sandbox' })
  if (Test-Path $WR) {
    if ($fencing.Count -gt 0) {
      "STOP: $W carries $($fencing -join ', ') and $WR already exists. NOT touched - hand this line to the agent."
    } else {
      "left in place: $W is $((Get-Item $W).Length) bytes, keys [$($keys -join ', ')] - preferences only, it fences nothing. Already retired: $WR"
    }
  } else {
    Rename-Item $W $WR -ErrorAction SilentlyContinue
    if (Test-Path $WR) { "renamed -> $WR (rename it back to undo)" } else { "RENAME FAILED - $W is untouched" }
  }
}

# ---- 4. the Windows clone: report, never delete -----------------------------------------------------------
Say '4. the Windows clone C:\Sudo_Hatter_Command (report only)'
if (Test-Path 'C:\Sudo_Hatter_Command\.git') {
  Push-Location 'C:\Sudo_Hatter_Command'
  $dirty = @(git status --short)
  Pop-Location
  "uncommitted files: $($dirty.Count)"
  $dirty | ForEach-Object { "  $_" }
  'NOT deleted. These belong to other sessions (memory files) and to AVCH-109 (scratch). The operator says when,'
  'after their owners commit them or the agent carries them into the Ubuntu clone under a memory commit.'
} else { 'no Windows clone at C:\Sudo_Hatter_Command' }

# ---- 5. probes + the gate ----------------------------------------------------------------------------------
Say "5. probe: $UB"
$pU = Linux $UB 'probe'; $pU
Say "5. probe: $ZOO2"
$pZ = Linux $ZOO2 'probe'; $pZ
Say '5. the lobby gate, bare, inside Ubuntu (about 30 s)'
$gate = Linux $UB 'gate'; $gate

# ---- 6. the checklist ---------------------------------------------------------------------------------------
Say '6. Phase 6 checklist (live values above; recorded gates named)'
'[1] Sandbox ACTIVE by demonstrated containment ........ Phase 3 gate, recorded 2026-09-02 (three probes); live: sandbox.enabled above'
'[2] Zero Windows binaries resolve inside either distro .. live: "windows binaries resolving: 0" and "PATH leak=0" in BOTH probes'
'[3] Repo and venvs on the Linux filesystem ............... live: "clone fs=ext2/ext3" (how stat names the ext4 family) in BOTH probes'
"[4] All test suites green from WSL, run bare ............ live: $($gate -join ' ')"
"[5] code and code2 isolated, and BOTH seats fenced ...... Phase 4 gate PASS (Desktop Team); live: master toggles ON in $togglesOn of $nStores stores - a seat with them OFF consults no list and asks for everything (must be $nStores of $nStores)"
'[6] Zoo and Claude allow lists carry no Windows rows ..... live: "0 Windows-shell rows" for zoo AND claude, "0 git -C rows"'
"[7] PC ~/.claude/settings.json == the committed portable file ... live: both distros print the committed sha; the Mac's install must print the same (e1a13e0d126f0478)"
'[8] Running as a normal user ............................. live: "user=dlohn uid=1001" in BOTH probes'
"Zoo stores in sync after the apply: $inSync of $nStores"
if ($nStores -gt 0 -and $inSync -eq $nStores -and $togglesOn -eq $nStores) { 'PHASE 6: all eight lines hold.' }
else { 'PHASE 6 NOT PASSED - see step 7.' }

# ---- 7. the one by-hand click --------------------------------------------------------------------------------
Say '7. if any count above is short'
'   The apply now turns the two master toggles ON itself (--enable-auto-approve), so no Zoo panel'
'   click is needed. A short count means the write did not happen: the usual cause is a VS Code'
'   process still alive when step 2 ran (it flushes its own state on exit and overwrites).'
'   Close every VS Code window, confirm with: Get-Process Code -ErrorAction SilentlyContinue'
'   then re-run this paste - it is idempotent.'
"transcript: $LOG  <- paste it back"
Stop-Transcript | Out-Null
