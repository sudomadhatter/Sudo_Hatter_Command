---
name: playwright-frontend-check
description: Read a running frontend with Playwright instead of asking a human to read it for you - capture console errors, uncaught exceptions, failing network rows with response bodies, screenshots, and the rendered DOM. Use when diagnosing any frontend symptom in a local app (blank screen, silent failure, a button that does nothing, a request that never fires), when a bug report needs evidence rather than description, or when you are about to type "check DevTools and tell me what it says". Node, not Python. Reads the browser; never writes product code.
---

# Playwright frontend check - see the browser yourself

Adapted for this machine from Anthropic's `webapp-testing` skill (`anthropics/skills`), which is
**Python**. What is installed here is **Node** (`@playwright/test` in the AGY frontend, browsers in
`~/Library/Caches/ms-playwright`). Following the upstream skill verbatim gets you a Python
`ImportError`. Everything below is Node and has been run on this machine.

**The boundary, first.** This skill *observes*. It captures what the browser knows and hands it to
whoever is writing the bug doc. It does not write product code, and it is **not** a second E2E door -
`/cicd-e2e` and the AGY journeys suite own that job, with emulators and a gate. If you find yourself
adding assertions and calling it a test, you are in the wrong skill.

---

## ⛔ Two traps. Both are invisible from inside the failure. Read these before you write a script.

| Symptom you will actually see | Cause | Fix |
|---|---|---|
| `FATAL:base/apple/mach_port_rendezvous_mac.cc:155] Check failed: kr == KERN_SUCCESS. bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.<pid>: Permission denied (1100)`, then `browserType.launch: Target page, context or browser has been closed` | **When the Bash sandbox is ON it blocks chromium's Mach-port bootstrap.** Nothing in the error says "sandbox", and the sandbox may already be off in your session - so this is the first thing to CHECK, not a certainty to act on. | Re-run the call with `dangerouslyDisableSandbox: true`, or have the operator turn the sandbox off. **Verify, do not assume:** a sandbox toggled off elsewhere may or may not have reached your session - probe it and read the result. |
| `Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'playwright'` | Playwright is a **project** dependency, not global. There is no `playwright` on `PATH` and no Python package. ESM resolves from the **script file's** location, so a script in the scratchpad cannot see a project's `node_modules`. | Resolve explicitly with `createRequire` - see below. Do not `cd` and hope. |
| `ERR_MODULE_NOT_FOUND` for `playwright` on a project that **does** have Playwright installed | The project declares `@playwright/test`; bare **`playwright` is a hoisted transitive** of it. npm's flat `node_modules` makes `require('playwright')` work by accident — under pnpm's strict layout or Yarn PnP it does not resolve at all. | Require **`@playwright/test`**, which is what projects actually declare and which exports `chromium` too. |

Probe both in one line before doing anything else:

```bash
cd <the frontend that owns playwright> && node --input-type=module -e \
  'import {chromium} from "@playwright/test"; const b=await chromium.launch({headless:true}); console.log("PROBE OK"); await b.close();'
```

`PROBE OK` and you are clear. A Mach-port abort is trap 1. `ERR_MODULE_NOT_FOUND` is trap 2.

ⓘ **Why `cd` works HERE but not for your script.** `node -e` resolves imports from the **current
directory**, so `cd`-ing into the owning frontend is enough for a one-liner. A `.mjs` **file**
resolves from the **file's own location**, so the same import in a scratchpad script fails however
you `cd`. That is the whole reason the instrument below uses `createRequire` instead: one rule that
works from anywhere, rather than two rules that look contradictory.

---

## Where Playwright lives

It belongs to a project, not to the machine. Find the owner before you script anything:

```bash
LOBBY=$(git rev-parse --show-toplevel)            # resolve it; never hardcode a home path
ls -d "$LOBBY"/Projects/*/frontend/node_modules/@playwright/test    # which projects own it
ls ~/Library/Caches/ms-playwright                 # the browsers, shared by every project
```

⚠ **Run that `ls` WITHOUT `2>/dev/null`.** Silencing it turns "the glob matched nothing" and "the
path is wrong on this machine" into the same empty output, and the second reads as *"no project has
Playwright"* — a confident wrong answer of exactly the kind this skill exists to prevent. This system
runs on two machines and the browser cache lives elsewhere on Windows
(`%USERPROFILE%\AppData\Local\ms-playwright`).

Known owner today: `Projects/AGY_AVIATIONCHAT/frontend` (`@playwright/test ^1.58.2`).

⛔ **The command centre does not own Playwright and must never install it.** The lobby has no
`package.json` and no `node_modules`, and it stays that way: what lives here is this markdown, and
the enforcement suite is stdlib-only so it passes on a machine with no browsers. The driver belongs
to the project under test. If you catch yourself running `npm i` from the lobby, stop - you are in
the wrong directory.

