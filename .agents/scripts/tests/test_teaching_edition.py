#!/usr/bin/env python3
"""Fresh-export and mutation checks for the shareable teaching edition (SCC-280)."""

from __future__ import annotations

import json
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
            findings = validate(target) if target.exists() else ["target was not created"]
            c.check("generated shell validates", not findings, " | ".join(findings[:8]))
            c.check("export has no git history", not (target / ".git").exists())

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
            proc.returncode == 0 and "LEAK MATCHER SELF-TEST VALID (8/8)" in transcript,
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
            fixture = temp / "source"
            fixture.mkdir()
            (fixture / ".env").write_text(
                "API_KEY=secretvalue12345 # production\n", encoding="utf-8"
            )
            (fixture / "payload.txt").write_text("secretvalue12345\n", encoding="utf-8")
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
                and "secretvalue12345" not in redaction_transcript,
                redaction_transcript,
            )

        original_exporter = exporter.read_text(encoding="utf-8")
        mutants = {
            "git-prefix boundary mutant is killed": original_exporter.replace(
                "$candidatePath.StartsWith($directoryPrefix, [StringComparison]::OrdinalIgnoreCase)",
                "$candidatePath.StartsWith($directoryPath, [StringComparison]::OrdinalIgnoreCase)",
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
