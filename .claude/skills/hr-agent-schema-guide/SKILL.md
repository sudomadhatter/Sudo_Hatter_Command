---
description: AviationChat's Firestore collections, document schemas, and TA Agent access patterns
---

# Firestore Schema Guide

**Skill Type:** Data Architecture  
**Domain:** AviationChat-AGY  
**Use When:** Reading/writing user data, implementing agent tools, or debugging database operations

---

## Core Principles

### The TA Agent is the Data Hub

**Golden Rule:** ALL Firestore reads and writes go through the **TA Agent (Teaching Assistant)**.

- ✅ Agents call TA tools: `get_student_profile()`, `update_student_profile()`
- ❌ Agents NEVER import Firestore directly
- ❌ Frontend NEVER writes to Firestore  directly (only through backend API)

**Why?** Centralized data access ensures:
- Consistent timestamps (`last_active` auto-updated)
- Data validation (check required fields)
- Audit trail (all writes logged)
- Schema enforcement (prevents drift)

---

## Database Configuration

**Service:** Cloud Firestore  
**Database ID:** `aviationchat-database`  
**Location:** `us-central1`  
**Mode:** Native mode (not Datastore mode)

**Authentication:**
```python
from google.cloud import firestore
import os

# Initialize Firestore client
db = firestore.Client(
    project=os.getenv("GCP_PROJECT_ID"),
    database="aviationchat-database"
)
```

---

## Collection 1: `users`

### Purpose
Stores pilot profiles, metrics, and session state.

### Document ID
Firebase Auth UID (e.g., `pbIQDyzNJbeTxregRP1NBiWYS7s1`)

### Schema

```json
{
  "name": "Daniel Lohneiss",
  "call_sign": "D-ICE",
  "current_rating": "Student",
  "checkride_type": "Private",
  "checkride_date": "2026-03-01",
  "last_active": "2026-01-28T14:30:00Z",
  "created_at": "2026-01-15T10:00:00Z",
  
  "pilot_metrics": {
    "weakness_tags": ["weather", "airspace"],
    "strength_tags": ["aerodynamics", "maneuvers"],
    "completion_rate": 65,
    "total_study_hours": 12.5,
    "last_quiz_score": 85
  },
  
  "session_state": {
    "current_topic_context": "VFR Weather Minimums",
    "last_agent": "specialist",
    "is_active": true
  }
}
```

### Field Definitions

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | string | ✅ | Legal name for certificates |
| `call_sign` | string | ✅ | Preferred nickname (how agents address them) |
| `current_rating` | string | ✅ | Student, Private, Instrument, Commercial, ATP |
| `checkride_type` | string | ✅ | Target certification |
| `checkride_date` | string | ✅ | YYYY-MM-DD format |
| `last_active` | timestamp | ✅ | Auto-updated on every profile write |
| `created_at` | timestamp | ✅ | Set once on first profile creation |
| `pilot_metrics` | object | ❌ | Dynamic scorecard (Admin Agent updates) |
| `session_state` | object | ❌ | Volatile context (expires after session) |

### Staleness Detection

```python
from datetime import datetime, timedelta

def is_profile_stale(profile: dict) -> bool:
    """
    Profile is stale if last_active > 30 days old.
    """
    if not profile.get("last_active"):
        return True
    
    last_active = datetime.fromisoformat(profile["last_active"].replace("Z", "+00:00"))
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    return last_active < thirty_days_ago
```

### Validation Rules

```python
def validate_profile_complete(profile: dict) -> tuple[bool, str]:
    """
    Returns (is_complete, reason).
    """
    required_fields = ["name", "call_sign", "current_rating", "checkride_type", "checkride_date"]
    
    for field in required_fields:
        if not profile.get(field):
            return False, f"missing_{field}"
    
    return True, "complete"
```

---

## Collection 2: `question_bank`

### Purpose
Stores pre-generated, verified quiz questions to ensure fresh content.

### Document ID
Composite: `acs-<checkride>-<task>-q<number>` (e.g., `acs-ppl-task-a-q1`)

### Schema

```json
{
  "id": "acs-ppl-task-a-q1",
  "acs_code": "PA.I.A.K1",
  "question": "What are the recent flight experience requirements to act as PIC carrying passengers?",
  "answer": "Within the preceding 90 days, you must have made three takeoffs and landings in an aircraft of the same catigory, class, and type (if type rating required). If operations are at night, the landings must be to a full stop.",
  "regulatory_sources": ["14 CFR 61.57(a)", "14 CFR 61.57(b)"],
  "difficulty": 3,
  "created_at": "2026-01-20T10:00:00Z",
  "status": "unused",
  "checkride": "Private"
}
```