### The project has no Playwright — the install procedure

**1. Confirm it is actually missing** (not just resolved from the wrong place):

```bash
cd <PROJECT>/frontend
node -e "require.resolve('@playwright/test'); console.log('present')" 2>&1 | tail -1
ls ~/Library/Caches/ms-playwright                  # browsers are machine-wide, shared by every project
```

`present` plus a populated cache and you have trap 2, not a missing install. Fix the resolution, not
the dependency.

**2. STOP and ask before installing.** ⛔ This is not a drive-by. It edits that project's
`package.json` **and its lockfile** — a real, reviewable change to a repo that is not the one you are
standing in, in the middle of a debugging session that was supposed to write no product code. Say
what you want to add, to which project, and why.

**3. On their word, from the project's frontend — never globally, never with `-g`:**

```bash
cd <PROJECT>/frontend
npm i -D @playwright/test        # devDependency: it is a tool, never shipped to users
npx playwright install chromium  # the browser binary; skip if ms-playwright already has one
```

Chromium alone is enough for this skill. Do not `npx playwright install` bare — that pulls Firefox
and WebKit too, hundreds of megabytes nobody asked for.

**4. That change needs its OWN ticket, in that project's tracker.** Cross-repo work takes a ticket
per repo: a lobby ticket cannot account for a commit inside a project, and the dependency bump is a
commit inside that project. Hand the lockfile change to that project's normal lane rather than
committing it from a live-testing session.

**If they say no, you are not blocked.** Fall back to the human's own DevTools for this session and
say so in the bug doc, so a reader knows why the evidence is relayed rather than captured.

**Then resolve it from anywhere.** This is what lets the instrument script live in the scratchpad
instead of littering the project tree:

```js
import { createRequire } from 'node:module';
const OWNER = process.argv[2];      // the frontend that owns Playwright, passed in - never hardcoded
const require = createRequire(OWNER.replace(/\/?$/, '/'));   // trailing slash is REQUIRED, see below
const { chromium } = require('@playwright/test');
```

⛔ **Require `@playwright/test`, not bare `playwright`.** Projects declare `@playwright/test`; bare
`playwright` is a **transitive** dependency of it that only resolves because npm's flat
`node_modules` hoists it. `require('playwright')` therefore works on an npm project and throws
`ERR_MODULE_NOT_FOUND` on a pnpm or Yarn-PnP one that is correctly installed - a failure that looks
identical to trap 2 and sends you round in a circle applying a fix you already applied. Both packages
export `chromium`; only one is actually declared.

⛔ **The trailing slash is not a nicety - without it this fails every time.** `createRequire` takes
a path to resolve *from*, and treats the last segment as a **filename**, so it searches the PARENT
directory. Measured on this machine:

```
FAIL  ".../Projects/AGY_AVIATIONCHAT/frontend"   -> MODULE_NOT_FOUND
OK    ".../Projects/AGY_AVIATIONCHAT/frontend/"  -> .../frontend/node_modules/@playwright/test/...
```

`Projects/AGY_AVIATIONCHAT/node_modules` does not exist, so the parent search finds nothing. An
earlier draft of this file called the slash-less form *"usually still fine"*; that was wrong, and
wrong in the costly direction - an agent reads it, rules the missing slash out, and goes hunting the
sandbox instead. The `owner.replace(/\/?$/, '/')` in the instrument exists precisely so a path
pasted without the slash still works.

---

## Decision tree

```
A frontend symptom → is there a running app?
    ├─ No, it's a static .html file  → page.goto('file:///abs/path.html'), no server needed
    │
    └─ Yes → is the symptom reproducible without a login?
        ├─ Yes → SCRIPT IT. Reconnaissance-then-action (below). This is the default.
        │
        └─ No (auth-gated, MFA, a flow only the human can drive)
              → the human still flies. You are not stuck: attach to what they are
                already running with connectOverCDP, or ask for ONE specific artifact.
                Coaching a human through DevTools is the FALLBACK now, not the default.
```

## Reconnaissance-then-action

The pitfall the upstream skill names, and it is real: **inspecting the DOM before the app has
rendered.** A SPA serves an empty `<div id="root">` and your selector search finds nothing, so you
conclude the element is missing when it simply had not been drawn yet.

1. `await page.goto(url, { waitUntil: 'domcontentloaded' })`, then settle on something real
2. Screenshot + dump the DOM. **Look**, before deciding what to click.
3. Pick selectors from what you actually saw
4. Act, then re-capture

### ⛔ Do NOT default to `waitUntil: 'networkidle'` — measured, it hangs on the app you care about

`networkidle` waits for ~500 ms with no in-flight requests. **An app holding a connection open never
reaches that state**: server-sent events, a websocket, long-polling, a Firestore listen channel. A
chat frontend is exactly this shape.

