#!/usr/bin/env python3
"""
test_env_master.py — Unit and integration tests for env_master.py (SCC-39).

Tests discovery, formatting, marker parsing, security guards (path traversal),
restore idempotency, and backup creation.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_SCRIPTS = SCRIPTS_DIR.parent.parent / "docs" / "migrations" / "scripts"
sys.path.insert(0, str(MIGRATIONS_SCRIPTS))

import env_master


class TestCheck:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, desc: str, condition: bool, extra: str = ""):
        if condition:
            print(f"[PASS] {desc}")
            self.passed += 1
        else:
            print(f"[FAIL] {desc} {extra}".strip())
            self.failed += 1

    def finish(self) -> int:
        print(f"\n-- {self.passed}/{self.passed + self.failed} passed --")
        return 0 if self.failed == 0 else 1


def main() -> int:
    print("== test_env_master (SCC-39) ==")
    c = TestCheck()

    temp_dir = Path(tempfile.mkdtemp(prefix="test_env_master_"))
    try:
        # 1. Setup mock workspace tree
        (temp_dir / ".env").write_text("LOBBY_KEY=secret_lobby_val\n", encoding="utf-8")
        (temp_dir / ".env.example").write_text("LOBBY_KEY=\n", encoding="utf-8")

        proj_a = temp_dir / "Projects" / "ProjectA" / "backend"
        proj_a.mkdir(parents=True)
        (proj_a / ".env").write_text("PROJ_A_KEY=val_a\n", encoding="utf-8")
        (proj_a / ".env.bak").write_text("OLD_KEY=old\n", encoding="utf-8")

        proj_b_auth = temp_dir / "Projects" / "ProjectB" / "auth_keys"
        proj_b_auth.mkdir(parents=True)
        (proj_b_auth / "service-account.json").write_text('{"type": "service_account"}\n', encoding="utf-8")
        (proj_b_auth / ".env.example").write_text("SAMPLE=1\n", encoding="utf-8")

        # Mock node_modules that should be ignored
        ignored_nm = temp_dir / "Projects" / "ProjectA" / "node_modules" / "pkg"
        ignored_nm.mkdir(parents=True)
        (ignored_nm / ".env").write_text("IGNORE_ME=1\n", encoding="utf-8")

        # A project that is a git repo with a TRACKED .env.production (AGY's real shape, SCC-384)
        # and an untracked one beside it — only the untracked file may enter the bundle.
        import subprocess
        proj_c = temp_dir / "Projects" / "ProjectC"
        (proj_c / "frontend").mkdir(parents=True)
        (proj_c / "frontend" / ".env.production").write_text("PUBLIC_URL=https://x\n", encoding="utf-8")
        (proj_c / "frontend" / ".env.local").write_text("SECRET=1\n", encoding="utf-8")
        for cmd in (["git", "init", "-q"], ["git", "add", "frontend/.env.production"],
                    ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "SCC-384 fixture"]):
            subprocess.run(cmd, cwd=proj_c, check=True, capture_output=True)

        # ── Test 1: Discovery ────────────────────────────────────────────────
        discovered = env_master.discover_source_files(temp_dir)
        c.check("skips a git-TRACKED .env.production", "Projects/ProjectC/frontend/.env.production" not in discovered)
        c.check("keeps the untracked .env.local beside it", "Projects/ProjectC/frontend/.env.local" in discovered)
        c.check("discovers root .env", ".env" in discovered)
        c.check("discovers project backend .env", "Projects/ProjectA/backend/.env" in discovered)
        c.check("discovers auth_keys service-account.json", "Projects/ProjectB/auth_keys/service-account.json" in discovered)
        c.check("ignores node_modules .env", "Projects/ProjectA/node_modules/pkg/.env" not in discovered)
        c.check("ignores .env.example files", not any(f.endswith(".example") for f in discovered))
        c.check("ignores .bak files", not any(f.endswith(".bak") for f in discovered))
        c.check("total discovered count matches expected", len(discovered) == 4, f"got {len(discovered)}")

        # ── Test 2: Export ───────────────────────────────────────────────────
        vault_file = temp_dir / "master.env"
        rc = env_master.export_master(temp_dir, vault_file)
        c.check("export_master returns 0", rc == 0)
        c.check("master.env file created", vault_file.is_file())

        vault_text = vault_file.read_text(encoding="utf-8")
        c.check("master.env contains manifest header", "# MANIFEST (4 files):" in vault_text)
        c.check("master.env contains root .env marker", "# >>> FILE: .env" in vault_text)
        c.check("master.env contains secret content", "LOBBY_KEY=secret_lobby_val" in vault_text)
        c.check("master.env contains end marker", "# <<< END FILE: .env" in vault_text)

        # ── Test 3: Parse and Validation ─────────────────────────────────────
        entries, errors = env_master.parse_master_bundle(vault_file)
        c.check("parse_master_bundle succeeds with 0 errors", len(errors) == 0, str(errors))
        c.check("parsed 4 entries", len(entries) == 4)

        # ── Test 4: Path Traversal Rejection ─────────────────────────────────
        bad_vault = temp_dir / "bad_master.env"
        bad_vault.write_text(
            "# >>> FILE: ../../../etc/passwd\nroot:x:0:0\n# <<< END FILE: ../../../etc/passwd\n",
            encoding="utf-8",
        )
        _, bad_errs = env_master.parse_master_bundle(bad_vault)
        c.check("rejects relative path traversal (..)", any("traversal" in e.lower() for e in bad_errs))

        abs_vault = temp_dir / "abs_master.env"
        abs_vault.write_text(
            "# >>> FILE: /etc/shadow\nroot:*\n# <<< END FILE: /etc/shadow\n",
            encoding="utf-8",
        )
        _, abs_errs = env_master.parse_master_bundle(abs_vault)
        c.check("rejects absolute paths", any("absolute" in e.lower() for e in abs_errs))

        # ── Test 5: Restore & Backup ─────────────────────────────────────────
        restore_dir = Path(tempfile.mkdtemp(prefix="test_env_restore_"))
        try:
            # First restore to empty destination
            rc = env_master.restore_master(restore_dir, vault_file)
            c.check("first restore returns 0", rc == 0)
            c.check("restored root .env", (restore_dir / ".env").is_file())
            c.check("restored content matches", (restore_dir / ".env").read_text(encoding="utf-8").strip() == "LOBBY_KEY=secret_lobby_val")

            # Second restore (idempotent — unchanged)
            rc = env_master.restore_master(restore_dir, vault_file)
            c.check("second restore returns 0 (idempotent)", rc == 0)

            # Modify local file and restore again -> should create .pre-restore.bak
            (restore_dir / ".env").write_text("LOBBY_KEY=modified_locally\n", encoding="utf-8")
            rc = env_master.restore_master(restore_dir, vault_file)
            c.check("restore after modification returns 0", rc == 0)
            c.check("created .pre-restore.bak", (restore_dir / ".env.pre-restore.bak").is_file())
            c.check("backup contains modified value", (restore_dir / ".env.pre-restore.bak").read_text(encoding="utf-8").strip() == "LOBBY_KEY=modified_locally")
            c.check("restored file overwritten with vault value", (restore_dir / ".env").read_text(encoding="utf-8").strip() == "LOBBY_KEY=secret_lobby_val")
        finally:
            shutil.rmtree(restore_dir, ignore_errors=True)

        # ── Test 6: Live repo master.env check ───────────────────────────────
        live_repo_root = env_master.get_repo_root()
        live_vault = live_repo_root / env_master.DEFAULT_VAULT_REL
        if live_vault.is_file():
            rc = env_master.verify_master(live_vault)
            c.check("live master.env passes verification", rc == 0)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