### Field Definitions

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | string | ✅ | Unique identifier |
| `acs_code` | string | ✅ | Maps to ACS task (e.g., PA.I.A.K1) |
| `question` | string | ✅ | The quiz question text |
| `answer` | string | ✅ | Correct answer with explanation |
| `regulatory_sources` | array | ✅ | FAR/AIM citations (Bridge Keys) |
| `difficulty` | number | ✅ | 1-5 scale |
| `created_at` | timestamp | ✅ | When question was generated |
| `status` | string | ✅ | `unused` or `used` |
| `checkride` | string | ✅ | Private, Instrument, Commercial, etc. |

### Query Patterns

```python
def get_unused_question(checkride: str, acs_code: str = None):
    """
    Fetch an unused question for a specific checkride.
    """
    query = db.collection("question_bank") \
        .where("checkride", "==", checkride) \
        .where("status", "==", "unused") \
        .limit(1)
    
    if acs_code:
        query = query.where("acs_code", "==", acs_code)
    
    docs = list(query.stream())
    if not docs:
        return None
    
    return docs[0].to_dict()
```

---

## Sub-Collection: `users/{uid}/completed_items`

### Purpose
Tracks which questions/lessons a user has completed to prevent repeats.

### Document ID
Item ID (e.g., `q-101`, `lesson-pa-i-a`)

### Schema

```json
{
  "item_id": "q-101",
  "item_type": "question",
  "outcome": "correct",
  "completed_at": "2026-01-28T14:00:00Z",
  "status": "used"
}
```

### Field Definitions

| Field | Type | Purpose |
|-------|------|---------|
| `item_id` | string | Question or lesson identifier |
| `item_type` | string | `question`, `lesson`, `quiz` |
| `outcome` | string | `correct`, `incorrect`, `skipped` |
| `completed_at` | timestamp | When user completed it |
| `status` | string | `used` (prevents re-selection) |

### Query Pattern

```python
def check_if_completed(user_id: str, item_id: str) -> bool:
    """
    Check if user already completed this item.
    """
    doc_ref = db.collection("users").document(user_id) \
        .collection("completed_items").document(item_id)
    
    doc = doc_ref.get()
    return doc.exists
```

---

## TA Agent Tools (Required Interface)

### Tool 1: `get_student_profile`

```python
from google.genai.tools import FunctionTool

def get_student_profile(user_id: str) -> dict:
    """
    Retrieves the pilot profile from Firestore.
    
    Args:
        user_id: Firebase Auth UID
    
    Returns:
        dict: Profile data or empty dict if not found
    """
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return {}
    
    return doc.to_dict()

# Register as ADK tool
get_student_profile_tool = FunctionTool(get_student_profile)
```

### Tool 2: `update_student_profile`

```python
from datetime import datetime

def update_student_profile(
    user_id: str,
    name: str = None,
    call_sign: str = None,
    current_rating: str = None,
    checkride_type: str = None,
    checkride_date: str = None
) -> str:
    """
    Updates pilot profile in Firestore (partial update).
    
    Args:
        user_id: Firebase Auth UID
        name: Optional - Full legal name
        call_sign: Optional - Preferred nickname
        current_rating: Optional - Student|Private|Instrument|Commercial|ATP
        checkride_type: Optional - Target certification
        checkride_date: Optional - YYYY-MM-DD format
    
    Returns:
        str: Success message or error
    """
    doc_ref = db.collection("users").document(user_id)
    
    # Build update dict (only include non-None fields)
    updates = {}
    if name:
        updates["name"] = name
    if call_sign:
        updates["call_sign"] = call_sign
    if current_rating:
        updates["current_rating"] = current_rating
    if checkride_type:
        updates["checkride_type"] = checkride_type
    if checkride_date:
        updates["checkride_date"] = checkride_date
    
    # Auto-inject timestamp
    updates["last_active"] = datetime.utcnow().isoformat() + "Z"
    
    # If new user, add created_at
    if not doc_ref.get().exists:
        updates["created_at"] = datetime.utcnow().isoformat() + "Z"
    
    try:
        doc_ref.set(updates, merge=True)  # Partial update
        return f"Profile updated successfully for {user_id}"
    except Exception as e:
        return f"Error updating profile: {str(e)}"

# Register as ADK tool
update_student_profile_tool = FunctionTool(update_student_profile)
```

