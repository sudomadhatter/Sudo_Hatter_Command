#!/usr/bin/env python3
"""Fresh-export and mutation checks for the shareable teaching edition (SCC-280)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from _harness import Cases, TempDir

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(SCRIPTS))

from validate_teaching_edition import validate


def git_seed(root: Path) -> None:
    """Make a synthetic export fixture a real git repo with one commit.

    ⛔ THE EXPORTER FAILS CLOSED WITHOUT THIS, ON PURPOSE (SCC-456). It writes
    `.teaching-edition-source` carrying the source sha, and it STOPS rather than ship an unstamped
    tree - an export nobody can date is the exact defect the stamp exists to end, and a tree that
    silently loses its provenance is indistinguishable from one that never had it. The real source
    is always a git repo, so the fixtures are made to match the real thing rather than the
    guarantee being weakened to match the fixtures.
    """
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    for args in (
        ["init", "-q", "-b", "main"],
        ["config", "user.email", "fixture@example.invalid"],
        ["config", "user.name", "Fixture"],
        ["add", "-A"],
        ["commit", "-q", "-m", "fixture"],
    ):
        subprocess.run(["git", *args], cwd=str(root), check=True, capture_output=True, text=True,
                       env=env)


def _fenced_blocks(body: str) -> list[str]:
    """Every fenced code block of a door body, as separate strings.

    ⛔ COUNTING ACROSS THE WHOLE DOOR IS NOT A GUARD. F9 first asserted
    `instructions.count("LOBBY=$(git rev-parse --show-toplevel)") >= 2` over the concatenated
    instructions; the door has THREE such lines, so deleting the one that matters left the count
    at 2 and the row green (measured - mutant R4 survived). The property is per-BLOCK: the block
    that deletes files must re-derive its own paths, because a block is what a shell actually
    receives.
    """
    out, cur, inside = [], [], False
    for line in body.splitlines():
        if line.startswith("```"):
            if inside:
                out.append("\n".join(cur))
                cur = []
            inside = not inside
            continue
        if inside:
            cur.append(line)
    return out


def _uncommented_instructions(body: str) -> str:
    """Only the fenced COMMAND lines of a door body.

    The door warns about `rm -rf`, `--force` and `git init` by name, so a bare substring search
    over the whole file would fail on the door's own safety notes - a guard that fires on the
    warning rather than the act. Fences are what an agent actually runs.
    """
    out, inside = [], False
    for line in body.splitlines():
        if line.startswith("```"):
            inside = not inside
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    c = Cases("test_teaching_edition")
    manifest = SCRIPTS / "teaching-edition" / "lobby.manifest.json"
    exporter = SCRIPTS / "export-teaching-edition.ps1"

    # ⛔ EVERY CASE IN THIS FILE SHELLS `pwsh`, SO THIS FILE MAKES POWERSHELL A HARD DEPENDENCY
    # OF THE WHOLE LOBBY SUITE. `run_all.py:53` auto-discovers `test_*.py`, so the moment this
    # file landed, a machine without PowerShell ran the enforcement suite and got a RED for a
    # reason that had nothing to do with the lane it was working. `ubuntu-latest` ships pwsh and
    # so does this workstation; a fresh clone elsewhere is what this guards.
    #
    # ⛔ AND IT REPORTS A FAILING ROW, NOT A SKIP. A row that skips and scores green is the exact
    # trap SCC-441 measured on the server side — a skipped job reports Success and SATISFIES the
    # requirement, so the gate is advertised and never ran. The absence is therefore NAMED and
    # NON-PASSING: the suite tells you the export is unverified here rather than implying it is
    # verified. Install PowerShell, or read this row as the unverified export it is.
    # ⛔ THE `which` TEST IS OUTSIDE A BLOCK AND THE ROW IS INSIDE ONE, AND THAT SPLIT IS LOAD-
    # BEARING. `test_suite_runner.py`'s ORPHAN case refuses any `c.check` that is not under a
    # `c.block` guard, because an orphan row runs even when `--case` selected nothing — which
    # turns a typo'd filter from a clean exit 3 into a run that reports a result. So the row
    # lives in a block. The early return does NOT, or a filtered run on a machine without
    # PowerShell would skip the guard and then raise FileNotFoundError inside whichever block
    # the filter did select.
    if shutil.which("pwsh") is None:
        if c.block("pwsh · PowerShell is required to verify the teaching-edition export"):
            c.check(
                "pwsh · PowerShell is required to verify the teaching-edition export",
                False,
                "pwsh not found on PATH - the export engine is PowerShell and NOTHING in this "
                "file ran. This is reported as a failure, never a skip: a green here would "
                "claim the export was verified on a machine that cannot run it. Install "
                "PowerShell 7 (https://aka.ms/powershell) and re-run.",
            )
        return c.finish()

    if c.block("A · a real fresh export satisfies the teaching-shell contract"):
        with TempDir() as temp:
            target = temp / "command-center"
            proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(exporter),
                    "-Manifest",
                    str(manifest),
                    "-Target",
                    str(target),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            transcript = (proc.stdout or "") + (proc.stderr or "")
            c.check("exporter exits zero", proc.returncode == 0, transcript[-2000:])
            c.check(
                "successful transcript withholds private source path",
                str(REPO) not in transcript and "sudohatter" not in transcript.lower(),
                transcript[-2000:],
            )
            findings = validate(target) if target.exists() else ["target was not created"]
            c.check("generated shell validates", not findings, " | ".join(findings[:8]))
            shipped_validator = target / ".agents" / "scripts" / "validate_teaching_edition.py"
            shipped_proc = subprocess.run(
                [sys.executable, str(shipped_validator), str(target)],
                cwd=target,
                capture_output=True,
                text=True,
                errors="replace",
            )
            c.check(
                "generated shell validates with its own shipped validator",
                shipped_proc.returncode == 0
                and "TEACHING EDITION VALID" in (shipped_proc.stdout or ""),
                (shipped_proc.stdout or "") + (shipped_proc.stderr or ""),
            )
            c.check("export has no git history", not (target / ".git").exists())
            c.check(
                "export writes no unscanned sibling report",
                not target.with_name(target.name + ".export-report.txt").exists(),
            )

            if target.exists():
                sentinel = target / ".training-mode"
                canonical_sentinel = (
                    SCRIPTS
                    / "teaching-edition"
                    / "replacements"
                    / "training-mode-sentinel"
                ).read_bytes()
                training_command = (
                    target / ".agents" / "commands" / "smh-training.md"
                ).read_text(encoding="utf-8")
                embedded_match = re.search(
                    r"```text\n(?P<sentinel>.*?)\n\s*```", training_command, flags=re.DOTALL
                )
                embedded_sentinel = (
                    (textwrap.dedent(embedded_match.group("sentinel")) + "\n").encode("utf-8")
                    if embedded_match
                    else b""
                )
                c.check(
                    "training on restores the committed sentinel bytes",
                    sentinel.read_bytes() == canonical_sentinel
                    and embedded_sentinel == canonical_sentinel,
                )
                subprocess.run(["git", "init", "-q"], cwd=target, check=True)
                subprocess.run(["git", "add", ".gitignore", ".training-mode"], cwd=target, check=True)
                subprocess.run(
                    [
                        "git", "-c", "user.name=Teaching Test",
                        "-c", "user.email=teaching@example.invalid",
                        "commit", "-qm", "initial teaching shell",
                    ],
                    cwd=target,
                    check=True,
                )
                (target / ".training-mode-off").write_text(
                    "training disabled locally\n", encoding="utf-8"
                )
                status = subprocess.run(
                    ["git", "status", "--short", "--", ".training-mode", ".training-mode-off"],
                    cwd=target, capture_output=True, text=True,
                    check=True,
                ).stdout
                c.check("training off override leaves a clean clone", status == "", status)
                (target / ".training-mode-off").unlink()

                readme = target / "README.md"
                original = readme.read_text(encoding="utf-8") if readme.is_file() else ""
                readme.write_text(original + "\nRun /sudo-tour now.\n", encoding="utf-8")
                retired_findings = validate(target)
                c.check(
                    "retired-command mutant is killed",
                    any("retired /sudo" in finding for finding in retired_findings),
                    " | ".join(retired_findings[:8]),
                )
                readme.write_text(original, encoding="utf-8")

                generated_tour = target / ".opencode" / "commands" / "smh-tour.md"
                generated_original = generated_tour.read_text(encoding="utf-8")
                generated_tour.write_text(
                    generated_original + "\nRun /sudo-tour now.\n", encoding="utf-8"
                )
                generated_findings = validate(target)
                c.check(
                    "generated tutor-mirror mutant is killed",
                    any(
                        "retired /sudo" in finding and ".opencode/commands/smh-tour.md" in finding
                        for finding in generated_findings
                    ),
                    " | ".join(generated_findings[:8]),
                )
                generated_tour.write_text(generated_original, encoding="utf-8")

                generated_tour.write_text("", encoding="utf-8")
                empty_mirror_findings = validate(target)
                c.check(
                    "empty generated tutor mirror is rejected",
                    any("mirror drifted" in finding for finding in empty_mirror_findings),
                    " | ".join(empty_mirror_findings[:8]),
                )
                generated_tour.write_text(generated_original, encoding="utf-8")

                readme.write_text(original + '\nRun ["/sudo-tour"] now.\n', encoding="utf-8")
                quoted_retired_findings = validate(target)
                c.check(
                    "quoted Markdown retired-command mutant is killed",
                    any("retired /sudo" in finding for finding in quoted_retired_findings),
                    " | ".join(quoted_retired_findings[:8]),
                )
                readme.write_text(original, encoding="utf-8")

                active_jira = target / ".agents" / "jira.conf"
                active_jira.write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
                jira_findings = validate(target)
                c.check(
                    "active-Jira mutant is killed",
                    any("active .agents/jira.conf" in finding for finding in jira_findings),
                    " | ".join(jira_findings[:8]),
                )
                active_jira.unlink()

                jira_example = target / ".agents" / "jira.conf.example"
                jira_original = jira_example.read_text(encoding="utf-8")
                jira_example.write_text(
                    jira_original + '\nREAL_SITE="https://private.atlassian.net"\n',
                    encoding="utf-8",
                )
                extra_jira_findings = validate(target)
                c.check(
                    "extra Jira binding mutant is killed",
                    any("extra assignments" in finding or "extra site" in finding
                        for finding in extra_jira_findings),
                    " | ".join(extra_jira_findings[:8]),
                )
                jira_example.write_text(jira_original, encoding="utf-8")

                private_probe = target / "privacy-probe.txt"
                private_probe.write_text(
                    "Daniel AviationChat AVCH SCC dlohneiss dlohn Sudos-MacBook-Pro.local "
                    "sudomadhatter@gmail.com clean-bmad SullySessionTelemetry igor_temp\n",
                    encoding="utf-8",
                )
                private_findings = validate(target)
                c.check(
                    "shipped validator retains the source privacy denylist",
                    any("private literal" in finding for finding in private_findings)
                    and any("private alias" in finding for finding in private_findings),
                    " | ".join(private_findings[:12]),
                )
                c.check(
                    "shipped validator rejects the source Jira key",
                    any("source Jira key" in finding for finding in private_findings),
                    " | ".join(private_findings[:12]),
                )

                private_probe.write_text(
                    "sudomadhatter@gmail.com\n", encoding="utf-8"
                )
                email_only_findings = validate(target)
                c.check(
                    "shipped validator independently rejects the source account literal",
                    any("private literal" in finding for finding in email_only_findings),
                    " | ".join(email_only_findings[:8]),
                )
                private_probe.write_text("clean-bmad\n", encoding="utf-8")
                legacy_name_only_findings = validate(target)
                c.check(
                    "shipped validator independently rejects the legacy skeleton literal",
                    any("private literal" in finding
                        for finding in legacy_name_only_findings),
                    " | ".join(legacy_name_only_findings[:8]),
                )
                private_probe.unlink()

                private_path_probe = target / "docs" / "SCC-private.md"
                private_path_probe.write_text("sanitized content\n", encoding="utf-8")
                private_path_findings = validate(target)
                c.check(
                    "shipped validator rejects the source Jira key in a path",
                    any("source Jira key in exported path" in finding
                        for finding in private_path_findings),
                    " | ".join(private_path_findings[:12]),
                )
                private_path_probe.unlink()

                nested_worktree = target / ".claude" / "worktrees" / "foreign-lane"
                nested_worktree.mkdir(parents=True)
                (nested_worktree / "private.txt").write_text("private lane\n", encoding="utf-8")
                nested_findings = validate(target)
                c.check(
                    "shipped validator rejects nested source worktrees",
                    any("source checkout worktrees" in finding for finding in nested_findings),
                    " | ".join(nested_findings[:8]),
                )
                (nested_worktree / "private.txt").unlink()
                nested_worktree.rmdir()
                nested_worktree.parent.rmdir()

                private_probe.write_bytes("Daniel AviationChat\n".encode("utf-32-be"))
                utf32_findings = validate(target)
                c.check(
                    "shipped validator scans UTF-32BE content",
                    any("private literal" in finding for finding in utf32_findings),
                    " | ".join(utf32_findings[:8]),
                )
                private_probe.unlink()

                mcp_files = (
                    target / ".mcp.json",
                    target / ".opencode" / "mcp.json",
                    target / ".claude" / "mcp.json",
                )
                mcp_text = "\n".join(
                    path.read_text(encoding="utf-8") for path in mcp_files if path.is_file()
                )
                # ⛔ THIS ASSERTS THE PROPERTY, NOT THE OLD LITERAL. It used to require
                # `--workspace=.` once per file, which was right when each server was launched
                # with an explicit workspace path and the danger was that path being the
                # author's. SCC-432 rebuilt these configs from `.agents/tools/connections.json`
                # as `npx` launches with no workspace argument at all, so the literal could
                # never match again and the row failed on a correct export. The thing worth
                # guarding was never the flag — it is that NO absolute path from this machine
                # reaches a clone, so that is what is checked, on every root the three shells
                # actually use. A literal that has outlived its config shape is a stale spec
                # failing an honest export, not a guard catching anything.
                leaked = [
                    frag for frag in ("/Users/", "/home/", "C:\\Users", "/private/var/")
                    if frag in mcp_text
                ]
                c.check(
                    "exported MCP configs carry no machine-absolute path",
                    mcp_text.strip() != "" and not leaked,
                    f"leaked={leaked}\n{mcp_text}",
                )

                operator_profile = (
                    target / ".agents" / "rules" / "operator-profile.md"
                ).read_text(encoding="utf-8")
                c.check(
                    "exported floor profile remains always-on",
                    "trigger: always_on" in operator_profile,
                    operator_profile[:500],
                )

                jira_rule = (target / ".agents" / "rules" / "jira.md").read_text(
                    encoding="utf-8"
                )
                c.check(
                    "exported Jira rule is generic and binding-first",
                    "No binding means no board" in jira_rule
                    and "JIRA_SITE" in jira_rule
                    and "JIRA_KEYS" in jira_rule
                    and "two team-managed projects" not in jira_rule
                    and "P=YOUR_KEY" not in jira_rule
                    and "P=PROJECT" not in jira_rule,
                    jira_rule[:2500],
                )

                new_project_command = (
                    target / ".agents" / "commands" / "smh-new-project.md"
                ).read_text(encoding="utf-8")
                c.check(
                    "new-project hand-off validates Jira site and key together",
                    "JIRA_SITE" in new_project_command
                    and "JIRA_KEYS" in new_project_command
                    and "acli jira auth status" in new_project_command,
                    new_project_command,
                )

    if c.block("B · leak matcher is literal, boundary-safe, and mutation-proven"):
        proc = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(exporter), "-SelfTestLeakMatcher"],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
        )
        transcript = (proc.stdout or "") + (proc.stderr or "")
        c.check(
            "leak matcher self-test passes",
            proc.returncode == 0 and "LEAK MATCHER SELF-TEST VALID (12/12)" in transcript,
            transcript,
        )

        inside_proc = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-File",
                str(exporter),
                "-Manifest",
                str(manifest),
                "-Target",
                str(REPO / "docs" / "teaching-output"),
                "-WhatIf",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            errors="replace",
        )
        inside_transcript = (inside_proc.stdout or "") + (inside_proc.stderr or "")
        c.check(
            "target inside source is refused before enumeration",
            inside_proc.returncode != 0 and "outside the source tree" in inside_transcript,
            inside_transcript,
        )

        with TempDir() as temp:
            fixture_source = temp / "source"
            fixture_source.mkdir()
            (fixture_source / "payload.txt").write_text("safe\n", encoding="utf-8")
            fixture_manifest = fixture_source / "manifest.json"
            fixture_manifest.write_text(
                json.dumps({
                    "name": "symlink containment probe",
                    "source": ".",
                    "include": ["payload.txt"],
                    "leakScan": {"literals": [], "wordLiterals": []},
                }),
                encoding="utf-8",
            )
            nested = fixture_source / "nested-output"
            nested.mkdir()
            outside_link = temp / "outside-name"
            os.symlink(nested, outside_link)
            symlink_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter), "-Manifest",
                 str(fixture_manifest), "-Target", str(outside_link), "-WhatIf"],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            symlink_transcript = (symlink_proc.stdout or "") + (symlink_proc.stderr or "")
            c.check(
                "symlink target resolving inside source is refused",
                symlink_proc.returncode != 0 and "outside the source tree" in symlink_transcript,
                symlink_transcript,
            )

        with TempDir() as temp:
            fixture_source = temp / "source"
            fixture_source.mkdir()
            outside = temp / "outside-secret.txt"
            outside.write_text("not part of the source\n", encoding="utf-8")
            os.symlink(outside, fixture_source / "payload.txt")
            fixture_manifest = fixture_source / "manifest.json"
            fixture_manifest.write_text(
                json.dumps({
                    "name": "include symlink probe",
                    "source": ".",
                    "include": ["payload.txt"],
                    "leakScan": {"literals": [], "wordLiterals": []},
                }),
                encoding="utf-8",
            )
            include_link_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter), "-Manifest",
                 str(fixture_manifest), "-Target", str(temp / "public"), "-WhatIf"],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            include_link_transcript = (
                (include_link_proc.stdout or "") + (include_link_proc.stderr or "")
            )
            c.check(
                "include symlink resolving outside source is refused",
                include_link_proc.returncode != 0
                and "outside the source tree" in include_link_transcript,
                include_link_transcript,
            )

        with TempDir() as temp:
            fixture_source = temp / "source"
            fixture_source.mkdir()
            (fixture_source / "payload.txt").write_text("safe\n", encoding="utf-8")
            outside = temp / "machine-local.json"
            outside.write_text('{"local": true}\n', encoding="utf-8")
            os.symlink(outside, fixture_source / "settings.local.json")
            fixture_manifest = fixture_source / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "excluded symlink probe",
                        "source": ".",
                        "include": ["."],
                        "exclude": ["settings.local.json", "manifest.json"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            excluded_link_proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(exporter),
                    "-Manifest",
                    str(fixture_manifest),
                    "-Target",
                    str(temp / "public"),
                    "-WhatIf",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            excluded_link_transcript = (
                (excluded_link_proc.stdout or "") + (excluded_link_proc.stderr or "")
            )
            c.check(
                "explicitly excluded machine-local symlink is skipped without dereferencing",
                excluded_link_proc.returncode == 0,
                excluded_link_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            (fixture / ".env").write_text(
                "API_KEY='secret\\qwerty123456' # production\n", encoding="utf-8"
            )
            (fixture / "payload.txt").write_bytes(
                "secret\\qwerty123456\n".encode("utf-32-be")
            )
            fixture_manifest = fixture / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "redaction probe",
                        "source": ".",
                        "include": ["payload.txt"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_seed(fixture)
            redaction_proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(exporter),
                    "-Manifest",
                    str(fixture_manifest),
                    "-Target",
                    str(temp / "public"),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            redaction_transcript = (redaction_proc.stdout or "") + (redaction_proc.stderr or "")
            c.check(
                "inline-comment secret is blocked without echoing it",
                redaction_proc.returncode != 0
                and "LEAK SCAN FAILED" in redaction_transcript
                and "qwerty123456" not in redaction_transcript,
                redaction_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            short_secret = "A7x!pQ9z2#"
            (fixture / ".env").write_text(
                f"API_KEY={short_secret}\nPUBLIC_MODE=testing\n", encoding="utf-8"
            )
            (fixture / "payload.txt").write_text(
                f"copied credential: {short_secret}\n", encoding="utf-8"
            )
            fixture_manifest = fixture / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "short secret probe",
                        "source": ".",
                        "include": ["payload.txt"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_seed(fixture)
            short_secret_proc = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(exporter),
                    "-Manifest", str(fixture_manifest),
                    "-Target", str(temp / "public"),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            short_secret_transcript = (
                (short_secret_proc.stdout or "") + (short_secret_proc.stderr or "")
            )
            c.check(
                "short value from a secret-named dotenv key is blocked",
                short_secret_proc.returncode != 0
                and "LEAK SCAN FAILED" in short_secret_transcript
                and short_secret not in short_secret_transcript,
                short_secret_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            (fixture / ".env").write_text(
                "API_KEY=abc\nBYPASS_SSL=true\n", encoding="utf-8"
            )
            (fixture / "payload.txt").write_text("safe\n", encoding="utf-8")
            fixture_manifest = fixture / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "tiny secret probe",
                        "source": ".",
                        "include": ["payload.txt"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_seed(fixture)
            tiny_secret_proc = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(exporter),
                    "-Manifest", str(fixture_manifest),
                    "-Target", str(temp / "public"),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            tiny_secret_transcript = (
                (tiny_secret_proc.stdout or "") + (tiny_secret_proc.stderr or "")
            )
            c.check(
                "tiny secret is refused without treating BYPASS as a password key",
                tiny_secret_proc.returncode != 0
                and "too short for safe leak matching" in tiny_secret_transcript
                and "abc" not in tiny_secret_transcript,
                tiny_secret_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=fixture, check=True)
            (fixture / "payload.txt").write_text("safe\n", encoding="utf-8")
            fixture_manifest = fixture / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "source git probe",
                        "source": ".",
                        "include": ["."],
                        "exclude": ["manifest.json"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_seed(fixture)
            source_git_proc = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(exporter),
                    "-Manifest", str(fixture_manifest),
                    "-Target", str(temp / "public"),
                    "-WhatIf",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            source_git_transcript = (
                (source_git_proc.stdout or "") + (source_git_proc.stderr or "")
            )
            c.check(
                "source git history is refused even when a manifest tries to include it",
                source_git_proc.returncode != 0
                and "Source .git cannot be exported" in source_git_transcript,
                source_git_transcript,
            )

            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "git-as-source probe",
                        "source": ".git",
                        "include": ["config"],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_source_proc = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(exporter),
                    "-Manifest", str(fixture_manifest),
                    "-Target", str(temp / "public-source"),
                    "-WhatIf",
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            git_source_transcript = (
                (git_source_proc.stdout or "") + (git_source_proc.stderr or "")
            )
            c.check(
                "a manifest cannot select source git metadata as its source root",
                git_source_proc.returncode != 0
                and "Source .git cannot be exported" in git_source_transcript,
                git_source_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            (fixture / "payload.txt").write_text("safe\n", encoding="utf-8")
            (fixture / "replacement.txt").write_text("replacement\n", encoding="utf-8")
            victim = temp / "victim.txt"
            victim.write_text("keep\n", encoding="utf-8")
            fixture_manifest = fixture / "manifest.json"
            fixture_manifest.write_text(
                json.dumps(
                    {
                        "name": "transform traversal probe",
                        "source": ".",
                        "include": ["payload.txt"],
                        "transforms": [
                            {"path": "../victim.txt", "replaceWith": "replacement.txt"}
                        ],
                        "leakScan": {"literals": [], "wordLiterals": []},
                    }
                ),
                encoding="utf-8",
            )
            git_seed(fixture)
            traversal_proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(exporter),
                    "-Manifest",
                    str(fixture_manifest),
                    "-Target",
                    str(temp / "public"),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                errors="replace",
            )
            traversal_transcript = (
                (traversal_proc.stdout or "") + (traversal_proc.stderr or "")
            )
            c.check(
                "transform destination traversal is refused without overwriting its sibling",
                traversal_proc.returncode != 0
                and "outside the export target" in traversal_transcript
                and victim.read_text(encoding="utf-8") == "keep\n",
                traversal_transcript,
            )

        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            missing_manifest = fixture / "manifest.json"
            missing_manifest.write_text(
                json.dumps({
                    "name": "missing include probe",
                    "source": ".",
                    "include": ["required-but-missing"],
                    "leakScan": {"literals": [], "wordLiterals": []},
                }),
                encoding="utf-8",
            )
            git_seed(fixture)
            missing_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter), "-Manifest",
                 str(missing_manifest), "-Target", str(temp / "public"), "-WhatIf"],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            missing_transcript = (missing_proc.stdout or "") + (missing_proc.stderr or "")
            c.check(
                "missing declared include fails closed",
                missing_proc.returncode != 0 and "Required include path missing" in missing_transcript,
                missing_transcript,
            )

        original_exporter = exporter.read_text(encoding="utf-8")
        mutants = {
            "git-prefix boundary mutant is killed": original_exporter.replace(
                "$candidatePath.StartsWith($directoryPrefix, $comparison)",
                "$candidatePath.StartsWith($directoryPath, $comparison)",
                1,
            ),
            "wildcard-secret matcher mutant is killed": original_exporter.replace(
                "return $Text.IndexOf($Needle, [StringComparison]::OrdinalIgnoreCase) -ge 0",
                'return $Text -like "*$Needle*"',
                1,
            ),
        }
        with TempDir() as temp:
            for label, mutant in mutants.items():
                mutant_path = temp / (label.split()[0] + ".ps1")
                mutant_path.write_text(mutant, encoding="utf-8")
                mutant_proc = subprocess.run(
                    ["pwsh", "-NoProfile", "-File", str(mutant_path), "-SelfTestLeakMatcher"],
                    cwd=REPO,
                    capture_output=True,
                    text=True,
                    errors="replace",
                )
                c.check(
                    label,
                    mutant != original_exporter and mutant_proc.returncode != 0,
                    (mutant_proc.stdout or "") + (mutant_proc.stderr or ""),
                )

    if c.block("C · obsolete two-export source is gone"):
        c.check(
            "retired skeleton manifest absent",
            not (SCRIPTS / "teaching-edition" / "skeleton.manifest.json").exists(),
        )
        c.check(
            "retired skeleton replacements absent",
            not (SCRIPTS / "teaching-edition" / "replacements" / "skeleton-README.md").exists()
            and not (
                SCRIPTS
                / "teaching-edition"
                / "replacements"
                / "skeleton-active-context.md"
            ).exists(),
        )

    if c.block("D · new-project clones a safe named skeleton and fails honestly"):
        with TempDir() as temp:
            shell = temp / "command-center"
            scripts = shell / ".agents" / "scripts"
            projects = shell / "Projects"
            scripts.mkdir(parents=True)
            projects.mkdir()
            local_script = scripts / "new-project.ps1"
            shutil.copy2(SCRIPTS / "new-project.ps1", local_script)
            (shell / "docs" / "migrations" / "scripts").mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                REPO / "docs" / "migrations" / "scripts" / "Arm-HooksInclude.ps1",
                shell / "docs" / "migrations" / "scripts" / "Arm-HooksInclude.ps1",
            )

            skeleton = temp / "skeleton"
            skeleton.mkdir()
            (skeleton / "README.md").write_text("# Local skeleton\n", encoding="utf-8")
            (skeleton / ".githooks").mkdir()
            (skeleton / ".githooks" / ".gitkeep").write_text("", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=skeleton, check=True)
            subprocess.run(["git", "add", "README.md", ".githooks/.gitkeep"],
                           cwd=skeleton, check=True)
            identity_env = os.environ.copy()
            identity_env.update(
                {
                    "GIT_AUTHOR_NAME": "Teaching Test",
                    "GIT_AUTHOR_EMAIL": "teaching@example.invalid",
                    "GIT_COMMITTER_NAME": "Teaching Test",
                    "GIT_COMMITTER_EMAIL": "teaching@example.invalid",
                }
            )
            subprocess.run(
                ["git", "commit", "-qm", "local skeleton"],
                cwd=skeleton,
                env=identity_env,
                check=True,
            )

            success = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(local_script),
                    "-Name", "First_Project", "-SkeletonUrl", str(skeleton),
                ],
                cwd=shell,
                env=identity_env,
                capture_output=True,
                text=True,
                errors="replace",
            )
            success_transcript = (success.stdout or "") + (success.stderr or "")
            created = projects / "First_Project"
            head = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=created if created.is_dir() else shell,
                capture_output=True,
                text=True,
            )
            hook_path = subprocess.run(
                ["git", "config", "--get", "core.hooksPath"],
                cwd=created if created.is_dir() else shell,
                capture_output=True,
                text=True,
            )
            c.check(
                "named local skeleton becomes an independent project with hooks and HEAD",
                success.returncode == 0
                and (created / "README.md").is_file()
                and head.returncode == 0
                and hook_path.stdout.strip() == ".githooks",
                success_transcript,
            )
            c.check(
                "successful scaffold prints project-local optional Jira setup",
                "cd Projects/First_Project" in success_transcript
                and "JIRA_SITE" in success_transcript
                and "JIRA_KEYS" in success_transcript
                and "acli jira auth status" in success_transcript,
                success_transcript,
            )

        with TempDir() as temp:
            shell = temp / "command-center"
            scripts = shell / ".agents" / "scripts"
            projects = shell / "Projects"
            scripts.mkdir(parents=True)
            projects.mkdir()
            local_script = scripts / "new-project.ps1"
            shutil.copy2(SCRIPTS / "new-project.ps1", local_script)
            skeleton = temp / "skeleton"
            skeleton.mkdir()
            (skeleton / "README.md").write_text("safe\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=skeleton, check=True)
            subprocess.run(["git", "add", "README.md"], cwd=skeleton, check=True)
            subprocess.run(
                [
                    "git", "-c", "user.name=Teaching Test",
                    "-c", "user.email=teaching@example.invalid",
                    "commit", "-qm", "local skeleton",
                ],
                cwd=skeleton,
                check=True,
            )
            unsafe = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(local_script),
                    "-Name", "../escape", "-SkeletonUrl", str(skeleton),
                ],
                cwd=shell,
                capture_output=True,
                text=True,
                errors="replace",
            )
            unsafe_transcript = (unsafe.stdout or "") + (unsafe.stderr or "")
            c.check(
                "unsafe project name is refused before clone",
                unsafe.returncode != 0
                and "portable folder name" in unsafe_transcript
                and not (shell / "escape").exists(),
                unsafe_transcript,
            )
            reserved = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(local_script),
                    "-Name", "CON.txt", "-SkeletonUrl", str(skeleton),
                ],
                cwd=shell,
                capture_output=True,
                text=True,
                errors="replace",
            )
            reserved_transcript = (reserved.stdout or "") + (reserved.stderr or "")
            c.check(
                "Windows reserved device basename is refused before clone",
                reserved.returncode != 0
                and "portable folder name" in reserved_transcript
                and not (projects / "CON.txt").exists(),
                reserved_transcript,
            )

        with TempDir() as temp:
            shell = temp / "command-center"
            scripts = shell / ".agents" / "scripts"
            projects = shell / "Projects"
            scripts.mkdir(parents=True)
            projects.mkdir()
            local_script = scripts / "new-project.ps1"
            shutil.copy2(SCRIPTS / "new-project.ps1", local_script)
            missing_dest = projects / "Missing_Project"
            clone_failure = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(local_script),
                    "-Name", "Missing_Project",
                    "-SkeletonUrl", str(temp / "does-not-exist"),
                ],
                cwd=shell,
                capture_output=True,
                text=True,
                errors="replace",
            )
            clone_failure_transcript = (
                (clone_failure.stdout or "") + (clone_failure.stderr or "")
            )
            c.check(
                "clone failure is reported without a project directory",
                clone_failure.returncode != 0
                and "skeleton clone failed" in clone_failure_transcript
                and not missing_dest.exists(),
                clone_failure_transcript,
            )

        with TempDir() as temp:
            shell = temp / "command-center"
            scripts = shell / ".agents" / "scripts"
            projects = shell / "Projects"
            scripts.mkdir(parents=True)
            projects.mkdir()
            local_script = scripts / "new-project.ps1"
            shutil.copy2(SCRIPTS / "new-project.ps1", local_script)
            (shell / "docs" / "migrations" / "scripts").mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                REPO / "docs" / "migrations" / "scripts" / "Arm-HooksInclude.ps1",
                shell / "docs" / "migrations" / "scripts" / "Arm-HooksInclude.ps1",
            )
            skeleton = temp / "skeleton"
            skeleton.mkdir()
            (skeleton / "README.md").write_text("safe\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=skeleton, check=True)
            subprocess.run(["git", "add", "README.md"], cwd=skeleton, check=True)
            subprocess.run(
                [
                    "git", "-c", "user.name=Teaching Test",
                    "-c", "user.email=teaching@example.invalid",
                    "commit", "-qm", "local skeleton",
                ],
                cwd=skeleton,
                check=True,
            )
            no_identity_env = os.environ.copy()
            no_identity_env.update(
                {
                    "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": str(temp / "empty-gitconfig"),
                    "GIT_AUTHOR_NAME": "",
                    "GIT_AUTHOR_EMAIL": "",
                    "GIT_COMMITTER_NAME": "",
                    "GIT_COMMITTER_EMAIL": "",
                }
            )
            commit_failure = subprocess.run(
                [
                    "pwsh", "-NoProfile", "-File", str(local_script),
                    "-Name", "No_Identity", "-SkeletonUrl", str(skeleton),
                ],
                cwd=shell,
                env=no_identity_env,
                capture_output=True,
                text=True,
                errors="replace",
            )
            failed_project = projects / "No_Identity"
            failed_head = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=failed_project if failed_project.is_dir() else shell,
                capture_output=True,
                text=True,
            )
            commit_failure_transcript = (
                (commit_failure.stdout or "") + (commit_failure.stderr or "")
            )
            c.check(
                "failed scaffold commit cannot be reported as a created project",
                commit_failure.returncode != 0
                and "scaffold commit failed" in commit_failure_transcript
                and failed_head.returncode != 0
                and "new-project: created" not in commit_failure_transcript,
                commit_failure_transcript,
            )

    if c.block("E · the export stamps its source, and fails closed when it cannot"):
        with TempDir() as temp:
            fixture = temp / "source"
            fixture.mkdir()
            (fixture / "payload.txt").write_text("hello\n", encoding="utf-8")
            (fixture / "manifest.json").write_text(
                json.dumps({"name": "stamp probe", "source": ".", "include": ["payload.txt"],
                            "leakScan": {"literals": [], "wordLiterals": []}}),
                encoding="utf-8",
            )
            git_seed(fixture)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(fixture),
                check=True, capture_output=True, text=True,
            ).stdout.strip()

            target = temp / "public"
            stamp_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter),
                 "-Manifest", str(fixture / "manifest.json"), "-Target", str(target)],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            stamp_transcript = (stamp_proc.stdout or "") + (stamp_proc.stderr or "")
            stamp_file = target / ".teaching-edition-source"
            # ⛔ rc IS NOT CHECKED HERE, and the reason is a fixture limit, not a soft assertion.
            # The exporter's last pass shells `<source>/.agents/scripts/validate_teaching_edition.py`
            # and throws when it is absent, so NO synthetic fixture can reach exit 0 - block A is
            # where a real manifest proves the whole run. What this case owns is the stamp, and the
            # stamp is proven by the file on disk plus the pass announcing itself.
            c.check("E1 · a real export writes .teaching-edition-source",
                    stamp_file.is_file() and "-- provenance --" in stamp_transcript,
                    stamp_transcript)

            body = stamp_file.read_text(encoding="utf-8") if stamp_file.is_file() else ""
            c.check("E2 · it carries the SOURCE tree's own HEAD, not some other sha",
                    f"source_commit: {head}" in body, f"head={head}\n{body}")

            # ⛔ THE STAMP SHIPS TO A PUBLIC REPO, so what it does NOT carry is the point. A branch
            # name, an author, a remote or an absolute path would each be a new leak surface on a
            # file that exists to be read by strangers. Three lines, three keys, nothing else.
            keys = sorted(ln.split(":", 1)[0] for ln in body.splitlines() if ln.strip())
            c.check("E3 · it carries ONLY a sha and two dates - no branch, author, remote or path",
                    keys == ["exported", "source_commit", "source_date"], f"keys={keys}\n{body}")

            # E4 - the fail-closed arm. Every other fixture in this file is git-seeded precisely
            # because the exporter refuses an unstampable tree; this is the case that proves the
            # refusal is real rather than an assumption the seeding hides.
            nogit = temp / "nogit"
            nogit.mkdir()
            (nogit / "payload.txt").write_text("hello\n", encoding="utf-8")
            (nogit / "manifest.json").write_text(
                json.dumps({"name": "unstampable probe", "source": ".",
                            "include": ["payload.txt"],
                            "leakScan": {"literals": [], "wordLiterals": []}}),
                encoding="utf-8",
            )
            nogit_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter),
                 "-Manifest", str(nogit / "manifest.json"), "-Target", str(temp / "public2")],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            nogit_transcript = (nogit_proc.stdout or "") + (nogit_proc.stderr or "")
            c.check("E4 · an unstampable source FAILS the export rather than shipping undated",
                    nogit_proc.returncode != 0
                    and "provenance stamp" in nogit_transcript,
                    nogit_transcript)

            # E5 - THE STAMP IS SCANNED LIKE EVERY OTHER BYTE, proven behaviourally rather than by
            # reading the pass order. The needle is the source sha's own first eight characters:
            # nothing else in this fixture contains them, so the ONLY file that can trip the scan
            # is the stamp. If the stamp were ever written AFTER the leak scan - which is the
            # natural way to write it, and a hole straight to a public repo - this export would
            # come back clean and this case would go red.
            scanned = temp / "source2"
            scanned.mkdir()
            (scanned / "payload.txt").write_text("nothing interesting\n", encoding="utf-8")
            (scanned / "manifest.json").write_text(
                json.dumps({"name": "stamp-is-scanned probe", "source": ".",
                            "include": ["payload.txt"],
                            "leakScan": {"literals": [], "wordLiterals": []}}),
                encoding="utf-8",
            )
            git_seed(scanned)
            scanned_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(scanned),
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            (scanned / "manifest.json").write_text(
                json.dumps({"name": "stamp-is-scanned probe", "source": ".",
                            "include": ["payload.txt"],
                            "leakScan": {"literals": [scanned_head[:8]], "wordLiterals": []}}),
                encoding="utf-8",
            )
            scanned_proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter),
                 "-Manifest", str(scanned / "manifest.json"), "-Target", str(temp / "public3")],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            scanned_transcript = (scanned_proc.stdout or "") + (scanned_proc.stderr or "")
            c.check("E5 · the stamp is written BEFORE the leak scan, so the scan sees it",
                    scanned_proc.returncode != 0
                    and "LEAK SCAN FAILED" in scanned_transcript,
                    scanned_transcript)

    if c.block("G · the overlay's four refusals, each one run"):
        # ⛔ THESE WERE UNPINNED WHILE TWO RECORDS CLAIMED THEY WERE PINNED - the manifest's own
        # comment said "Four properties, each pinned by a case in test_teaching_edition.py" and
        # the plan baked the same claim. Nothing asserted any of them. Every refusal below is a
        # way an unreviewed byte reaches a PUBLIC repo, so each is run, not read.
        def overlay_probe(temp: Path, label: str, entries: list, extra_files: dict) -> str:
            root = temp / label
            (root / "docs").mkdir(parents=True)
            (root / "docs" / "a.md").write_text("hi\n", encoding="utf-8")
            mdir = root / "tm"
            (mdir / "overlay").mkdir(parents=True)
            for rel, body in extra_files.items():
                f = mdir / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(body, encoding="utf-8")
            git_seed(root)
            (mdir / "m.json").write_text(json.dumps({
                "name": label, "source": "..", "include": ["docs"],
                "excludeAnywhere": [".git"], "overlay": entries,
                "leakScan": {"literals": ["ZZZNOMATCH"], "wordLiterals": []},
            }), encoding="utf-8")
            proc = subprocess.run(
                ["pwsh", "-NoProfile", "-File", str(exporter),
                 "-Manifest", str(mdir / "m.json"), "-Target", str(temp / (label + "-out"))],
                cwd=REPO, capture_output=True, text=True, errors="replace",
            )
            return f"rc={proc.returncode}\n" + (proc.stdout or "") + (proc.stderr or "")

        with TempDir() as temp:
            out = overlay_probe(temp, "g1",
                                [{"from": "overlay/gone.md", "path": "docs/x.md"}], {})
            c.check("G1 · a missing overlay source FAILS the export",
                    "rc=0" not in out and "Overlay source missing" in out, out[:600])

            out = overlay_probe(temp, "g2",
                                [{"from": "overlay/a.md", "path": "docs/a.md"}],
                                {"overlay/a.md": "tutor\n"})
            c.check("G2 · a collision with the copy pass FAILS the export",
                    "rc=0" not in out and "Overlay collision" in out, out[:600])

            out = overlay_probe(temp, "g3", [],
                                {"overlay/stray.md": "nobody declared me\n"})
            c.check("G3 · an UNDECLARED file under overlay/ FAILS the export",
                    "rc=0" not in out and "Undeclared" in out, out[:600])

            # ⛔ G4 is the one a review found live: `from` was joined to the manifest folder with
            # no containment test, so `../../../.env` pulled any file on disk into a PUBLIC
            # export - and the leak scan does not save you, because it matches a fixed needle
            # list, not "content that should not be here".
            (temp / "outside.txt").write_text("OUT-OF-TREE-PRIVATE\n", encoding="utf-8")
            out = overlay_probe(temp, "g4",
                                [{"from": "../../outside.txt", "path": "docs/pulled.md"}], {})
            c.check("G4 · a source OUTSIDE the manifest folder FAILS the export",
                    "rc=0" not in out and "resolves outside the manifest folder" in out,
                    out[:600])

    if c.block("F · the publish recipe DELETES, and only what git tracks"):
        door = REPO / ".agents" / "commands" / "smh-publish-teaching-edition.md"
        door_body = door.read_text(encoding="utf-8") if door.is_file() else ""
        c.check("F0 · the publish door exists", bool(door_body), str(door))

        # ⛔ THE RECIPE IS EXTRACTED FROM THE DOOR AND RUN, never re-typed here. A test that
        # re-implements the clear proves only that the test can delete a file; it would stay green
        # while the door said `rm -rf *`. This runs whatever the door actually tells an agent to
        # run, so editing the door to something destructive changes what this case executes.
        clear_line = next(
            (ln.strip() for ln in door_body.splitlines()
             if ln.strip().startswith("git ls-files") and "rm -f" in ln),
            "",
        )
        c.check("F1 · the door carries a tracked-only clear command", bool(clear_line), door_body[:400])

        if clear_line:
            with TempDir() as temp:
                pub = temp / "published"
                pub.mkdir()
                (pub / "retired-door.md").write_text("a command nobody still has\n", encoding="utf-8")
                (pub / "kept.md").write_text("old\n", encoding="utf-8")
                git_seed(pub)
                # The reader's own state: untracked, and it must survive.
                (pub / "my-notes.txt").write_text("mine\n", encoding="utf-8")

                export_dir = temp / "fresh"
                export_dir.mkdir()
                (export_dir / "kept.md").write_text("new\n", encoding="utf-8")

                subprocess.run(["bash", "-c", clear_line], cwd=str(pub), check=True,
                               capture_output=True, text=True)
                subprocess.run(["bash", "-c", f'cp -a "{export_dir}/." "{pub}/"'],
                               cwd=str(pub), check=True, capture_output=True, text=True)

                c.check("F2 · a tracked file the export no longer carries is GONE",
                        not (pub / "retired-door.md").exists(),
                        "this is the whole defect: a copy-over adds and overwrites but never "
                        "removes, so 84 deleted files kept shipping to every team clone")
                c.check("F3 · a file the export DOES carry is refreshed, not lost",
                        (pub / "kept.md").is_file()
                        and (pub / "kept.md").read_text(encoding="utf-8").strip() == "new",
                        "the clear must not outlive the copy")
                c.check("F4 · the reader's UNTRACKED file survives",
                        (pub / "my-notes.txt").is_file(),
                        "tracked-only is the guard: a glob delete would take the reader's own work")
                c.check("F5 · the repository itself survives",
                        (pub / ".git").is_dir(),
                        "aimed one level wrong this eats .git and the history every clone depends on")

        # ⛔ F7 IS A REAL DEFECT THIS DOOR SHIPPED WITH, caught on its FIRST live run. The
        # published repo is checked out on `main`, so `git push origin HEAD` landed the entire
        # refresh directly on `main` of a PUBLIC repo with no PR and no review - and
        # `gh pr create --head main` cannot open one either, so the door could not complete.
        # A branch has to be cut before anything is committed.
        instructions = _uncommented_instructions(door_body)

        # ⛔ ORDER, NOT PRESENCE. This row said "before it commits" and asserted only that the
        # string existed somewhere - a source-contains assert, which cannot see ORDER, which is
        # the trap `tests-must-gate-for-real` names by name. Measured: reordering the door to
        # commit first left this row green. Compare positions.
        _sw = instructions.find("git switch -c")
        _ci = instructions.find("git commit -m")
        c.check("F7 · the door cuts a branch BEFORE it commits",
                _sw != -1 and _ci != -1 and _sw < _ci,
                f"switch@{_sw} commit@{_ci} - without the branch the push lands on `main` of a "
                "public repo, unreviewed")
        c.check("F8 · ...and never pushes a bare HEAD from the checked-out branch",
                not any(s in instructions for s in
                        ("git push origin HEAD", "git push -u origin HEAD", "HEAD:main")),
                "on this repo HEAD is `main`; the push must name the publish branch")

        # ⛔ THE DESTRUCTIVE BLOCK MUST BE SAFE IN A FRESH SHELL. `$LOBBY` and `$SCRATCH` are set
        # in an earlier block; a shell that does not inherit them computes
        # `PUB=/Projects/sudo-command-center`, fails the `cd`, and runs the tracked-file delete in
        # whatever directory it is standing in - measured, it deletes the LOBBY. Every fresh
        # terminal and most tool calls are that shell.
        # Every assertion below is about THE BLOCK THAT DELETES, not about the door as a whole -
        # a shell receives one block, and a safety line in a different block is not in scope when
        # the delete runs.
        destructive = next((b for b in _fenced_blocks(door_body) if "git ls-files -z" in b), "")
        c.check("F9a · the destructive command lives in exactly one fenced block",
                sum(1 for b in _fenced_blocks(door_body) if "git ls-files -z" in b) == 1,
                "two copies means one of them is unguarded")
        c.check("F9 · THAT block re-derives its own paths",
                "LOBBY=$(git rev-parse --show-toplevel)" in destructive,
                f"it must not depend on a variable an earlier block set. block={destructive!r}")
        c.check("F10 · ...and aborts on the first failure",
                "set -euo pipefail" in destructive,
                "without it a failed `cd` is followed by the delete running where it landed")
        c.check("F11 · ...and refuses a target that is not the published repo",
                "*/Projects/sudo-command-center)" in destructive
                and '[ -d "$PUB/.git" ]' in destructive,
                "the wrong directory must be refused before anything is deleted")
        c.check("F12 · ...and refuses an empty or absent export",
                '[ -d "$SCRATCH/.agents" ]' in destructive,
                "an unset SCRATCH makes the copy source `/.` - the filesystem root")

        # ⛔ A FAILED EXPORT MUST NOT REACH THE COPY. The only thing between a FAILED leak scan
        # and the wipe-and-copy was a sentence telling the reader to check the log.
        c.check("F13 · a failed export stops the run before Step 2",
                "EXPORT REFUSED" in instructions
                and "grep -q 'TEACHING EDITION VALID'" in instructions,
                "a leak hit must end the run mechanically, not by prose")

        # The three shapes that would each be irreversible on a PUBLIC repo with live clones.
        for banned, why in (
            ("rm -rf", "a glob delete takes the reader's untracked files and can reach .git"),
            ("--force", "a force-push breaks every team clone silently at their next pull"),
            ("git init", "re-initialising discards the history every team clone is pinned to"),
        ):
            c.check(f"F6 · the door never says `{banned}` as an instruction",
                    banned not in _uncommented_instructions(door_body),
                    why)


    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
