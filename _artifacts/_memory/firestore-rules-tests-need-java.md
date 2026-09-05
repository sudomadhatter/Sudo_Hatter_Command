---
name: firestore-rules-tests-need-java
description: "The tea-12 Firestore rules emulator suite runs GREEN (61/61) but needs Java on PATH; Java 17 is installed here (Temurin) — set JAVA_HOME per shell since the silent MSI didn't add it to PATH."
metadata:
  probe: 'java -version' 
  node_type: memory
  type: project
  originSessionId: dc0bca70-54bb-4ac4-9a98-2a93ffae6a1e
---

tea-12 built a **local-only** Firestore security-rules test suite at `Projects/AGY_AVIATIONCHAT/firebase/tests/` (`@firebase/rules-unit-testing` + Node's `node --test`, kept OUT of the PR gate per the B5 posture). It runs **GREEN — 61 tests / 61 pass / 0 fail** under the real Firestore emulator, with non-vacuity proven by the emulator's own `PERMISSION_DENIED @ L<n>` logs. (`/bmad-testarch-test-review`: PASS 93/100.)

Requirements are satisfied on this box now: **Java 17** (`winget install EclipseAdoptium.Temurin.17.JRE` → `C:\Program Files\Eclipse Adoptium\jre-17.0.19.10-hotspot`) + **firebase-tools** (local npm dep). The **silent MSI does NOT add Java to PATH**, so each shell must set it before running:

```powershell
cd Projects/AGY_AVIATIONCHAT/firebase/tests
npm install
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jre-17.0.19.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
npm test   # firebase emulators:exec --config ../../firebase.json --only firestore --project demo-agy "node --test firestore.rules.test.js"
```

There was **no pre-existing rules-test setup** — `deploy-rules.yml` only DEPLOYS rules in CI (via `firebase deploy`), never tests them (that deploy-but-never-test gap was GAP-1). No firebase MCP is wired into the Claude Code session (both ToolSearches empty); the local firebase CLI (npm) is what drives the emulator.

**macOS addendum (2026-08-06) — different JDK, different scope, and the suite has grown to 70.**
The Mac uses the Homebrew **`openjdk@17` formula**, NOT the Temurin cask — casks are `.pkg`
installers that need interactive sudo and cannot be driven headlessly. The formula is keg-only and
is deliberately **not** registered with `/usr/libexec/java_home`, so that helper reports *"Unable to
locate a Java Runtime"* right next to a working JDK; point at it explicitly:
`/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home`.

⛔ **Do NOT set it "per shell" here.** That advice is Windows-shaped and produces a
pass-by-hand/fail-in-automation split on macOS. JAVA_HOME belongs in **`~/.zshenv`** — `~/.zshrc` is
interactive-only, so agents, hooks and `zsh -c` never see it ([[interactive-startup-files-are-invisible-to-automation]]).
Also required, and separate from the frontend's install: `(cd firebase/tests && npm install)` — the
backend emulator tier and the TEA-16 E2E journeys both resolve `firebase-tools` out of that same
directory, so all three suites die together when it is missing. Verified on the Mac: **70 pass / 0
fail**. Both emulator orchestrators now discover Java themselves on darwin
([[windows-authored-code-hides-posix-bugs]]).

**Why:** without JAVA_HOME set, `npm test` fails with a cryptic emulator startup error even though everything is installed — the PATH step is non-obvious.
**How to apply:** to run or extend the rules suite, set JAVA_HOME first — Temurin path on Windows, the Homebrew openjdk@17 path via `~/.zshenv` on macOS; it's proven green on both. Related: [[tea-retrofit-active-initiative]].
