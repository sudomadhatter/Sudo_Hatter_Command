---
description: Clean context transfer between AviationChat agents
---

# Agent Handoff Patterns

**Skill Type:** Integration Pattern  
**Domain:** AviationChat-AGY  
**Use When:** Implementing agent transitions, debugging context issues, or designing new agent workflows

---

## Core Principle: Minimal Context Transfer

**Philosophy:** Each agent should receive ONLY the context it needs—nothing more, nothing less.

**Why?**
- **Token efficiency:** Don't waste tokens passing irrelevant conversation history
- **Session isolation:** Prevent context bleed between agents
- **Clear boundaries:** Each agent has a defined responsibility
- **Memory management:** Avoid context window overflow

---

### Parent Agents (User-Facing)
1. **Chuck** (Greeting) - Stateless, pre-login
2. **Mrs. Coleman** (HR) - Onboarding, profile management
3. **Capt. Lindbergh** (Specialist) - Ground instruction

### Sub-Agents & Universal Tools
4. **Reasoner** (Sub-Agent) - Fact-checking (Lane 3)
5. **TA Agent** (Sub-Agent) - Data hub for HR
6. **Admin Agent** (Parent) - Grading
7. **Librarian** (Global Tool) - RAG queries
8. **Tutor** (Future Parent/Sub) - Deep dive teaching

---

## Handoff 1: Chuck → Mrs. Coleman

**Scenario:** User logs in after greeting conversation

### What to Pass
```json
{
  "trigger": "user_login",
  "user_id": "pbIQDyzNJbeTxregRP1NBiWYS7s1",
  "timestamp": "2026-01-28T14:30:00Z"
}
```

### What NOT to Pass
❌ Greeting conversation history  
❌ Marketing messaging Chuck used  
❌ Chuck's session ID

**Rationale:** Chuck is stateless. His job ends at login. Mrs. Coleman starts fresh with ONLY the user ID.

### Implementation

```python
# frontend/src/components/GreetingChat.tsx
async function handleLogin(userId: string) {
    // Close greeting chat
    setGreetingOpen(false);
    
    // Check if HR needed
    const profileStatus = await fetch(`/api/profile/get/${userId}`);
    const { needs_onboarding } = await profileStatus.json();
    
    if (needs_onboarding) {
        // Open HR chat with NO greeting context
        setHRChatOpen(true);
    }
}
```

**Key Point:** No API call passes greeting chat messages to HR endpoint.

---

## Handoff 2: Mrs. Coleman → Capt. Lindbergh

**Scenario:** Profile complete, user starts study session

### What to Pass
```json
{
  "user_id": "pbIQDyzNJbeTxregRP1NBiWYS7s1",
  "pilot_data": {
    "name": "Daniel Lohneiss",
    "call_sign": "D-ICE",
    "current_rating": "Student",
    "checkride_type": "Private",
    "checkride_date": "2026-03-01"
  },
  "pilot_metrics": {
    "weakness_tags": ["weather", "airspace"],
    "strength_tags": ["aerodynamics"]
  }
}
```

### What NOT to Pass
❌ HR conversation history (onboarding questions)  
❌ How user answered onboarding questions  
❌ Mrs. Coleman's session ID

**Rationale:** Specialist needs to know WHO the student is and WHAT they're working on, but doesn't need to know HOW they enrolled.

### Implementation

```python
# backend/app.py
@app.post("/api/chat/specialist")
async def specialist_chat(request: SpecialistRequest):
    # Step 1: Fetch profile (via TA Agent)
    profile = get_student_profile(request.user_id)
    
    # Step 2: Build ONLY relevant context
    student_context = f"""
    STUDENT PROFILE:
    Name: {profile['name']}
    Call Sign: {profile['call_sign']}
    Current Rating: {profile['current_rating']}
    Target: {profile['checkride_type']}
    Weak Topics: {profile.get('pilot_metrics', {}).get('weakness_tags', [])}
    
    USER MESSAGE: {request.message}
    """
    
    # Step 3: Specialist uses ONLY this context (no HR history)
    response = await specialist_agent.generate(student_context)
    return response
```

**Key Point:** Specialist gets profile snapshot, NOT conversation replay.

---

## Handoff 3: Lindbergh → Tutor (Deep Dive)

**Scenario:** User clicks "Teach Me" button

### What to Pass: The Dossier

```json
{
  "user_id": "pbIQDyzNJbeTxregRP1NBiWYS7s1",
  "topic": "VFR Weather Minimums",
  "dossier": {
    "legal_context": [
      "14 CFR 91.155: Basic VFR weather minimums...",
      "AIM 3-1-4: VFR cruising altitudes..."
    ],
    "pedagogical_context": [
      "PA.VI.A.K1: Weather information sources...",
      "PHAK Chapter 12: Aviation Weather Services"
    ],
    "wide_search": [
      "NTSB Safety Alert: VFR into IMC accidents..."
    ]
  },
  "student_question": "What are the VFR weather minimums in Class E below 10,000 feet?"
}
```

