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
    "Dan" + "iel",
    "dloh" + "neiss",
    "dlo" + "hn",
    "Sudos-" + "MacBook-Pro.local",
    "sudo" + "hatter",
    "Aviation" + "Chat",
    "Aviation" + " Chat",
    "AV" + "CH",
    "NEX" + "gen",
    "Sudo_Hatter" + "_Command",
    "Fresh_Workspace" + "_BMAD",
    "sudo" + "madhatter@gmail.com",
    "clean-" + "bmad",
    "sudo-command" + ".atlassian.net",
)

PRIVATE_PREFIX_LITERALS = ("Sul" + "ly", "Ig" + "or")
PRIVATE_WORD_LITERALS = ("S" + "CC",)

LIVE_TUTOR_FILES = (
    "README.md",
    "router.md",
    ".agents/rules/training-mode.md",
    ".agents/commands/smh-tour.md",
    ".agents/commands/smh-training.md",
    ".agents/skills/smh-tour/SKILL.md",
    ".agents/skills/smh-training/SKILL.md",
    ".agents/workflows/smh-tour.md",
    ".agents/workflows/smh-training.md",
    ".claude/skills/smh-tour/SKILL.md",
    ".claude/skills/smh-training/SKILL.md",
    ".opencode/commands/smh-tour.md",
    ".opencode/commands/smh-training.md",
)

