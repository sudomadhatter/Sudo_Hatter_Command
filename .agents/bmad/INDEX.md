# bmad — INDEX

BMAD install (agents, workflows, install manifests). Regenerated on BMAD update — never hand-edit.

> ⛔ **NOT mirrored to projects.** `/smh-sync-agents` excludes `bmad/` from the vendor **entirely** — BMAD
> self-installs per repo and `project_name` is per-project identity, so master never overwrites it.
> (Corrected 2026-08-08, SCC-40: this line previously claimed the opposite, and that false claim is why
> two team overrides were hand-edited here — where nothing reads them — while the live copies stayed
> stale for weeks.)
>
> **Team BMAD overrides live in `_bmad/custom/<skill>.toml`, per repo.** That is the update-safe seam:
> a BMAD update replaces the skill directory and never touches `_bmad/custom/`. Each skill's own
> `customize.toml` (stamped *"DO NOT EDIT"*) declares the fields you may override. Edit them there —
> never here.

## Top-level contents
<!-- auto-listed by /smh-update-maps-indexes — refresh via /smh-update-maps-indexes; do not hand-edit entries -->
- `_config/`
- `bmm/`
- `config.toml`
- `config.user.toml`
- `core/`
- `custom/`
- `scripts/`
- `tea/`
