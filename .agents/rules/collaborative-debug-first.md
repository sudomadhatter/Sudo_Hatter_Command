---
name: collaborative-debug-first
description: "Activates when you cannot directly observe runtime behavior (browser console, network, Firestore, UI) but Daniel can. Instrument with one targeted debug log and ask him to report back instead of guessing."
---

# Rule: Collaborative Debug-First (Ask the Pilot)

## When This Applies
Any time you cannot directly observe runtime behavior — browser console, network requests, Firestore state, or UI rendering — and the user CAN.

## The Rule
**STOP GUESSING. Add a debug log, ask the user to check, then fix with certainty.**

You do not have reliable browser access. The user is sitting in front of the running app. They are your eyes. Use them.

## The Protocol

### Step 1: Instrument, Don't Speculate
When you suspect a runtime issue (race condition, missing data, failed fetch, wrong state), **add a temporary debug log** at the exact point of uncertainty:

```tsx
// Frontend
console.log("[DEBUG] flashcard hydration:", { userUid, sessionId, timestamp: Date.now() });

// or tagged for easy filtering
console.warn("[DEBUG:FLASHCARDS]", data);
```

```python
# Backend
logger.info(f"[DEBUG] flashcard-decks endpoint hit, uid={token_uid}, cache_count={len(docs)}")
```

### Step 2: Ask the User to Report Back
Give them a **specific, actionable instruction**:

> "Hard refresh, open DevTools Console, filter for `[DEBUG]`, and tell me what you see."

or

> "Open the Cards tab and paste me the console output."

Do NOT say "check the logs" — tell them exactly WHERE and WHAT to look for.

### Step 3: Fix with Evidence, Not Theories
Now you have the actual data. Fix the real problem, not the one you imagined.

### Step 4: Remove Debug Logs
After the fix is confirmed, **remove or downgrade** temporary debug logs. Production code should not have `[DEBUG]` prefixed logs.

## Why This Matters
- **Guessing wastes rounds.** Each guess → edit → refresh → "still broken" cycle burns 3-5 minutes.
- **One debug log saves 3 guesses.** A single `console.log` at the right place tells you the exact state of the world.
- **The user is a sensor, not a spectator.** They have the running browser, the real Firestore, the actual auth state. You have none of those. Leverage the partnership.

## Anti-Patterns

❌ **Guessing in circles:**
> "The issue is probably X..." → edit → "Try now" → still broken → "Actually maybe Y..." → edit → "Try now" → still broken

❌ **Asking the user to debug for you:**
> "Can you check the Network tab, filter for flashcard-decks, look at the response headers, check the status code, examine the payload..."

That's too much. Add the log yourself and ask for ONE piece of info.

❌ **Stacking multiple speculative fixes:**
> "I changed 3 things, try now."

If it works, you don't know which fix mattered. If it fails, you've muddied the water.

## The Golden Pattern
```
1. "I suspect X. Adding a debug log at [exact location]."
2. [Add console.log / logger.info]  
3. "Please hard refresh and paste me the console line starting with [DEBUG:TAG]."
4. User pastes output.
5. "Got it — the issue is [Y]. Fixing now."
6. [Fix the actual problem]
7. [Remove debug log]
```

One round. Done.
