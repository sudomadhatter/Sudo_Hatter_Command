# phase4_pc.ps1 - SCC-376 Phase 4, the Desktop Team's ONE paste. Windows PowerShell, run as yourself.
#
# In order:  0. preconditions (VS Code, the Remote-WSL extension, a distro named Ubuntu)
#            1. inside Ubuntu: Java 17 + JAVA_HOME in ~/.profile, a `code` door, the three work
#               extensions (Python, Claude Code, Zoo Code) re-asserted, then a probe
#            2. STOP - you close every VS Code window - then WSL shuts down
#            3. Ubuntu exported as a disk image and imported as Ubuntu-zoo2
#            4. Ubuntu-zoo2: the copied Claude login removed, then the same probe
#            5. code2 repointed at Ubuntu-zoo2 (old launcher kept as code2.cmd.bak-scc376)
#            6. the report you paste back, then the by-hand gate
# Re-runnable: every step checks before it acts. Prints no secret. Log: %TEMP%\phase4_pc.log
$ErrorActionPreference = 'Continue'
$env:WSL_UTF8 = '1'
$ZOO2    = 'Ubuntu-zoo2'
$EXPORT  = 'C:\WSL\exports\Ubuntu-scc376-phase3.vhdx'
$INSTALL = 'C:\WSL\Ubuntu-zoo2'
$CODE    = 'C:\Microsoft VS Code\bin\code.cmd'
$CODE2   = Join-Path $env:USERPROFILE '.local\bin\code2.cmd'
Start-Transcript -Path (Join-Path $env:TEMP 'phase4_pc.log') -Force | Out-Null
function Say($s) { Write-Host ''; Write-Host "== $s" -ForegroundColor Cyan }

# ---- the Linux half: one script, run by mode, written once with LF endings ----
$sh = @'
#!/bin/bash
# SCC-376 Phase 4, the Linux half. Modes: setup (Ubuntu) | strip (Ubuntu-zoo2) | probe (either).
# Every mode ends with the probe. Prints no secret.
set -u
MODE="${1:-probe}"
SHIM="/mnt/c/Microsoft VS Code/bin/code"
JH=/usr/lib/jvm/java-17-openjdk-amd64
case "$MODE" in
  setup)
    echo "-- java 17 (the Firebase emulator needs a JRE: AGY rules + e2e tiers)"
    if [ -x "$JH/bin/java" ]; then echo "java: already installed"
    else
      sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq >/tmp/p4-apt.log 2>&1
      sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq openjdk-17-jre-headless >>/tmp/p4-apt.log 2>&1 \
        && echo "java: installed" || echo "java: apt FAILED - see /tmp/p4-apt.log"
    fi
    if grep -q 'JAVA_HOME=' ~/.profile 2>/dev/null; then echo "profile: JAVA_HOME already present"
    else
      printf '\n# SCC-376 Phase 4: JDK 17 for the Firebase emulator. Lives in ~/.profile because the VS Code server and every login shell read it; ~/.bashrc is invisible to automation.\nexport JAVA_HOME=%s\nexport PATH="$JAVA_HOME/bin:$PATH"\n' "$JH" >> ~/.profile
      echo "profile: JAVA_HOME added to ~/.profile"
    fi
    echo "-- code door (appendWindowsPath=false took the Windows shim off PATH)"
    sudo ln -sfn "$SHIM" /usr/local/bin/code && echo "code: /usr/local/bin/code -> VS Code shim"
    echo "-- work extensions inside this distro (idempotent)"
    "$SHIM" --install-extension ms-python.python --install-extension anthropic.claude-code \
            --install-extension zoocodeorganization.zoo-code@3.81.100433 2>&1 | grep -i 'installed\|error\|fail'
    ;;
  strip)
    if [ -f ~/.claude/.credentials.json ]; then
      rm -f ~/.claude/.credentials.json && echo "claude login: copy removed (one login per distro; run claude /login here if ever needed)"
    else echo "claude login: no copy present"; fi
    ;;
