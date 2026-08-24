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

    if c.block("D · new-project clones a safe named skeleton and fails honestly"):
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

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
