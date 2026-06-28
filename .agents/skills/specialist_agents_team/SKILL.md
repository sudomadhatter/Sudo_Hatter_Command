---
description: AviationChat's 3-lane Expert Witness pattern for multi-agent coordination
---

# Multi-Agent Orchestration Patterns

**Skill Type:** Architecture Pattern  
**Domain:** AviationChat-AGY  
**Use When:** Implementing or debugging multi-agent workflows in the Specialist/Verifier system

---

## Core Philosophy

AviationChat uses a **"System 2" Expert Witness Topology** that prioritizes **regulatory accuracy over speed**. Instead of a single agent that tries to be both fast and accurate, we split the cognitive load across three parallel lanes:

- **Lane 1:** Fast Talker (streams immediately)
- **Lane 2:** Investigation Swarm (queries databases in parallel)
- **Lane 3:** Verifier (fact-checks Lane 1 against Lane 2 evidence)

This pattern ensures users get **immediate engagement** while the system **verifies accuracy in the background**.

---

## The 3-Lane Pattern

### Lane 1: The Fast Talker (Capt. Lindbergh)

**Role:** Chief Ground Instructor  
**Model:** Gemini 3.1 Flash Lite  
**Latency Goal:** < 500ms to first token  

**Behavior:**
- Starts streaming **immediately** based on internal parametric memory
- Does NOT wait for RAG results
- Uses cached answers for common questions
- Conversational, natural, engaging

**Implementation:**
```python
# backend/services/specialist_orchestrator.py
async def handle_user_message(message: str, session_id: str):
    # Lane 1: Start streaming immediately
    talker_stream = talker_agent.stream_response(message)
    
    # DON'T await RAG results before streaming
    # Start sending tokens to frontend immediately
    async for chunk in talker_stream:
        yield {"type": "delta", "content": chunk}
```

**Critical Rules:**
- ✅ Stream within 500ms (user perception of "instant")
- ✅ Use Gemini 3.1 Flash Lite (speed over reasoning)
- ✅ Cache frequent answers in session memory
- ❌ Never wait for database queries
- ❌ Never block on verification results

---

### Lane 2: The Investigation Swarm (Experts A, B, C)

**Role:** Parallel RAG researchers  
**Model:** Gemini 3.1 Flash Lite (for graph query construction)  
**Trigger:** Exactly when user submits query (parallel with Lane 1)

**The Three Experts:**

#### Expert A: The Regulatory Hunter
- **Target:** FAR/AIM citations in DB2
- **Filter:** `type: "regulation"`
- **Goal:** Find the specific law/CFR text
- **Example Query:** "14 CFR 91.205 VFR day equipment"

#### Expert B: The Curriculum Specialist
- **Target:** ACS tasks in DB1, then supporting docs in DB2
- **Strategy:** Use Bridge Keys from DB1 to query DB2
- **Goal:** Find pedagogical context + official handbook backing

#### Expert C: The Library Search
- **Target:** Wide search of DB2 (no filters)
- **Strategy:** Hybrid keyword/semantic search
- **Goal:** Catch safety risks or edge cases the curriculum might miss

**Implementation:**
```python
async def dispatch_investigation_swarm(user_query: str):
    # Launch all experts in parallel
    tasks = [
        expert_a.search_regulations(user_query),
        expert_b.search_curriculum(user_query),
        expert_c.search_library_wide(user_query)
    ]
    
    # Wait for all to complete (or timeout after 3 seconds)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "regulatory": results[0],
        "curriculum": results[1],
        "wide_search": results[2]
    }
```

