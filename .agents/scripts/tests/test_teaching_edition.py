#!/usr/bin/env python3
"""Fresh-export and mutation checks for the shareable teaching edition (SCC-280)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from _harness import Cases, TempDir

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(SCRIPTS))

from validate_teaching_edition import validate


def main() -> int:
    c = Cases("test_teaching_edition")
    manifest = SCRIPTS / "teaching-edition" / "lobby.manifest.json"
    exporter = SCRIPTS / "export-teaching-edition.ps1"

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
                    "SullySessionTelemetry igor_temp\n",
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
                private_probe.unlink()

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
                    target / ".antigravity" / "mcp.json",
                )
                mcp_text = "\n".join(
                    path.read_text(encoding="utf-8") for path in mcp_files if path.is_file()
                )
                c.check(
                    "exported MCP workspaces are clone-relative",
                    mcp_text.count("--workspace=.") == len(mcp_files)
                    and "/Users/" not in mcp_text,
                    mcp_text,
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

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