Measured on this machine against a page serving one SSE stream:

```
networkidle:       FAILED after 8005 ms - page.goto: Timeout 8000ms exceeded
domcontentloaded:  OK in 14 ms | DOM: APP RENDERED FINE
```

The page is **healthy**. It renders in 14 ms. With the default 30 s timeout `networkidle` stalls the
whole session for half a minute and then throws — and the natural reading of *"navigating to … timeout"*
is *"the page didn't load"*, which is the exact opposite of the truth. That is a confident wrong
answer manufactured by the instrument.

**Settle on something that actually signals readiness**, in this order of preference:

```js
await page.goto(url, { waitUntil: 'domcontentloaded' });
await page.getByRole('heading').first().waitFor({ timeout: 10_000 });   // best: a real element
// or, when you do not yet know the page:
await page.waitForLoadState('networkidle', { timeout: 5_000 }).catch(() => {});  // bounded, optional
```

Wrapping `networkidle` in a bounded `.catch(() => {})` is the safe way to *want* it: a quiet page
settles fast, a streaming page costs you the timeout and carries on instead of dying.

Prefer `getByRole` / `getByText` over CSS descendant chains - they survive a restyle, and they read
like the thing the human described ("the Go button").

---

## The instrument

Write it to the scratchpad, run it, read the JSON. Adapt per symptom - this is a starting point, not
a fixture. Every channel below was verified on this machine.

```js
// ~/scratchpad/inspect.mjs — usage: node inspect.mjs <url> <owner-frontend> <out.png>
import { createRequire } from 'node:module';
const [url, owner, shot] = process.argv.slice(2);
const { chromium } = createRequire(owner.replace(/\/?$/, '/'))('@playwright/test');

const consoleLines = [], pageErrors = [], httpErrors = [], reqFailed = [];
const pending = [];                                 // in-flight body reads — see below
let navError = null;

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();

  page.on('console',       m => consoleLines.push({ type: m.type(), text: m.text() }));
  page.on('pageerror',     e => pageErrors.push(e.message));          // ⭐ NOT the same as console
  page.on('requestfailed', r => reqFailed.push({ url: r.url(), err: r.failure()?.errorText }));
  page.on('response',      r => {
    if (r.status() < 400) return;
    const row = { url: r.url(), status: r.status(), body: null };
    httpErrors.push(row);                           // ⭐ push NOW, fill the body when it arrives
    pending.push(r.text().then(t => { row.body = t.slice(0, 2000); },
                               () => { row.body = '<unreadable>'; }));
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded' });        // ⛔ NOT networkidle - see above
    await page.waitForLoadState('networkidle', { timeout: 5_000 }).catch(() => {});  // bounded
    // ── act here: await page.getByRole('button', { name: 'Go' }).click(); ──
    await page.waitForTimeout(300);                 // let async handlers land before capture
    await page.screenshot({ path: shot, fullPage: true });
  } catch (e) {
    navError = String(e.message || e);              // ⭐ keep what we captured; never exit silently
  }

  await Promise.allSettled(pending);                // ⭐ bodies before serialize
  console.log(JSON.stringify({
    navError, consoleLines, pageErrors, httpErrors, reqFailed,
    title: await page.title().catch(() => null),
    text: await page.locator('body').innerText().then(t => t.slice(0, 2000), () => null),
    // ⭐ real DOM, for picking selectors. innerText has no tags, roles or attributes, so you
    // cannot choose a locator from it - that is what this field is for.
    html: await page.content().then(h => h.slice(0, 6000), () => null),
    roles: await page.locator('button, a, input, [role]').evaluateAll(
      els => els.slice(0, 40).map(e => ({ tag: e.tagName.toLowerCase(),
                                          role: e.getAttribute('role'),
                                          name: (e.innerText || e.getAttribute('aria-label')
                                                 || e.getAttribute('placeholder') || '').slice(0, 60) }))
    ).catch(() => null),
  }, null, 2));
} finally {
  await browser.close();                            // ⭐ every path, including the failures
}
```

### Three things in that shape are load-bearing, not style

- **The `try`/`finally`.** The single most useful run of this instrument is the one where the page
  is broken — and `page.goto` **rejects** exactly then: `net::ERR_CONNECTION_REFUSED` when the dev
  server is down, or a `TimeoutError` when `networkidle` never arrives (any app holding a long-lived
  connection — websockets, SSE, polling, a Firestore listen channel — may never go idle). Top-level
  await + no handler means the process dies before it prints, so **everything already captured is
  thrown away** and chromium is left running with its user-data dir held. Catch, record `navError`,
  print anyway.
