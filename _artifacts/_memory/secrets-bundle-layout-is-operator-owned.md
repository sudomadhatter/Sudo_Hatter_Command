---
name: secrets-bundle-layout-is-operator-owned
description: "The operator organizes the hand-carried secrets bundle their own way — do not consolidate, relocate, or recreate _secrets/; pass explicit paths to scripts instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: eafbef40-5e30-4001-b696-a23ece42c00d
  modified: 2026-08-07T00:13:33.439Z
---

On the Mac (2026-08-06) the operator keeps the hand-carried secrets bundle under
`docs/migrations/auth_keys/` and deleted the `_secrets/` copy the agent had recreated at the
kit's canonical path. When the agent moved to "consolidate duplicates," the operator stopped it:
**"leave the secrets alone they are organized the way I want."**

**Why:** the bundle layout is the operator's personal filing, not agent-owned infrastructure. Gitignore
rules (`**/auth_keys/`, `**/_secrets/`) cover both locations, so there is no leak risk either way.

**How to apply:** never reorganize, dedupe, or delete anything under the operator's secrets folders,
and don't recreate `_secrets/` at some other "canonical" path. The fix runs the other way — SCC-89
(2026-08-11) repointed the scripts AT the operator's copy, so their default is now
`docs/migrations/auth_keys/_secrets/master.env`, the place he actually keeps it. If a script ever
expects a bundle that isn't there, move the SCRIPT's path (`-MasterPath` on the `.ps1`,
`--master-path` on `restore-env-master.sh`), never the operator's files.
Related: [[env-migration-kit]].