### What NOT to Pass
❌ Entire Specialist conversation  
❌ Streaming chunks from Talker  
❌ Investigation Swarm raw results

**Rationale:** Tutor needs AGGREGATED evidence (the Dossier), not the raw retrieval workflow.

### Implementation

```python
# backend/services/specialist_orchestrator.py
async def handle_teach_me_button(user_query: str, user_id: str):
    # Step 1: Run 3-lane orchestration
    talker_output = await lane_1_fast_talker(user_query)
    evidence = await lane_2_librarian_tool(user_query)
    verification = await lane_3_reasoner(talker_output, evidence)
    
    # Step 2: Aggregate evidence into Dossier
    dossier = {
        "legal_context": evidence["expert_a_regulations"],
        "pedagogical_context": evidence["expert_b_curriculum"],
        "wide_search": evidence["expert_c_library"]
    }
    
    # Step 3: Handoff to Tutor with ONLY Dossier
    deep_dive = await tutor_agent.generate({
        "topic": extract_topic(user_query),
        "dossier": dossier,
        "student_question": user_query
    })
    
    return deep_dive
```

**Key Point:** Dossier is a CLEAN aggregation, not a raw dump.

---

## Handoff 4: Specialist → Admin (Grading)

**Scenario:** User completes quiz, Admin grades response

### What to Pass
```json
{
  "user_id": "pbIQDyzNJbeTxregRP1NBiWYS7s1",
  "question_id": "acs-ppl-task-a-q1",
  "user_answer": "You must hold a valid pilot certificate and medical certificate.",
  "correct_answer": "A valid pilot certificate, medical certificate, and photo ID.",
  "grading_criteria": {
    "keywords": ["pilot certificate", "medical certificate", "photo ID"],
    "partial_credit": true
  }
}
```

### What NOT to Pass
❌ Entire quiz conversation  
❌ Hints Specialist gave  
❌ How many attempts user made

**Rationale:** Admin needs ONLY the question, answer, and grading criteria.

### Implementation

```python
# backend/app.py
@app.post("/api/quiz/grade")
async def grade_quiz_response(request: GradeRequest):
    # Step 1: Admin grades the response
    grade_result = await admin_agent.grade({
        "question_id": request.question_id,
        "user_answer": request.user_answer,
        "correct_answer": request.correct_answer,
        "grading_criteria": request.grading_criteria
    })
    
    # Step 2: TA Agent updates metrics
    update_pilot_metrics(
        user_id=request.user_id,
        last_quiz_score=grade_result["score"]
    )
    
    return grade_result
```

**Key Point:** Grading is deterministic, doesn't need conversation context.

---

## Session Boundaries

### When to Create New Session ID

✅ **Create new session when:**
- User switches agents (Greeting → HR → Specialist)
- User starts a new study session (logs in again)
- User clicks "Start Quiz" (quiz mode is separate from chat)

❌ **Don't create new session when:**
- User sends multiple messages to same agent
- User scrolls through history
- Agent internally calls tools

### Session ID Format

```python
def generate_session_id(agent_name: str, user_id: str) -> str:
    """
    Format: {agent}-{user_id_prefix}-{timestamp}
    """
    timestamp = int(datetime.now().timestamp())
    user_prefix = user_id[:8]
    return f"{agent_name}-{user_prefix}-{timestamp}"

# Examples:
# "hr-pbIQDyzN-1738104960"
# "specialist-pbIQDyzN-1738105120"
# "tutor-pbIQDyzN-1738105300"
```

---

## Memory Management

### ADK MemoryService Usage

**What to Store:**
```python
# Store conversation in agent-specific session
memory_service.add_message(
    session_id=f"specialist-{user_id}-{timestamp}",
    role="user",
    content="What are VFR weather minimums?"
)

memory_service.add_message(
    session_id=f"specialist-{user_id}-{timestamp}",
    role="assistant",
    content="VFR weather minimums vary by airspace class..."
)
```

**What NOT to Store:**
- Tool calls (internal operations)
- RAG retrieval results (transient data)
- Verification results (shown via SSE, not saved)

### History Limits

```python
def get_conversation_history(session_id: str, limit: int = 5) -> list:
    """
    Retrieve last N messages for context.
    
    Args:
        session_id: Agent-specific session
        limit: Max messages (default 5 to prevent token overflow)
    """
    messages = memory_service.get_messages(session_id, limit=limit)
    return messages
```

**Rationale:** 5 messages = ~2-3 exchanges, enough for context without token bloat.

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Passing Entire Conversation