- **Pushing the response row synchronously.** `page.on` does **not** await its handler. Building the
  row *after* `await r.text()` means a 4xx/5xx whose body arrives late is simply absent from the
  JSON — the instrument reports "no failing requests" for a page that got a 500. Push the row
  immediately, fill `body` when the read resolves, and `await Promise.allSettled(pending)` before
  serializing.
- **Capping the body at 2000 chars**, the same cap the page text gets. A 500 from a framework often
  returns a full HTML error page; uncapped it floods the output you have to read and the bug doc it
  gets attached to. The useful part (`{"error":"boom"}`, a stack head) is short.

### ⭐ `pageerror` is not `console` - listen to both

An uncaught exception arrives on **`pageerror`** and does **not** appear as a console `error`.
Measured, same page, same run:

```
CONSOLE:    [{"type":"warning","text":"a warning"},
             {"type":"error","text":"Failed to load resource: … status of 500 …"},
             {"type":"error","text":"got boom"}]
PAGEERRORS: ["Cannot read properties of null (reading 'x')"]
```

The `TypeError` that actually broke the page is in the second list only. An agent listening on
`console` alone reports "no JS errors" about a page that threw. This is the single most common way
this instrument produces a confident wrong answer.

### The other three channels

- **`response` with `status() >= 400`** - and read `await r.text()`. The status alone tells you a
  request failed; the **body** usually tells you why (`{"error":"boom"}`, a stack, a validation list).
  That body is the thing a human relaying a Network tab almost never types out.
- **`requestfailed`** - a request that never got a response at all: CORS, DNS, connection refused,
  a dev server that is not running. Empty `httpErrors` **and** a populated `reqFailed` means you are
  chasing a backend that is down, not a frontend bug.
- **Screenshot** - `fullPage: true`. A blank screenshot with a clean console is its own finding: the
  app rendered nothing and threw nothing, which points at routing or a failed mount, not at code
  inside the component you were staring at.

### Attaching to a browser the human is already driving

When the state is expensive to reach (logged in, three steps into a flow), do not rebuild it -
attach. Have them start the browser with `--remote-debugging-port=9222`, then:

```js
const browser = await chromium.connectOverCDP('http://localhost:9222');
const pages = browser.contexts().flatMap(c => c.pages());
console.log('tabs:', pages.map(p => p.url()));               // ⛔ LOOK first, then choose
const page = pages.find(p => p.url().includes('localhost:5173'));   // pick by URL, never by index
if (!page) throw new Error('no tab matched - say which tabs you saw and ask');
```

⛔ **Never take `pages()[0]`.** That is the tab opened *earliest*, not the tab with the symptom — a
human three steps into a flow usually has a docs or Jira tab from before the app. Capturing it
yields a clean console, a clean `pageerror`, an empty `httpErrors` and a screenshot of the wrong
page, which in the JSON is **indistinguishable from "the app is fine"**. Print the tab list, match on
URL or title, and say in the bug doc which page you read.

Read from their live session. **Do not click things in a browser someone else is driving** without
saying so first - you are moving a window they are looking at.

⛔ **Never `close()` a browser you attached to.** The cleanup rule below is about browsers *you*
launched. Closing an attached one kills the human's session and the expensive state you connected
for. Use `browser.close()` on a `connectOverCDP` handle only when they have said they are done.

---

## Using this inside `/cicd-live-testing-team`

That command is the main caller. The loop it changes:

- **Before:** "check the Console and tell me the exact error line" → the human retypes it → half the
  stack is gone.
- **Now:** capture it, attach the JSON and the PNG to the bug doc's `## Evidence`, and ask the human
  only for what a script genuinely cannot reach.

Keep the artifacts. A bug doc that says *"console showed an error"* is a description; one carrying
the captured `pageerror` string, the 500's response body and a full-page screenshot is evidence, and
it is what `Root cause` gets ranked against. Write them next to the doc, under the **project's** tree:
`PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/` - the same path the command's Step 3
names. ⛔ Not a bare relative `_artifacts/...`: a relative path resolves against your CWD, which
resets to the command centre's main checkout, and the capture PNGs land in the lobby repo where they
are neither gitignored nor anywhere near the bug doc.

## Cleaning up

Close the browser **you launched** (`await browser.close()` in a `finally`) on every path, including
failures. ⚠ The reason is **lost evidence, not a leaked process**: measured twice here, an uncaught
throw still left zero stray chromium processes - Playwright reaps a browser it launched when the node
process dies. What the `finally` actually buys you is the JSON getting printed at all. Delete scratch
scripts and one-off PNGs you did not attach to anything.

⛔ **The one exception is the browser you did not launch.** A `connectOverCDP` handle belongs to the
human; closing it ends their session. Leave it open, and at close-out *ask* them to shut down the
`--remote-debugging-port` browser rather than doing it for them.
