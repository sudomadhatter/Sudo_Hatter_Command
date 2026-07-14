# GitNexus Graph Index Synchronization Guide

This guide explains how GitNexus indexes (graphs) are synchronized and updated across different developer machines.

## Do the GitNexus graphs sync automatically?

**No, the compiled index databases do not sync automatically via Git, but their configuration rules do.**

Here is the breakdown:

### What does NOT sync (Machine-Local)
- The **`.gitnexus/` folder** (which houses the compiled `lbug` database, caches, and the generated runner `run.cjs`) is ignored by Git in both the lobby and the projects (`**/.gitnexus/` is in `.gitignore`).
- This means when you push/pull changes via Git, the compiled code intelligence graph does not travel between machines. This is intentional to keep the repository size clean and avoid committing binary database diffs on every change.

### What DOES sync (Repository-Tracked)
- The **`.gitnexusignore`** file: Defines the scoping rules for what folders and files to index (excluding artifacts, temporary folders, and dev tooling).
- The **`.gitnexusrc`** file: Configures run properties (e.g., enabling PDG/taint analysis, skipping writing stubs to `AGENTS.md`).

---

## How to update the graph on another machine

When you pull changes on another machine, your local GitNexus index will become stale (it won't match the new `HEAD` commit). 

To update it:

1. **Verify Freshness**:
   Run the map-check script. It will run nine checks, including **Check 9 (GitNexus index freshness)**:
   ```powershell
   python .agents/scripts/check_maps.py --all
   ```
   If the index is stale (or missing), Check 9 will output a warning hint.

2. **Re-Index**:
   Run the analysis command in any stale repository:
   - For the **Lobby**:
     ```powershell
     node .gitnexus/run.cjs analyze
     ```
   - For **AGY_AVIATIONCHAT**:
     ```powershell
     cd Projects/AGY_AVIATIONCHAT
     node .gitnexus/run.cjs analyze
     ```

## How `node .gitnexus/run.cjs` works on new clones
If `.gitnexus/` is entirely missing (e.g., on a fresh clone), `node .gitnexus/run.cjs` will not exist initially. In this case, you can boot the indexer using:
```powershell
npx gitnexus analyze
```
This will automatically generate the `.gitnexus/` folder and write a fresh `.gitnexus/run.cjs` so that subsequent runs can use the shorter `node .gitnexus/run.cjs analyze` format.
