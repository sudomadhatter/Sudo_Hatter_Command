Why: SCC-376 moves the PC's working environment into WSL2 / Ubuntu and, in its Phase 5, strips every Windows-shaped allow rule out of the lobby's Claude and Zoo fences (20 rows out by exact match, 3 Unix twins in, the git -C wildcard rules respelled) so ONE file drives both machines. AGY carries its own .claude/settings.json and the two copies differ - git diff --no-index returns 1, 111 insertions / 267 deletions, measured 2026-09-02 - which fires .agents/rules/port-checklist.md: all six checks are due, and a lobby ticket cannot carry them because cross-repo work takes a ticket per repo. Opened when SCC-376 Phase 4 closed, as that plan said it would.

## Plan
- [ ] Sequencing - starts AFTER SCC-376 Phase 5 lands on main; the lobby's LANDED file is the source of the port, never the lane's draft
- [ ] Port section first - answer the six port-checklist questions with commands, in the plan, before a line is written: git paths used as git gave them; printf not echo for operator-facing lines; verify the FILE not $?; no .agents/rules path a thin repo lacks; python3 vs python and per-machine hooksPath; hooks stay repo-local and the work carries THIS repo's key
- [ ] Windows rows OUT of AGY's .claude/settings.json by EXACT match (never prefix - dirname must survive), the Unix twins IN for pytest / ruff / the firebase emulator via .venv/bin, and the git -C wildcard rules respelled so no wildcard sits before the subcommand
- [ ] Zoo side stays with AVCH-114 (tracked allow rules, the zoo-code fence, the .roo front door) - not duplicated here; if AVCH-114 lands first, its fence gets the same Windows-row pass in this ticket
- [ ] Both machines - the emulator tiers run green from inside Ubuntu (JAVA_HOME from ~/.profile, Node 22) and on the Mac; totals certified at the shipping SHA
- [ ] Gate - AGY's gate suites green, run bare; one real Claude workload in AGY inside Ubuntu completes with zero prompts

## Done
(filled at close-out)

## Files
- Opened from: _artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/implementation_plan.md - https://github.com/sudomadhatter/Sudo_Hatter_Command/blob/main/_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/implementation_plan.md
- Port checklist (lobby): .agents/rules/port-checklist.md
