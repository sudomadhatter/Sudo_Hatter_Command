#!/usr/bin/env python3
"""
env_master.py — Cross-platform master .env bundle engine.

Bundles and restores secret environment files and credentials across Sudo_Hatter_Command
and all child projects under Projects/.

Usage:
  python env_master.py --export                     # Bundle all env/auth_keys into master.env
  python env_master.py --restore                    # Unpack master.env into target files
  python env_master.py --restore --dry-run          # Preview restore without writing
  python env_master.py --verify-only                # Validate master.env format and safety
"""

import argparse
import os
import subprocess
import re
import shutil
import sys
from pathlib import Path

DEFAULT_VAULT_REL = "docs/migrations/auth_keys/_secrets/master.env"
ENV_FILENAMES = {".env", ".env.local", ".env.production"}
EXCLUDE_DIR_PATTERNS = {"node_modules", ".venv", "venv", "worktrees", ".git"}
EXCLUDE_FILE_PATTERNS = (".example", ".bak", ".pre-restore.bak")


def get_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    # Script lives at docs/migrations/scripts/env_master.py -> walk up 3 levels
    return Path(__file__).resolve().parent.parent.parent.parent


def _git_tracks(path: Path) -> bool:
    """True when git tracks `path` in whichever repo/submodule contains it.

    The bundle carries what git deliberately does NOT — a tracked file restored from it would
    silently overwrite a committed one (measured 2026-09-03: AGY's `frontend/.env.production` is
    tracked, and a restore dirtied the tree; SCC-384). Not-a-repo and untracked both return False.
    """
    try:
        rc = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path.name],
            cwd=path.parent, capture_output=True, text=True, check=False,
        ).returncode
    except OSError:
        return False
    return rc == 0


def discover_source_files(root: Path) -> list[str]:
    """Discovers all real .env and auth_keys files relative to the repository root.

    Skips anything git tracks — see `_git_tracks`.
    """
    found: set[str] = set()

    # 1. Root .env
    root_env = root / ".env"
    if root_env.is_file():
        found.add(".env")

    # 2. Projects directory
    projects_dir = root / "Projects"
    if projects_dir.is_dir():
        for root_path, dirs, files in os.walk(projects_dir):
            # Skip ignored directories in place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_PATTERNS]
            for file in files:
                # Skip sample / backup files
                if any(file.endswith(ext) for ext in EXCLUDE_FILE_PATTERNS):
                    continue

                full_path = Path(root_path) / file
                rel_path = full_path.relative_to(root).as_posix()

                is_env = file in ENV_FILENAMES
                is_auth_key = "auth_keys" in full_path.parts

                if (is_env or is_auth_key) and not _git_tracks(full_path):
                    found.add(rel_path)

    return sorted(found)


def export_master(root: Path, vault_path: Path, dry_run: bool = False) -> int:
    """Gathers all secret files and writes the master vault bundle."""
    targets = discover_source_files(root)
    if not targets:
        print("[ERROR] No secret or .env files found to export.", file=sys.stderr)
        return 1

    lines: list[str] = [
        "# ================================================================",
        "# MASTER ENV — Sudo_Hatter_Command lobby + all sub-projects",
        f"# Exported via env_master.py (Python {sys.version.split()[0]})",
        "# NEVER COMMIT THIS FILE. It contains live credentials.",
        "#",
        "# Format: each original file appears verbatim between a marker pair:",
        "#   # >>> FILE: <path relative to lobby root>",
        "#   ...content...",
        "#   # <<< END FILE: <same path>",
        "# Restore with docs/migrations/scripts/Restore-EnvMaster.ps1 or env_master.py",
        "#",
        f"# MANIFEST ({len(targets)} files):",
    ]
    for t in targets:
        lines.append(f"#   - {t}")
    lines.extend(["# ================================================================", ""])

    for t in targets:
        src = root / Path(t)
        try:
            content = src.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[WARN] Failed to read {t}: {e}", file=sys.stderr)
            continue

        lines.append(f"# >>> FILE: {t}")
        lines.append(content if content.endswith("\n") else content + "\n")
        lines.append(f"# <<< END FILE: {t}")
        lines.append("")

    bundle_text = "\n".join(lines)

    if dry_run:
        print(f"[DRY-RUN] Would write {vault_path} ({len(targets)} files bundled):")
        for t in targets:
            print(f"  - {t}")
        return 0

    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_path.write_text(bundle_text, encoding="utf-8")
    if os.name != "nt":
        vault_path.chmod(0o600)

    print(f"Wrote {vault_path} ({len(targets)} files bundled):")
    for t in targets:
        print(f"  - {t}")
    return 0


