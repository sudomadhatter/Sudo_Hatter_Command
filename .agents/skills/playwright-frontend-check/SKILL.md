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
| `FATAL:base/apple/mach_port_rendezvous_mac.cc:155] Check failed: kr == KERN_SUCCESS. bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.<pid>: Permission denied (1100)`, then `browserType.launch: Target page, context or browser has been closed` | **The Bash sandbox blocks chromium's Mach-port bootstrap.** Nothing in the error says "sandbox". | Re-run the call with `dangerouslyDisableSandbox: true`, or have the operator turn the sandbox off. **Verify, do not assume:** a sandbox toggled off elsewhere may or may not have reached your session - probe it and read the result. |
| `Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'playwright'` | Playwright is a **project** dependency, not global. There is no `playwright` on `PATH` and no Python package. ESM resolves from the **script file's** location, so a script in the scratchpad cannot see a project's `node_modules`. | Resolve explicitly with `createRequire` - see below. Do not `cd` and hope. |

Probe both in one line before doing anything else:

```bash
cd <the frontend that owns playwright> && node --input-type=module -e \
  'import {chromium} from "playwright"; const b=await chromium.launch({headless:true}); console.log("PROBE OK"); await b.close();'
```

`PROBE OK` and you are clear. A Mach-port abort is trap 1. `ERR_MODULE_NOT_FOUND` is trap 2.

---

## Where Playwright lives

It belongs to a project, not to the machine. Find the owner before you script anything:

```bash
ls -d /Users/sudohatter/Sudo_Hatter_Command/Projects/*/frontend/node_modules/playwright 2>/dev/null
ls ~/Library/Caches/ms-playwright                 # the browsers, shared by every project
```

Known owner today: `Projects/AGY_AVIATIONCHAT/frontend` (`@playwright/test ^1.58.2`). A project with
no Playwright installs it with `npm i -D @playwright/test && npx playwright install chromium` **from
that project's frontend** - never globally, and never as a drive-by edit to someone's `package.json`
in the middle of a debugging session. Ask first; it is their lockfile.

**Then resolve it from anywhere.** This is what lets the instrument script live in the scratchpad
instead of littering the project tree:

```js
import { createRequire } from 'node:module';
const OWNER = '/Users/sudohatter/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/frontend/';  // trailing slash matters
const require = createRequire(OWNER);
const { chromium } = require('playwright');
```

`createRequire` takes a *path to resolve from*. Without the trailing slash Node treats the last
segment as a filename and resolves from its parent - which is usually still fine and occasionally
is not, so just always write it.

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

1. `await page.goto(url, { waitUntil: 'networkidle' })` - wait first, always
2. Screenshot + dump the DOM. **Look**, before deciding what to click.
3. Pick selectors from what you actually saw
4. Act, then re-capture

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
const { chromium } = createRequire(owner.replace(/\/?$/, '/'))('playwright');

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

const consoleLines = [], pageErrors = [], httpErrors = [], reqFailed = [];
page.on('console',       m => consoleLines.push({ type: m.type(), text: m.text() }));
page.on('pageerror',     e => pageErrors.push(e.message));            // ⭐ NOT the same as console
page.on('requestfailed', r => reqFailed.push({ url: r.url(), err: r.failure()?.errorText }));
page.on('response',      async r => {
  if (r.status() >= 400) httpErrors.push({ url: r.url(), status: r.status(),
                                           body: await r.text().catch(() => '<unreadable>') });
});

await page.goto(url, { waitUntil: 'networkidle' });
// ── act here: await page.getByRole('button', { name: 'Go' }).click(); ──
await page.waitForTimeout(300);                    // let async handlers land before capture

await page.screenshot({ path: shot, fullPage: true });
console.log(JSON.stringify({ consoleLines, pageErrors, httpErrors, reqFailed,
                             title: await page.title(),
                             text: (await page.locator('body').innerText()).slice(0, 2000) }, null, 2));
await browser.close();
```

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
const page = browser.contexts()[0].pages()[0];
```

Read from their live session. **Do not click things in a browser someone else is driving** without
saying so first - you are moving a window they are looking at.

---

## Using this inside `/cicd-live-testing-team`

That command is the main caller. The loop it changes:

- **Before:** "check the Console and tell me the exact error line" → the human retypes it → half the
  stack is gone.
- **Now:** capture it, attach the JSON and the PNG to the bug doc's `## Evidence`, and ask the human
  only for what a script genuinely cannot reach.

Keep the artifacts. A bug doc that says *"console showed an error"* is a description; one carrying
the captured `pageerror` string, the 500's response body and a full-page screenshot is evidence, and
it is what `Root cause` gets ranked against. Write them next to the doc under
`_artifacts/debugging/<date>_live-testing/`.

## Cleaning up

Close the browser (`await browser.close()`) on every path, including failures - an orphaned chromium
holds its user-data dir and the next launch inherits a confusing profile. Delete scratch scripts and
one-off PNGs you did not attach to anything. Never leave a `--remote-debugging-port` browser running
after the session.