```python
# BAD: Specialist receives ALL HR messages
hr_history = get_all_messages("hr-session-123")
specialist_context = f"""
HR CONVERSATION:
{hr_history}  # Could be 50+ messages!

USER MESSAGE: {current_message}
"""
```

**Why Bad:** Wastes tokens, creates context confusion, slows response.

### ✅ Correct Pattern: Pass Profile Only

```python
# GOOD: Specialist gets profile snapshot
profile = get_student_profile(user_id)
specialist_context = f"""
STUDENT: {profile['call_sign']} (Target: {profile['checkride_type']})
MESSAGE: {current_message}
"""
```

---

### ❌ Anti-Pattern 2: Shared Session IDs

```python
# BAD: Same session for multiple agents
session_id = "user-123-session"
hr_agent.generate(session_id=session_id)
specialist_agent.generate(session_id=session_id)  # Sees HR history!
```

**Why Bad:** Agents see each other's conversations, context bleed.

### ✅ Correct Pattern: Agent-Specific Sessions

```python
# GOOD: Each agent has own session
hr_session = f"hr-{user_id}-{timestamp}"
specialist_session = f"specialist-{user_id}-{timestamp}"

hr_agent.generate(session_id=hr_session)
specialist_agent.generate(session_id=specialist_session)
```

---

### ❌ Anti-Pattern 3: Passing Streaming Chunks

```python
# BAD: Tutor receives raw streaming data
async for chunk in talker_agent.stream():
    tutor_context.append(chunk)  # Messy, incomplete

tutor_agent.generate(tutor_context)
```

**Why Bad:** Streaming chunks are incomplete, out of order, hard to parse.

### ✅ Correct Pattern: Aggregate First, Then Pass

```python
# GOOD: Collect full response, then aggregate
full_response = ""
async for chunk in talker_agent.stream():
    full_response += chunk

# Aggregate into clean Dossier
dossier = build_dossier(full_response, evidence)
tutor_agent.generate(dossier)
```

---

## Testing Handoffs

### Test Case 1: Clean HR → Specialist Transition

```python
async def test_hr_to_specialist_handoff():
    # Step 1: Complete HR onboarding
    update_student_profile(
        user_id="test_user",
        name="Test Pilot",
        call_sign="TEST",
        current_rating="Student",
        checkride_type="Private",
        checkride_date="2026-03-01"
    )
    
    # Step 2: Start Specialist session
    specialist_context = build_specialist_context("test_user")
    
    # Step 3: Verify NO HR conversation in context
    assert "name" in specialist_context  # Profile yes
    assert "HR" not in specialist_context  # HR convo no
    assert "Test Pilot" in specialist_context  # Data yes
```

---

### Test Case 2: Dossier Aggregation

```python
async def test_dossier_aggregation():
    # Step 1: Run investigation swarm
    evidence = await dispatch_investigation_swarm("VFR weather minimums")
    
    # Step 2: Build Dossier
    dossier = build_dossier(evidence)
    
    # Step 3: Verify structure
    assert "legal_context" in dossier
    assert "pedagogical_context" in dossier
    assert "wide_search" in dossier
    
    # Step 4: Verify content is aggregated (not raw)
    assert len(dossier["legal_context"]) < 500  # Summarized
    assert "14 CFR" in str(dossier)  # Contains citations
```

---

## Frontend Considerations

### Component Isolation

```typescript
// Each agent has own component, own state
function HRChat({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId] = useState(() => `hr-${userId}-${Date.now()}`);
  
  // HR component manages its own session
}

function SpecialistChat({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId] = useState(() => `specialist-${userId}-${Date.now()}`);
  
  // Specialist component DOES NOT access HR messages
}
```

**Key Point:** React state is component-scoped, preventing accidental context sharing.

---

### Profile Context Sharing

```typescript
// ProfileContext is the ONLY shared state
import { useProfile } from "@/contexts/ProfileContext";

function SpecialistChat() {
  const { profile } = useProfile();
  
  // Specialist reads profile, NOT HR conversation
  const context = {
    call_sign: profile.call_sign,
    checkride_type: profile.checkride_type
  };
}
```

---

## Related Skills

- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - How agents coordinate in 3-lane pattern
- [firestore-schema-guide.md](../firestore-schema-guide/SKILL.md) - What data to pass (profile schemas)

---

## Summary

**Key Takeaways:**

1. **Minimal Context Transfer** - Pass only what's needed
2. **Chuck → Mrs. Coleman** - No context (fresh start)
3. **Mrs. Coleman → Lindbergh** - Profile snapshot only
4. **Lindbergh → Tutor** - Aggregated Dossier, not raw streaming
5. **Agent-Specific Sessions** - Prevent context bleed
6. **5-Message History Limit** - Prevent token overflow

**Golden Rule:** When in doubt, pass LESS context, not more.