def parse_master_bundle(master_path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """Parses a master.env bundle into a list of (relative_path, content) pairs."""
    if not master_path.is_file():
        return [], [f"Master file not found: {master_path}"]

    content = master_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    entries: list[tuple[str, str]] = []
    errors: list[str] = []
    current_file: str | None = None
    buffer: list[str] = []

    file_marker_re = re.compile(r"^# >>> FILE:\s*(.+)$")
    end_marker_re = re.compile(r"^# <<< END FILE:\s*(.*)$")

    for idx, line in enumerate(lines, 1):
        file_match = file_marker_re.match(line)
        end_match = end_marker_re.match(line)

        if file_match:
            if current_file is not None:
                errors.append(f"Line {idx}: New FILE marker started before END of '{current_file}'")
            current_file = file_match.group(1).strip()
            buffer = []
        elif end_match:
            if current_file is None:
                errors.append(f"Line {idx}: END marker without a preceding FILE marker")
            else:
                end_file = end_match.group(1).strip()
                if end_file and end_file != current_file:
                    errors.append(f"Line {idx}: END marker '{end_file}' does not match FILE '{current_file}'")
                
                # Safety checks on path
                if current_file.startswith("/") or ":" in current_file:
                    errors.append(f"Unsafe absolute path: '{current_file}'")
                elif ".." in current_file.split("/"):
                    errors.append(f"Unsafe path traversal: '{current_file}'")
                else:
                    entries.append((current_file, "\n".join(buffer) + "\n"))

                current_file = None
                buffer = []
        elif current_file is not None:
            buffer.append(line)

    if current_file is not None:
        errors.append(f"Master file ended mid-block: '{current_file}' was never closed with END FILE")

    return entries, errors


def verify_master(master_path: Path) -> int:
    """Verifies format, markers, and safety of a master.env bundle."""
    entries, errors = parse_master_bundle(master_path)
    print(f"=== Master Env Verification ===")
    print(f"File: {master_path}")
    print(f"Found {len(entries)} valid file entries.")

    if errors:
        print(f"\n[FAIL] {len(errors)} error(s) found:")
        for err in errors:
            print(f"  • {err}")
        return 1

    print("\nManifest of files:")
    for path_rel, text in entries:
        print(f"  [OK] {path_rel} ({len(text)} bytes)")
    print("\nVerification PASSED: All markers matched, all paths safe.")
    return 0


def restore_master(root: Path, master_path: Path, dry_run: bool = False) -> int:
    """Unpacks a master.env bundle into the workspace."""
    entries, errors = parse_master_bundle(master_path)
    if errors:
        print(f"[ERROR] Cannot restore invalid master file ({len(errors)} errors):", file=sys.stderr)
        for err in errors:
            print(f"  • {err}", file=sys.stderr)
        return 1

    written = 0
    unchanged = 0
    backed_up = 0

    print(f"Lobby root : {root}")
    print(f"Master     : {master_path}")
    if dry_run:
        print("MODE       : DRY RUN — nothing will be written\n")
    else:
        print("")

    for rel_path, content in entries:
        dest = root / Path(rel_path)
        
        # Check existing content
        if dest.is_file():
            try:
                existing = dest.read_text(encoding="utf-8", errors="replace")
                if existing == content:
                    print(f"  unchanged  {rel_path}")
                    unchanged += 1
                    continue
            except Exception:
                pass

        if dry_run:
            if dest.is_file():
                print(f"  [DRY-RUN] WOULD back up + overwrite  {rel_path}")
                backed_up += 1
            else:
                print(f"  [DRY-RUN] WOULD create              {rel_path}")
            written += 1
            continue

        # Real restore
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file():
            backup = dest.with_name(dest.name + ".pre-restore.bak")
            shutil.copy2(dest, backup)
            print(f"  backed up  {rel_path} -> {backup.name}")
            backed_up += 1

        dest.write_text(content, encoding="utf-8")
        if os.name != "nt":
            try:
                dest.chmod(0o600)
            except OSError:
                pass

        print(f"  restored   {rel_path}")
        written += 1

    mode_str = " (dry run)" if dry_run else ""
    print(f"\nDone{mode_str}. {written} file(s) written/updated, {unchanged} unchanged, {backed_up} backed up.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Master .env bundle and restore engine.")
    parser.add_argument("--root", type=str, default=None, help="Root path of Sudo_Hatter_Command")
    parser.add_argument("--master-path", type=str, default=None, help="Path to master.env file")
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--export", action="store_true", help="Bundle source env files into master.env")
    action_group.add_argument("--restore", action="store_true", help="Restore master.env into workspace")
    action_group.add_argument("--verify-only", action="store_true", help="Validate master.env syntax without writes")
    
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying filesystem")

    args = parser.parse_args()
    root = get_repo_root(args.root)
    master_path = Path(args.master_path).resolve() if args.master_path else (root / DEFAULT_VAULT_REL)

    if args.export:
        return export_master(root, master_path, dry_run=args.dry_run)
    elif args.verify_only:
        return verify_master(master_path)
    elif args.restore:
        return restore_master(root, master_path, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
