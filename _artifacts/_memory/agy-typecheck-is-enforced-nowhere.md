---
name: agy-typecheck-is-enforced-nowhere
description: "FRONTEND typecheck is still enforced nowhere (next.config ignoreBuildErrors, no CI tsc job). The BACKEND half was FIXED 2026-07-30: pyrefly is now pinned and a CI hard gate on changed files"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7c61bd5b-6cad-4c69-b6de-8ce2dea9c7a9
  modified: 2026-08-01T03:23:31.992Z
---

**2026-07-26 (story 21.3 ③).** AviationChat's machine floor has a type-shaped hole on **both** stacks,
and nothing in the pipeline reports it.

- **Frontend.** `frontend/next.config.ts` sets `typescript: { ignoreBuildErrors: true }` (and
  `eslint: { ignoreDuringBuilds: true }`). CI's only frontend build step is `npm run build` → `next build`,
  so it **cannot fail on type errors**. There is no `typecheck` script in `package.json` and no CI job runs
  `tsc`. ESLint *is* still gated — by a separate changed-files job in `pr-check.yml`, not by the build.
- **Backend.** `.agents/rules/code-standards.md` §6 names `backend/.venv/Scripts/pyrefly.exe check` as the
  backend type check. pyrefly is **not in the venv, not on PATH, and absent from `backend/requirements.txt`**
  (`No module named pyrefly`). `pr-check.yml` never invokes it either.

Caught when story 21.3's brand-new frontend contract file shipped **5 TypeScript errors** through ① and ②
and reached ③ unnoticed — `vi.fn(defaultAdminFetch)` inferred a 1-tuple call signature, so every
`call[1].method` / `call[1].body` assertion was untyped.

**Why it matters:** `npx tsc --noEmit` on `main_debug` was **completely silent** — the frontend is 100%
type-clean today. So the cost of turning the gate on is currently **zero**, and only grows. A green CI run
on a typecheck that never ran is the exact shape [[e2e-gate-fiction-test-guardrails]] and the
`tests-must-gate-for-real` rule exist to catch; this one is just quieter, because no job is even pretending.

**How to apply:**
- Run `npx tsc --noEmit` (frontend) by hand in any review that touches `.ts`/`.tsx` — CI will not do it
  for you, and a clean baseline means any output is yours.
- A **test** file's type errors count. They are the most likely place to introduce them (mock signatures
  are inferred from a helper, not from the thing being mocked) and the least likely place anyone looks.
- Prefer typing a `vi.fn` explicitly against the real dependency's shape —
  `vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(impl)` — over letting it infer from the
  default implementation.
- Before citing pyrefly output in any audit, check it is installed. A missing tool is a **finding**, not a
  skip — the floor is unrunnable, not passing.

## ✅ The BACKEND half is FIXED — 2026-07-30 (story 21.7 ③)

The backend bullet above is now HISTORY. What it did not know is that pyrefly had a **third** breakage on
top of "not installed, not pinned, not in CI": `pyrefly.toml` was committed but **completely inert** —
every key sat inside an unrecognised `[default]` section (pyrefly warned `Extra keys found in config:
default` and ignored the whole file), and its paths were **hardcoded absolutes to one machine**
(`c:\Users\dlohn\...`), violating `code-standards` §5. That is the real reason it was never wired to CI:
it could not have run on a Linux runner or the laptop lane even if someone had installed it.

All of it fixed and pushed on `claude/story-21-7-demo-profile-seed`:
- `pyrefly==1.1.1` pinned in `backend/requirements.txt` beside `ruff==0.16.0`, under an `AIDEV-NOTE`.
- `pyrefly.toml` flattened to top level with **relative** paths; no interpreter pin, so pyrefly resolves
  it from the invoking environment — which is what keeps CI and `backend/.venv` on the same one.
- Two `pr-check.yml` steps mirroring the ruff ratchet exactly: **`Types (pyrefly) — changed files` is a
  HARD gate** (no `continue-on-error`, same base-sha guard), and `— full repo` is **report-only** with
  OWNER + tracked EXPIRY + its **measured 470-error baseline**.
- **Measured full-repo debt: 470 errors** — missing-attribute 181, unsupported-operation 65,
  bad-argument-type 64, not-callable 50, missing-argument 28. Overwhelmingly untyped Firestore snapshot
  handling (`doc.to_dict()` returning `Awaitable` etc.). That number is why the full-repo step must stay
  soft; the changed-files gate is what protects new lines.

### ✅ …and it has LANDED — verified 2026-07-31 (story 21.8 ③, then on `main_debug`; on `main` since the 2026-08-07 branch migration)

The paragraph above describes a fix that was, at the time, only **on a branch** — which is why the earlier
guidance was "gate pyrefly on regression-vs-baseline until 21.7 lands". **21.7 has landed.** Re-verified
directly against the trunk at 21.8's close-out, not inferred:

- `git show origin/main_debug:backend/requirements.txt` → `ruff==0.16.0` **and** `pyrefly==1.1.1` pinned.
- `git show origin/main_debug:.github/workflows/pr-check.yml` → **`Types (pyrefly) — changed files, HARD
  GATE`** present, plus the report-only full-repo step carrying OWNER + EXPIRY.

So on any story branched from the current base (the live epic branch if one exists, else `main`),
**pyrefly on changed files is a real hard gate and a non-zero count on YOUR files is a blocker, not a
baseline artefact.** Story 21.8 ran it clean (0 errors, 4 documented sync-stub suppressions). Note the
changed-files gate lints **whole changed files**, so inherited debt in a file you touched becomes yours —
the same ratchet as [[agy-ruff-changed-files-is-a-hard-gate]]. Both hard gates fire on **pull requests
only**, never on the direct push that lands a story on its epic branch, so a local run remains the only
pre-landing signal.

**The frontend half is still open** — `ignoreBuildErrors`, no `typecheck` script, no CI `tsc` job. Run
`npx tsc --noEmit` by hand on any `.ts`/`.tsx` change; the baseline was clean, so any output is yours.
(Bookkeeping note from 21.8 ③: `sudo-tests.yaml`'s 21.7 audit entry claims **four** report-only CI steps;
`pr-check.yml` has **three** — there is no full-repo `tsc` step, because there is no `tsc` job at all.
Drift in the note, not a hole in the pipeline — and one more tell that the frontend half never shipped.)

**How to apply now:** pyrefly output is real and citable — but it only *gates* changed files. When a
review needs the whole picture, run `pyrefly check backend/` and compare against the 470 baseline rather
than reading a non-zero count as a regression.

Related: [[agy-ruff-changed-files-is-a-hard-gate]] (the half of §6 that IS enforced, and hard),
[[e2e-gate-fiction-test-guardrails]], [[coverage-source-silently-ignores-file-paths]],
[[governance-gate-scans-venv]], [[agy-frontend-vitest-harness]].
