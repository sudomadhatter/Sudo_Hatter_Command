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
`_my_resources/migrations/auth_keys/` and deleted the `_secrets/` copy the agent had recreated at the
kit's canonical path. When the agent moved to "consolidate duplicates," the operator stopped it:
**"leave the secrets alone they are organized the way I want."**

**Why:** the bundle layout is the operator's personal filing, not agent-owned infrastructure. Gitignore
rules (`**/auth_keys/`, `**/_secrets/`) cover both locations, so there is no leak risk either way.

**How to apply:** never reorganize, dedupe, or delete anything under the operator's secrets folders,
and don't recreate `_secrets/` at the kit path. If a restore/export script expects
`_my_resources/migrations/_secrets/master.env` and it isn't there, point the script at the operator's
copy (`-MasterPath` on the `.ps1`; for `restore-env-master.sh` ask or copy WITH the operator's OK)
rather than moving files. Related: [[env-migration-kit]].