esac
echo "-- probe, from a LOGIN shell (what the VS Code server and every terminal get)"
bash -lc '
  printf "distro=%s user=%s uid=%s home=%s\n" "${WSL_DISTRO_NAME:-?}" "$(whoami)" "$(id -u)" "$HOME"
  printf "windows PATH leak=%s (must be 0)\n" "$(echo "$PATH" | tr ":" "\n" | grep -c "^/mnt/")"
  printf "repo=%s fs=%s\n" "$HOME/Sudo_Hatter_Command" "$(stat -f -c %T "$HOME/Sudo_Hatter_Command" 2>/dev/null || echo MISSING)"
  printf "JAVA_HOME=%s java=%s\n" "${JAVA_HOME:-UNSET}" "$(java -version 2>&1 | head -1)"
  printf "code door=%s\n" "$(command -v code || echo MISSING)"
  printf "claude login copy=%s\n" "$([ -f "$HOME/.claude/.credentials.json" ] && echo present || echo none)"
  printf "vscode-server extensions=%s\n" "$(ls -d "$HOME"/.vscode-server/extensions/*/ 2>/dev/null | wc -l)"
  ls -d "$HOME"/.vscode-server/extensions/*/ 2>/dev/null | xargs -n1 basename | sed "s/^/  /"
'
'@
$TMP = Join-Path $env:TEMP 'phase4_wsl.sh'
[IO.File]::WriteAllText($TMP, ($sh -replace "`r`n", "`n"), (New-Object System.Text.UTF8Encoding($false)))
$WSLTMP = '/mnt/' + $env:TEMP.Substring(0,1).ToLower() + ($env:TEMP.Substring(2) -replace '\\','/') + '/phase4_wsl.sh'
function Linux($distro, $mode) { & wsl.exe -d $distro -u dlohn -- bash $WSLTMP $mode }

Say '0. preconditions'
if (-not (Test-Path $CODE)) { Write-Host "VS Code is not at $CODE - stop and tell the operator"; Stop-Transcript | Out-Null; exit 1 }
$have = & $CODE --list-extensions 2>$null | Select-String -SimpleMatch 'ms-vscode-remote.remote-wsl'
if ($have) { 'remote-wsl: installed on Windows' } else { & $CODE --install-extension ms-vscode-remote.remote-wsl 2>$null | Select-String 'installed' }
$distros = @(& wsl.exe --list --quiet | ForEach-Object { $_.Trim() } | Where-Object { $_ })
"distros: $($distros -join ', ')"
if ($distros -notcontains 'Ubuntu') { Write-Host 'no distro named Ubuntu - stop and tell the operator'; Stop-Transcript | Out-Null; exit 1 }

Say '1. Ubuntu: Java 17, JAVA_HOME, code door, extensions, probe'
Linux 'Ubuntu' 'setup'

Say '2. STOP. Close EVERY VS Code window and any terminal running claude or zoo. WSL shuts down next.'
Read-Host '   Press Enter when they are closed' | Out-Null
& wsl.exe --shutdown
'wsl: shut down'

Say "3. export Ubuntu, import as $ZOO2"
if ($distros -contains $ZOO2) { "$ZOO2 is already registered - export/import skipped" }
else {
  New-Item -ItemType Directory -Force -Path (Split-Path $EXPORT), $INSTALL | Out-Null
  if (Test-Path $EXPORT) { "export already on disk: $EXPORT" }
  else {
    'exporting (a block copy of the ~22 GB disk; a few minutes)...'
    & wsl.exe --export Ubuntu $EXPORT --vhd
    "export rc=$LASTEXITCODE size=$([math]::Round((Get-Item $EXPORT -ErrorAction SilentlyContinue).Length/1GB,1)) GB"
  }
  & wsl.exe --import $ZOO2 $INSTALL $EXPORT --vhd --version 2
  "import rc=$LASTEXITCODE"
}

Say "4. ${ZOO2}: strip the copied Claude login, probe"
Linux $ZOO2 'strip'

Say "5. code2 -> $ZOO2"
$launcher = @'
@echo off
REM code2 - the second VS Code instance, pinned to the Ubuntu-zoo2 distro (SCC-376 Phase 4).
REM Same isolated user-data-dir, same clone-sync as before; only where it lands changed.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.local\bin\vscode-clone-sync.ps1" >nul 2>&1
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=/home/dlohn/Sudo_Hatter_Command"
"C:\Microsoft VS Code\bin\code.cmd" --user-data-dir "%USERPROFILE%\vscode-isolated" --new-window --remote wsl+Ubuntu-zoo2 "%TARGET%"
'@
if ((Test-Path $CODE2) -and -not (Test-Path "$CODE2.bak-scc376")) { Copy-Item $CODE2 "$CODE2.bak-scc376" }
[IO.File]::WriteAllText($CODE2, ($launcher -replace "`r?`n", "`r`n"), (New-Object System.Text.ASCIIEncoding))
"written: $CODE2 (previous launcher kept as code2.cmd.bak-scc376)"

Say '6. REPORT - paste everything from "== 0." down to here back to the operator (it is also in %TEMP%\phase4_pc.log)'
& wsl.exe --list --verbose
& $CODE --list-extensions --show-versions 2>$null | Select-String 'remote-wsl|zoo-code|claude-code|ms-python.python'
'code2 launcher, last line:'; Get-Content $CODE2 | Select-Object -Last 1
Stop-Transcript | Out-Null
Write-Host @'

BY HAND - the Phase 4 gate. Two instances, two distros; a change in one must not move the other.
  1. Windows Terminal, Ubuntu tab:   code ~/Sudo_Hatter_Command
       -> instance 1 opens; its title bar ends "[WSL: Ubuntu]"
  2. PowerShell:                     code2
       -> instance 2 opens with the green ZOO-2 badge; its title bar ends "[WSL: Ubuntu-zoo2]"
  3. Zoo Code starts EMPTY inside each distro (its provider profile lived on the Windows side).
     In the Windows Zoo: Zoo Code > Settings > Export (once). In EACH WSL window: Zoo Code > Settings >
     Import that file. If there is no Export button, type the provider key once per window instead.
  4. Instance 2: in the Zoo chat, switch the model (the profile picker under the chat box).
     Ctrl+Shift+P > "Developer: Reload Window". The model you picked is still selected (the change stuck).
  5. Instance 1: Ctrl+Shift+P > "Developer: Reload Window". Open Zoo Code. The model is UNCHANGED.
  6. Reply with: gate PASS or FAIL, instance 2 model = ___, instance 1 model = ___, plus the report above.
'@
