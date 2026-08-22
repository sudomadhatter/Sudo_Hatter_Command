#!/usr/bin/env python3
"""Validate a generated command-center teaching shell.

The exporter's privacy scan answers "did a private token escape?". This validator answers the
separate product question: "did we export the current tutor, with an empty project/Jira shell?"
It is deliberately stdlib-only so a new owner can run it before installing anything.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PRIVATE_LITERALS = (
    "Daniel",
    "dlohneiss",
    "sudo" + "hatter",
    "AviationChat",
    "NEXgen",
    "Sudo_Hatter_Command",
    "Fresh_Workspace_BMAD",
    "sudo-command.atlassian.net",
)

LIVE_TUTOR_FILES = (
    "README.md",
    "router.md",
    ".agents/rules/training-mode.md",
    ".agents/commands/smh-tour.md",
    ".agents/commands/smh-training.md",
)

REQUIRED_PATHS = (
    ".training-mode",
    ".agents/commands/smh-tour.md",
    ".agents/commands/smh-training.md",
    ".agents/rules/training-mode.md",
    ".agents/scripts/validate_teaching_edition.py",
    ".agents/jira.conf.example",
    ".agents/skills/smh-tour/SKILL.md",
    ".agents/skills/smh-training/SKILL.md",
    ".agents/workflows/smh-tour.md",
    ".agents/workflows/smh-training.md",
    ".claude/skills/smh-tour/SKILL.md",
    ".claude/skills/smh-training/SKILL.md",
    ".opencode/commands/smh-tour.md",
    ".opencode/commands/smh-training.md",
    "docs/_scc_sops_prds/workflows_testing_SOP.md",
)

RETIRED_PATHS = (
    ".agents/commands/sudo-tour.md",
    ".agents/commands/training.md",
    ".agents/skills/sudo-tour/SKILL.md",
    ".agents/workflows/sudo-tour.md",
    ".agents/workflows/training.md",
    ".claude/commands/sudo-tour.md",
    ".claude/commands/training.md",
    ".claude/skills/sudo-tour/SKILL.md",
    ".opencode/commands/sudo-tour.md",
    ".opencode/commands/training.md",
)


def _text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {path}: {exc}")
        return ""


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    if not root.is_dir():
        return [f"export root does not exist: {root}"]

    for rel in REQUIRED_PATHS:
        if not (root / rel).is_file():
            errors.append(f"required teaching path missing: {rel}")

    for rel in RETIRED_PATHS:
        if (root / rel).exists():
            errors.append(f"retired tutor door survived: {rel}")

    if (root / ".agents/jira.conf").exists():
        errors.append("fresh shell must not contain active .agents/jira.conf")

    projects = root / "Projects"
    if not projects.is_dir():
        errors.append("Projects/ shell directory missing")
    else:
        payload = [p.relative_to(projects).as_posix() for p in projects.rglob("*")
                   if p.name != ".gitkeep"]
        if payload:
            errors.append("fresh shell already contains project payload: " + ", ".join(payload[:5]))

    readme = _text(root / "README.md", errors)
    readme_needs = (
        "<chosen-command-center-name>",
        "sudo-project-skeleton",
        "Projects/<name>",
        "/smh-tour",
        "/smh-new-project",
        "no Jira board",
    )
    for token in readme_needs:
        if token not in readme:
            errors.append(f"README missing onboarding contract: {token}")
    if "validate_teaching_edition.py ." not in readme or "tests/run_all.py" in readme:
        errors.append("README does not use the generated shell's own validation gate")
    if "Projects/<name>/.agents/jira.conf" not in readme:
        errors.append("README does not bind optional Jira inside the named project")

    training = _text(root / ".agents/rules/training-mode.md", errors)
    if "docs/_scc_sops_prds/workflows_testing_SOP.md" not in training:
        errors.append("training rule is not bound to the live SOP")
    if "re-open" not in training.lower() and "open the current" not in training.lower():
        errors.append("training rule does not require a fresh SOP read")

    tour = _text(root / ".agents/commands/smh-tour.md", errors)
    for token in (
        "/smh-new-project",
        "sudo-project-skeleton",
        "Projects/<name>",
        "/cicd-write-story-tests",
        "/cicd-dev-story-tests",
        "/cicd-code-review",
        "/smh-quick-dev",
        "/smh-close-task-merge-tree",
        "/cicd-push-e2e",
    ):
        if token not in tour:
            errors.append(f"tour missing current workflow hand-off: {token}")
    if "Projects/<name>/.agents/jira.conf" not in tour:
        errors.append("tour does not bind optional Jira inside the named project")

    for rel in LIVE_TUTOR_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = _text(path, errors)
        if re.search(r"(?<![A-Za-z0-9])\/sudo-[a-z]", text, flags=re.MULTILINE):
            errors.append(f"live tutor surface teaches retired /sudo-* command: {rel}")
        if "main_debug" in text:
            errors.append(f"live tutor surface teaches retired main_debug branch: {rel}")

    example = _text(root / ".agents/jira.conf.example", errors)
    if "YOUR_JIRA_KEY" not in example or "YOUR-SITE.atlassian.net" not in example:
        errors.append("Jira example is not an inert site/key template")
    if 'JIRA_KEYS="SCC"' in example or "sudo-command.atlassian.net" in example:
        errors.append("Jira example leaks the source command center binding")

    training_command = _text(root / ".agents/commands/smh-training.md", errors)
    if "walk upward from the current directory" not in training_command:
        errors.append("training control has no archive-safe command-center root fallback")
    if "source export machinery is deliberately absent" not in training_command:
        errors.append("training control cannot recreate its sentinel without source export files")

    scripts_index = _text(root / ".agents/scripts/INDEX.md", errors)
    if "source distribution only; absent from the generated shell" not in scripts_index.lower():
        errors.append("exported scripts index presents the source-only exporter as available")

    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        for literal in PRIVATE_LITERALS:
            if literal.lower() in rel.lower():
                errors.append(f"private literal in exported path: {rel} ({literal})")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for literal in PRIVATE_LITERALS:
            if literal.lower() in text.lower():
                errors.append(f"private literal in exported content: {rel} ({literal})")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="generated teaching-shell root")
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print(f"TEACHING EDITION INVALID ({len(errors)} finding(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print("TEACHING EDITION VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