**Critical Rules:**
- ✅ Launch all three experts **simultaneously**
- ✅ Set 3-second timeout (don't block UI forever)
- ✅ Return partial results if one expert fails
- ❌ Never run experts sequentially (defeats parallelism)
- ❌ Never let Expert C use the same filters as A/B (redundancy)

---

### Lane 3: The Verifier (The Judge)

**Role:** Fact-checker and editor  
**Model:** Gemini 3.0 Pro (reasoning model)  
**Inputs:** Live stream from Lane 1 + Evidence from Lane 2

**The Verification Process:**

1. **Fact Check:** Does Lane 1 contradict regulatory evidence from Expert A?
2. **Safety Check:** Did Lane 1 miss a critical safety warning found by Expert C?
3. **Completeness Check:** Did Lane 1 skip important context from Expert B?

**Possible Actions:**

| Outcome | Action | UI Effect |
|---------|--------|-----------|
| **Correct** | Append `[Verified ✓]` badge | Green checkmark appears |
| **Incomplete** | Send `elaborate` event | Adds missing context below |
| **Wrong** | Send `swap` event | Crosses out incorrect text, shows correction |

**Implementation:**
```python
async def verify_response(talker_text: str, evidence: dict):
    verifier_prompt = f"""
    TALKER OUTPUT:
    {talker_text}
    
    EVIDENCE FROM EXPERTS:
    - Regulations: {evidence['regulatory']}
    - Curriculum: {evidence['curriculum']}
    - Wide Search: {evidence['wide_search']}
    
    TASK: Compare the Talker output against the evidence.
    - If CORRECT: Return {{"action": "confirm"}}
    - If MISSING SAFETY INFO: Return {{"action": "elaborate", "addition": "..."}}
    - IF CONTRADICTS REGULATION: Return {{"action": "swap", "correction": "..."}}
    """
    
    result = await verifier_agent.generate(verifier_prompt)
    
    if result['action'] == 'swap':
        # Send SSE event to frontend to replace text
        yield {
            "type": "swap",
            "original": result['incorrect_section'],
            "replacement": result['correction']
        }
```

**Critical Rules:**
- ✅ Use Gemini 3.0 Pro (needs reasoning, not speed)
- ✅ Only swap if there's **clear contradiction**
- ✅ Always cite the source in corrections (e.g., "Per 14 CFR 91.205...")
- ❌ Never swap for stylistic differences
- ❌ Never block Lane 1 streaming waiting for verification

---

## Orchestration Flow (Complete Example)

```python
# backend/services/specialist_orchestrator.py
async def orchestrate_specialist_response(message: str, session_id: str):
    """
    Implements the 3-lane Expert Witness pattern.
    """
    
    # Lane 1: Start Talker immediately
    talker_stream = talker_agent.stream_response(message)
    talker_text = ""  # Accumulate for verifier
    
    # Lane 2: Dispatch swarm in parallel
    investigation_task = asyncio.create_task(
        dispatch_investigation_swarm(message)
    )
    
    # Stream Lane 1 to user immediately
    async for chunk in talker_stream:
        talker_text += chunk
        yield {"type": "delta", "content": chunk}
    
    # Wait for Lane 2 results (should finish around now)
    evidence = await investigation_task
    
    # Lane 3: Verify and correct if needed
    async for correction in verify_response(talker_text, evidence):
        yield correction  # Could be swap/elaborate/confirm
```

---

## Timing Expectations

| Lane | Start | Complete | User Perception |
|------|-------|----------|-----------------|
| Lane 1 | 0ms | 2-4s | "Instant response" |
| Lane 2 | 0ms | 2-3s | "Background loading" |
| Lane 3 | 3s | 5s | "Verification badge appears" |

**Golden Rule:** User should see text streaming within 500ms, even if verification takes 5 seconds.

---

## Common Pitfalls

### ❌ Blocking Lane 1 on RAG results
```python
# BAD: Waits for database before streaming
evidence = await search_database(query)
response = await talker_agent.generate(evidence)
return response  # User waits 3+ seconds
```

### ✅ Correct: Parallel execution
```python
# GOOD: Stream immediately, verify in background
async for chunk in talker_agent.stream():
    yield chunk  # User sees < 500ms
    
# Verification happens after
```

### ❌ Running experts sequentially
```python
# BAD: 9 seconds total (3s each)
reg = await expert_a.search()
curr = await expert_b.search()
wide = await expert_c.search()
```

### ✅ Correct: Parallel dispatch
```python
# GOOD: 3 seconds total (all in parallel)
results = await asyncio.gather(
    expert_a.search(),
    expert_b.search(),
    expert_c.search()
)
```

### ❌ Verifier blocking the stream
```python
# BAD: User waits for verification before seeing ANY text
verified = await verify(talker_output, evidence)
return verified  # Long delay
```

### ✅ Correct: Verify after streaming
```python
# GOOD: Show text immediately, verify asynchronously
yield talker_output  # User sees now
yield await verify(...)  # Badge appears later
```

---

## Error Handling

### Lane 1 Failure (Talker crashes)
```python
try:
    async for chunk in talker_stream:
        yield chunk
except Exception as e:
    yield {"type": "error", "message": "The instructor had a brain freeze. Try again?"}
```

### Lane 2 Failure (Database timeout)
```python
try:
    evidence = await asyncio.wait_for(investigation_task, timeout=3.0)
except asyncio.TimeoutError:
    # Proceed without verification
    yield {"type": "badge", "status": "unverified"}
```

### Lane 3 Failure (Verifier error)
```python
try:
    corrections = await verify_response(...)
except Exception as e:
    # Log error, but don't break user experience
    logger.error(f"Verifier failed: {e}")
    yield {"type": "badge", "status": "unverified"}
```

**Philosophy:** Graceful degradation. If verification fails, **still show the response**, just mark it unverified.

---

## Agent Communication Protocol

### How Agents Share Context

1. **Talker → Swarm:** Query string only (no conversation history)
2. **Swarm → Verifier:** Evidence chunks + metadata (source, confidence)
3. **Verifier → Frontend:** Structured events (swap/elaborate/confirm)

### Session Isolation

- Each lane operates in its own session context
- Talker has conversation history (last 5 messages)
- Experts have NO conversation history (stateless)
- Verifier sees ONLY current exchange (no memory)

---

## Testing the 3-Lane Pattern

### Test Case 1: Happy Path (All lanes succeed)
```python
# Input: "What VFR equipment is required during the day?"
# Expected:
# - Lane 1 streams answer within 500ms
# - Lane 2 finds 14 CFR 91.205 in Expert A
# - Lane 3 confirms accuracy, shows [Verified ✓]
```

### Test Case 2: Talker makes mistake
```python
# Input: "When do I need strobes during the day?"
# Talker says: "Strobes are required for day VFR."
# Expert A finds: 14 CFR 91.205(b) - Strobes NOT required during day
# Verifier: Sends swap event to correct
# Expected: Text crossed out, correction shown with citation
```

### Test Case 3: Database timeout
```python
# Simulate: Vertex AI query takes > 3 seconds
# Expected:
# - Lane 1 still streams normally
# - Lane 2 returns empty evidence
# - Lane 3 shows "unverified" badge
# - User still gets answer, just not verified
```

---

## Performance Optimization

### Caching Strategy
- Cache common Talker responses (e.g., "What is VFR?")
- Cache DB queries for 15 minutes (InMemorySessionService)
- Don't cache verification results (always verify fresh)

### Token Management
- Talker: Max 500 tokens output (keep responses concise)
- Verifier: Max 1000 tokens context (limit evidence size)
- Use streaming to show progress (user patience increases)

---

## When to Use This Pattern

✅ **Use 3-lane orchestration for:**
- Specialist chat (ground instruction)
- Quiz explanations (need citations)
- "Teach Me" deep dives (need verification)

❌ **Don't use for:**
- HR onboarding (no verification needed)
- Greeting agent (stateless, no RAG)
- Admin grading (deterministic logic, no streaming)

---

## Related Skills

- [dual-store-rag-patterns.md](../dual-store-rag-patterns/SKILL.md) - How to query DB1 vs DB2
- [sse-streaming-patterns.md](../sse-streaming-patterns/SKILL.md) - How to implement Swap events
- [regulatory-verification-protocol.md](../regulatory-verification-protocol/SKILL.md) - What to verify

---

## Summary

The 3-lane Expert Witness pattern is AviationChat's **core architectural innovation**:

1. **Lane 1 (Talker):** Streams immediately for user engagement
2. **Lane 2 (Swarm):** Queries databases in parallel for evidence
3. **Lane 3 (Verifier):** Fact-checks and corrects if needed

**Key Insight:** Speed and accuracy are **not mutually exclusive** if you parallelize the work and verify asynchronously.