### Tool 3: `get_student_metrics`

```python
def get_student_metrics(user_id: str) -> dict:
    """
    Retrieves pilot_metrics subcollection.
    
    Returns:
        dict: Metrics data (weakness_tags, strength_tags, etc.)
    """
    profile = get_student_profile(user_id)
    return profile.get("pilot_metrics", {})

# Register as ADK tool
get_student_metrics_tool = FunctionTool(get_student_metrics)
```

### Tool 4: `update_pilot_metrics`

```python
def update_pilot_metrics(
    user_id: str,
    weakness_tags: list = None,
    strength_tags: list = None,
    completion_rate: int = None,
    total_study_hours: float = None,
    last_quiz_score: int = None
) -> str:
    """
    Updates pilot_metrics object (used by Admin Agent for grading).
    
    Args:
        user_id: Firebase Auth UID
        weakness_tags: Optional - List of weak topic tags
        strength_tags: Optional - List of strong topic tags
        completion_rate: Optional - Percentage complete (0-100)
        total_study_hours: Optional - Cumulative study time
        last_quiz_score: Optional - Most recent quiz result
    
    Returns:
        str: Success message or error
    """
    doc_ref = db.collection("users").document(user_id)
    
    metrics = {}
    if weakness_tags is not None:
        metrics["pilot_metrics.weakness_tags"] = weakness_tags
    if strength_tags is not None:
        metrics["pilot_metrics.strength_tags"] = strength_tags
    if completion_rate is not None:
        metrics["pilot_metrics.completion_rate"] = completion_rate
    if total_study_hours is not None:
        metrics["pilot_metrics.total_study_hours"] = total_study_hours
    if last_quiz_score is not None:
        metrics["pilot_metrics.last_quiz_score"] = last_quiz_score
    
    try:
        doc_ref.update(metrics)
        return f"Metrics updated for {user_id}"
    except Exception as e:
        return f"Error updating metrics: {str(e)}"

# Register as ADK tool
update_pilot_metrics_tool = FunctionTool(update_pilot_metrics)
```

### Tool 5: `check_assignment_history`

```python
def check_assignment_history(user_id: str, item_id: str) -> bool:
    """
    Check if user already completed a specific question/lesson.
    
    Args:
        user_id: Firebase Auth UID
        item_id: Question or lesson identifier
    
    Returns:
        bool: True if already completed
    """
    doc_ref = db.collection("users").document(user_id) \
        .collection("completed_items").document(item_id)
    
    return doc_ref.get().exists

# Register as ADK tool
check_assignment_history_tool = FunctionTool(check_assignment_history)
```

---

## Common Patterns

### Pattern 1: Pre-Load Profile on Login

```python
# backend/app.py
@app.get("/api/profile/get/{user_id}")
async def get_profile_endpoint(user_id: str):
    """
    Called by ProfileContext on user login.
    Checks completeness and staleness.
    """
    profile = get_student_profile(user_id)
    
    if not profile:
        return {
            "profile": None,
            "needs_onboarding": True,
            "reason": "no_profile"
        }
    
    # Check completeness
    is_complete, reason = validate_profile_complete(profile)
    if not is_complete:
        return {
            "profile": profile,
            "needs_onboarding": True,
            "reason": "incomplete"
        }
    
    # Check staleness
    if is_profile_stale(profile):
        return {
            "profile": profile,
            "needs_onboarding": True,
            "reason": "stale"
        }
    
    return {
        "profile": profile,
        "needs_onboarding": False,
        "reason": "complete"
    }
```

### Pattern 2: TA Agent Registration

```python
# backend/agents/specialists/ta/agent.py
from google.adk.agents import LlmAgent
from google.genai import Gemini

ta_agent = LlmAgent(
    name="ta_agent",
    model=Gemini(model="gemini-3.1-flash-lite-preview-preview"),
    tools=[
        get_student_profile_tool,
        update_student_profile_tool,
        get_student_metrics_tool,
        update_pilot_metrics_tool,
        check_assignment_history_tool
    ],
    instruction="""You are the TA Agent (Teaching Assistant).
    
    YOUR ROLE:
    - Master of user data (profiles, metrics, history)
    - Provide student context to other agents
    - Update profiles and track progress
    
    YOUR TOOLS:
    - get_student_profile: Fetch pilot profile
    - update_student_profile: Save profile changes
    - get_student_metrics: Get weakness/strength tags
    - update_pilot_metrics: Save quiz grades
    - check_assignment_history: Prevent repeat questions
    """
)
```

