#!/usr/bin/env bash
# link-memory.sh — macOS/Linux twin of link-memory.ps1
#
# Make Claude Code's auto-memory store portable: SYMLINK it into the repo so it travels via git.
#
# Claude Code keeps auto-memory at  ~/.claude/projects/<slug>/memory/  where <slug> is DERIVED FROM THE
# ABSOLUTE PATH of the workspace (':' '\' '/' and '_' all become '-'). That makes the store fragile:
#
#   1. MACHINE - ~/.claude is not a repo and is not synced, so memory never leaves the box it was
#                written on.
#   2. RENAME  - renaming the home base or a project changes the slug, silently orphaning everything
#                under the old one.
#   3. CASE    - on a case-insensitive macOS volume two spellings can collide rather than fragment;
#                the reverse of the Windows problem, handled the same way (verify, never guess).
#
# The fix: the repo holds the canonical store at <root>/_artifacts/_memory/, and the slug directory
# becomes a SYMLINK pointing at it.
#
# TWINS BY CONTRACT with link-memory.ps1 — if either changes, change both. Same standing rule the
# Restore-EnvMaster.ps1 / restore-env-master.sh pair lives under (see _my_resources/migrations/INDEX.md).
#
# SAFETY. This script never deletes memory. If canonical already holds files AND the local slug dir
# holds its own, the local ones are moved ASIDE to memory.local-backup-<timestamp> and reported — never
# merged, never clobbered. A human resolves it; the script refuses to guess.
#
# USAGE
#   bash .agents/scripts/link-memory.sh                 # dry run, this workspace
#   bash .agents/scripts/link-memory.sh --all           # dry run, lobby + maintained projects
#   bash .agents/scripts/link-memory.sh --all --apply   # do it
#   bash .agents/scripts/link-memory.sh --force         # re-point a link aimed elsewhere

set -euo pipefail

APPLY=0; ALL=0; FORCE=0; ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --all)   ALL=1 ;;
    --force) FORCE=1 ;;
    --root)  shift; ROOT="$1" ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

# Repo root: this script lives at <root>/.agents/scripts/ (master + vendored alike).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "$ROOT" ]; then ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"; fi
ROOT="$(cd "$ROOT" && pwd)"

PROJECTS_STORE="$HOME/.claude/projects"

# --- the slug algorithm ---------------------------------------------------------------------------
# ':' '\' '/' and '_' each become '-'. Nothing else is touched; case is preserved as the path supplies
# it. On a POSIX path the leading '/' therefore produces a LEADING '-'.
#
# NOTE: this rule was derived from Windows slugs and reproduces every one of them exactly, but the
# POSIX shape has not been observed on a real Mac. That is why link_workspace VERIFIES the computed
# slug dir before trusting it — run `ls ~/.claude/projects/` once on the Mac and compare.
memory_slug() { printf '%s' "$1" | sed 's#[:\\/_]#-#g'; }

# Case handling: APFS/HFS+ are case-INSENSITIVE by default, so two spellings resolve to one directory
# (same as NTFS). Compute ONE slug, then reuse any existing dir that matches case-insensitively rather
# than creating a second. Linking "both spellings" would process the same dir twice and manufacture a
# false canonical-vs-local conflict on the second pass.
resolve_slug_dir() {
  local slug want hit
  slug="$(memory_slug "$1")"
  want="$PROJECTS_STORE/$slug"
  if [ -d "$want" ]; then printf '%s' "$want"; return; fi
  if [ -d "$PROJECTS_STORE" ]; then
    hit="$(find "$PROJECTS_STORE" -mindepth 1 -maxdepth 1 -type d -iname "$slug" | head -1)"
    if [ -n "$hit" ]; then printf '%s' "$hit"; return; fi
  fi
  printf '%s' "$want"
}

# Count MEMORIES only. README.md / .gitkeep are scaffolding committed so the empty store is visible in
# git; counting them would make a fresh canonical look "already populated" and send the first machine
# down the backup path instead of seeding — silently stranding the memories we are rescuing.
count_memory_files() {
  [ -d "$1" ] || { echo 0; return; }
  find "$1" -maxdepth 1 -type f ! -name 'README.md' ! -name '.gitkeep' | wc -l | tr -d ' '
}

act() { if [ "$APPLY" -eq 1 ]; then echo "  $1"; else echo "  WHATIF: would $1"; fi; }

