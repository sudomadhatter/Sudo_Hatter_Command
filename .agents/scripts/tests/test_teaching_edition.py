#!/usr/bin/env python3
"""Fresh-export and mutation checks for the shareable teaching edition (SCC-280)."""

from __future__ import annotations

import subprocess
import sys
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

                active_jira = target / ".agents" / "jira.conf"
                active_jira.write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
                jira_findings = validate(target)
                c.check(
                    "active-Jira mutant is killed",
                    any("active .agents/jira.conf" in finding for finding in jira_findings),
                    " | ".join(jira_findings[:8]),
                )
                active_jira.unlink()

    if c.block("B · obsolete two-export source is gone"):
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