### Pattern 3: Cross-Agent Data Sharing

```python
# backend/services/specialist_orchestrator.py
async def handle_specialist_chat(user_id: str, message: str):
    """
    Specialist agent needs user context.
    """
    # Step 1: TA Agent fetches profile
    profile = get_student_profile(user_id)
    
    # Step 2: Build context for Specialist
    context = f"""
    STUDENT PROFILE:
    - Name: {profile.get('name')}
    - Call Sign: {profile.get('call_sign')}
    - Current Rating: {profile.get('current_rating')}
    - Target: {profile.get('checkride_type')}
    - Weaknesses: {profile.get('pilot_metrics', {}).get('weakness_tags', [])}
    
    USER MESSAGE: {message}
    """
    
    # Step 3: Specialist uses context to tailor response
    response = await specialist_agent.generate(context)
    return response
```

---

## Error Handling

### Missing Profile
```python
profile = get_student_profile(user_id)
if not profile:
    # Trigger HR Agent to collect profile
    return {"action": "open_hr_chat"}
```

### Firestore Connection Error
```python
try:
    doc_ref.set(data, merge=True)
except Exception as e:
    logger.error(f"Firestore write failed: {e}")
    return {"error": "Could not save data. Please try again."}
```

### Concurrent Writes
```python
# Use Firestore transactions for atomic updates
from google.cloud.firestore import firestore

@firestore.transactional
def update_metrics_atomic(transaction, doc_ref, new_score):
    snapshot = doc_ref.get(transaction=transaction)
    old_score = snapshot.get("pilot_metrics.last_quiz_score") or 0
    
    if new_score > old_score:
        transaction.update(doc_ref, {
            "pilot_metrics.last_quiz_score": new_score
        })
```

---

## Performance Optimization

### Caching Strategy
- **Frontend:** Cache profile in React Context (invalidate on update)
- **Backend:** Use InMemorySessionService for 15-minute cache
- **Database:** Index on `checkride_type`, `status` for fast queries

### Batch Operations
```python
# Writing multiple documents
batch = db.batch()

for item in completed_items:
    doc_ref = db.collection("users").document(user_id) \
        .collection("completed_items").document(item["id"])
    batch.set(doc_ref, item)

batch.commit()  # Single network round-trip
```

---

## Testing

### Unit Test: Profile Validation
```python
def test_validate_profile():
    complete = {
        "name": "Daniel",
        "call_sign": "D-ICE",
        "current_rating": "Student",
        "checkride_type": "Private",
        "checkride_date": "2026-03-01"
    }
    assert validate_profile_complete(complete) == (True, "complete")
    
    incomplete = {"name": "Daniel"}
    assert validate_profile_complete(incomplete) == (False, "missing_call_sign")
```

### Integration Test: CRUD Operations
```python
def test_profile_crud():
    # Create
    result = update_student_profile("test_uid", name="Test", call_sign="TEST")
    assert "successfully" in result
    
    # Read
    profile = get_student_profile("test_uid")
    assert profile["name"] == "Test"
    
    # Update
    update_student_profile("test_uid", call_sign="MAVERICK")
    profile = get_student_profile("test_uid")
    assert profile["call_sign"] == "MAVERICK"
    
    # Delete (cleanup)
    db.collection("users").document("test_uid").delete()
```

---

## Security Rules

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      
      // Completed items sub-collection
      match /completed_items/{itemId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
    
    // Question bank is read-only for all authenticated users
    match /question_bank/{questionId} {
      allow read: if request.auth != null;
      allow write: if false;  // Only backend can write
    }
  }
}
```

---

## Related Skills

- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - How agents coordinate
- [agent-handoff-patterns.md](../agent-handoff-patterns/SKILL.md) - Context transfer protocols

---

## Summary

**Key Takeaways:**

1. **TA Agent is the hub** - All Firestore operations go through TA tools
2. **Three core collections** - `users`, `question_bank`, `completed_items`
3. **Auto-timestamps** - `last_active` updates on every write
4. **Staleness = 30 days** - Trigger re-onboarding if inactive
5. **Partial updates** - Use `merge=True` to avoid overwriting fields

Following these patterns ensures **data consistency**, **audit trails**, and **clean agent separation**.