MIRROR_PAIRS = (
    (".agents/commands/smh-tour.md", ".agents/workflows/smh-tour.md"),
    (".agents/commands/smh-training.md", ".agents/workflows/smh-training.md"),
    (".agents/commands/smh-tour.md", ".opencode/commands/smh-tour.md"),
    (".agents/commands/smh-training.md", ".opencode/commands/smh-training.md"),
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
    "docs/doc-graph.md",
    "docs/doc-graph.json",
    "_artifacts/_memory/MEMORY.md",
    "_artifacts/_memory/README.md",
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


def _decoded_texts(path: Path) -> list[str]:
    try:
        payload = path.read_bytes()
    except OSError:
        return []
    texts: list[str] = []
    for encoding in ("utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
        try:
            text = payload.decode(encoding)
        except UnicodeError:
            continue
        if text not in texts:
            texts.append(text)
    return texts


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

    for authored_rel, mirror_rel in MIRROR_PAIRS:
        authored = root / authored_rel
        mirror = root / mirror_rel
        if authored.is_file() and mirror.is_file() and authored.read_bytes() != mirror.read_bytes():
            errors.append(f"generated tutor mirror drifted from authored command: {mirror_rel}")

    for rel in (
        ".agents/skills/smh-tour/SKILL.md",
        ".agents/skills/smh-training/SKILL.md",
        ".claude/skills/smh-tour/SKILL.md",
        ".claude/skills/smh-training/SKILL.md",
    ):
        launcher = _text(root / rel, errors)
        command_name = Path(rel).parent.name
        expected = f".agents/commands/{command_name}.md"
        if launcher and expected not in launcher:
            errors.append(f"generated tutor launcher points at the wrong command: {rel}")

    if (root / ".agents/jira.conf").exists():
        errors.append("fresh shell must not contain active .agents/jira.conf")
    if (root / ".claude/worktrees").exists():
        errors.append("fresh shell contains source checkout worktrees")

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

    operator_profile = _text(root / ".agents/rules/operator-profile.md", errors)
    if "trigger: always_on" not in operator_profile:
        errors.append("exported floor operator profile is not marked always-on")

    jira_rule = _text(root / ".agents/rules/jira.md", errors)
    if not all(token in jira_rule for token in ("No binding means no board", "JIRA_SITE", "JIRA_KEYS")):
        errors.append("exported Jira rule does not enforce the generic binding-first contract")
    if "two team-managed projects" in jira_rule or "P=YOUR_KEY" in jira_rule or "P=PROJECT" in jira_rule:
        errors.append("exported Jira rule retains source-specific board topology")

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
    if "validate_teaching_edition.py ." not in tour or "do **not** substitute" not in tour:
        errors.append("tour does not use the generated-shell validator at Stop 1")

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
    source_jira_key = "S" + "CC"
    source_jira_site = "sudo-" + "command.atlassian.net"
    if f'JIRA_KEYS="{source_jira_key}"' in example or source_jira_site in example:
        errors.append("Jira example leaks the source command center binding")
    assignments = [line.strip() for line in example.splitlines()
                   if line.strip() and not line.lstrip().startswith("#") and "=" in line]
    if assignments != [
        'JIRA_SITE="https://YOUR-SITE.atlassian.net"',
        'JIRA_KEYS="YOUR_JIRA_KEY"',
    ]:
        errors.append("Jira example contains active or extra assignments")
    sites = re.findall(r"https://([^/\s]+\.atlassian\.net)", example, flags=re.IGNORECASE)
    if sites != ["YOUR-SITE.atlassian.net"]:
        errors.append("Jira example contains a non-placeholder or extra site")

    training_command = _text(root / ".agents/commands/smh-training.md", errors)
    if "Walk upward from the current directory" not in training_command:
        errors.append("training control has no archive-safe command-center root fallback")
    if not all(
        phrase in training_command
        for phrase in ("source export machinery", "deliberately absent")
    ):
        errors.append("training control cannot recreate its sentinel without source export files")

    scripts_index = _text(root / ".agents/scripts/INDEX.md", errors)
    if "source distribution only; absent from the generated shell" not in scripts_index.lower():
        errors.append("exported scripts index presents the source-only exporter as available")
    if "- `export-teaching-edition.ps1`" in scripts_index:
        errors.append("exported scripts inventory lists the absent source-only exporter")

    sync_manifest = _text(root / ".agents/.sync-manifest.json", errors)
    if "sentry-security-team-" in sync_manifest:
        errors.append("sync ownership manifest claims an excluded incident door")

    new_project = _text(root / ".agents/scripts/new-project.ps1", errors)
    if "scaffold commit failed" not in new_project or "until HEAD exists" not in new_project:
        errors.append("new-project scaffold can report success without a first commit")
    new_project_command = _text(root / ".agents/commands/smh-new-project.md", errors)
    if not all(
        token in new_project_command
        for token in ("JIRA_SITE", "JIRA_KEYS", "acli jira auth status")
    ):
        errors.append("new-project command does not validate the optional Jira site/key binding")

    sop = _text(root / "docs/_scc_sops_prds/workflows_testing_SOP.md", errors)
    command_index = _text(root / ".agents/commands/INDEX.md", errors)
    workflow_index = _text(root / ".agents/workflows/INDEX.md", errors)
    for token in ("sentry-security-team-project", "sentry_error_response_team.md"):
        for rel, text in (
            ("docs/_scc_sops_prds/workflows_testing_SOP.md", sop),
            (".agents/commands/INDEX.md", command_index),
            (".agents/workflows/INDEX.md", workflow_index),
        ):
            if token in text:
                errors.append(f"fresh-shell catalog advertises excluded incident asset: {rel}")

    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", sop):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        local_target = target.split("#", 1)[0]
        if local_target and not (root / "docs/_scc_sops_prds" / local_target).resolve().exists():
            errors.append(f"live SOP contains dead local link: {target}")

    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        for literal in PRIVATE_LITERALS:
            if literal.lower() in rel.lower():
                errors.append(f"private literal in exported path: {rel} ({literal})")
        for prefix in PRIVATE_PREFIX_LITERALS:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(prefix)}", rel, flags=re.IGNORECASE):
                errors.append(f"private alias in exported path: {rel} ({prefix})")
        for word in PRIVATE_WORD_LITERALS:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(word)}(?![A-Za-z0-9])", rel):
                errors.append(f"source Jira key in exported path: {rel}")
        for text in _decoded_texts(path):
            for literal in PRIVATE_LITERALS:
                if literal.lower() in text.lower():
                    errors.append(f"private literal in exported content: {rel} ({literal})")
            for prefix in PRIVATE_PREFIX_LITERALS:
                if re.search(rf"(?<![A-Za-z0-9]){re.escape(prefix)}", text,
                             flags=re.IGNORECASE):
                    errors.append(f"private alias in exported content: {rel} ({prefix})")
        try:
            operational_text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            operational_text = ""
        for word in PRIVATE_WORD_LITERALS:
            if re.search(
                rf"(?<![A-Za-z0-9]){re.escape(word)}(?![A-Za-z0-9])",
                operational_text,
            ):
                errors.append(f"source Jira key in exported content: {rel}")

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