link_workspace() {
  local ws_root="$1"
  echo
  echo "=== $ws_root"

  local canonical="$ws_root/_artifacts/_memory"
  local canon_count=0
  if [ -d "$canonical" ]; then
    canon_count="$(count_memory_files "$canonical")"
    echo "  canonical : $canonical  ($canon_count memory file(s))"
  else
    echo "  canonical : $canonical  (does not exist yet)"
    act "create canonical store '$canonical'"
    [ "$APPLY" -eq 1 ] && mkdir -p "$canonical"
  fi

  local slug slug_dir link computed
  slug_dir="$(resolve_slug_dir "$ws_root")"
  link="$slug_dir/memory"
  slug="$(basename "$slug_dir")"
  computed="$(memory_slug "$ws_root")"
  if [ "$slug" != "$computed" ]; then
    echo "  slug      : $slug  (reusing existing dir; computed '$computed')"
  else
    echo "  slug      : $slug"
  fi

  # Sanity: if the store has entries but none matches our computed slug, the rule is wrong on this
  # platform. Say so loudly instead of creating a second, wrong directory.
  if [ -d "$PROJECTS_STORE" ] && [ ! -d "$slug_dir" ]; then
    if find "$PROJECTS_STORE" -mindepth 1 -maxdepth 1 -type d | grep -q .; then
      echo "  NOTE: no existing slug dir matches the computed name. Existing entries:"
      find "$PROJECTS_STORE" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sed 's/^/          /'
      echo "  If none of those correspond to this workspace, the slug rule differs on this platform —"
      echo "  stop and report before using --apply."
    fi
  fi

  if [ -L "$link" ]; then
    local tgt; tgt="$(readlink "$link")"
    if [ "$tgt" = "$canonical" ]; then
      echo "    [ok] already symlinked to canonical - nothing to do"
      return 0
    fi
    if [ "$FORCE" -ne 1 ]; then
      echo "    WARNING: link exists but points at '$tgt' - re-run with --force to re-point" >&2
      return 0
    fi
    act "remove symlink pointing at '$tgt'"
    [ "$APPLY" -eq 1 ] && rm "$link"
  elif [ -d "$link" ]; then
    local local_count; local_count="$(count_memory_files "$link")"
    if [ "$local_count" -eq 0 ]; then
      act "remove empty local memory dir '$link'"
      [ "$APPLY" -eq 1 ] && rm -rf "$link"
    elif [ "$canon_count" -eq 0 ]; then
      act "SEED canonical with $local_count local file(s) from '$link'"
      if [ "$APPLY" -eq 1 ]; then
        find "$link" -maxdepth 1 -type f -exec mv {} "$canonical/" \;
        rm -rf "$link"
      fi
      canon_count="$local_count"
    else
      local backup="$slug_dir/memory.local-backup-$(date +%Y-%m-%d_%H%M%S)"
      echo "    WARNING: canonical has $canon_count file(s) AND local has $local_count - NOT merging" >&2
      act "move local memory aside to '$backup' (nothing deleted; reconcile by hand)"
      [ "$APPLY" -eq 1 ] && mv "$link" "$backup"
    fi
  fi

  if [ ! -d "$slug_dir" ]; then
    act "create slug dir '$slug_dir'"
    [ "$APPLY" -eq 1 ] && mkdir -p "$slug_dir"
  fi

  act "symlink '$link' -> '$canonical'"
  if [ "$APPLY" -eq 1 ]; then
    ln -s "$canonical" "$link"
    if [ -L "$link" ]; then echo "    [ok] symlink verified"; else echo "ln reported success but '$link' is not a symlink" >&2; exit 1; fi
  fi
}

# --- targets --------------------------------------------------------------------------------------
TARGETS=("$ROOT")
if [ "$ALL" -eq 1 ]; then
  LIST="$ROOT/.agents/maintained-projects.txt"
  [ -f "$LIST" ] || { echo "--all needs '$LIST' (the maintained-projects source of truth)" >&2; exit 1; }
  while IFS= read -r line; do
    line="$(printf '%s' "$line" | sed 's/#.*$//' | xargs || true)"
    [ -z "$line" ] && continue
    p="$ROOT/Projects/$line"
    if [ -d "$p" ]; then TARGETS+=("$(cd "$p" && pwd)")
    else echo "WARNING: maintained project '$line' not found at '$p' - skipped" >&2; fi
  done < "$LIST"
fi

echo
echo "=============================================================================="
if [ "$APPLY" -eq 1 ]; then echo "CLAUDE MEMORY LINK  (APPLY)"
else echo "CLAUDE MEMORY LINK  (DRY RUN - re-run with --apply to write)"; fi
echo "=============================================================================="
echo "store: $PROJECTS_STORE"

for t in "${TARGETS[@]}"; do link_workspace "$t"; done

echo
if [ "$APPLY" -eq 1 ]; then
  echo "Done. Commit the new _artifacts/_memory/ content in each repo it appeared in."
else
  echo "Nothing was written. Re-run with --apply once the plan above looks right."
fi
