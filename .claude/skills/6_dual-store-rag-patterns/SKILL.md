---
description: AviationChat's Dual-Store Hybrid RAG topology (DB1 Curriculum + DB2 Regulations)
---

# Dual-Store RAG Patterns

**Skill Type:** Data Retrieval Pattern  
**Domain:** AviationChat-AGY  
**Use When:** Implementing Librarian tools, building retrieval queries, or debugging RAG responses

---

## Core Philosophy

AviationChat uses a **Dual-Store Topology** that separates teaching content from regulatory verification:

- **Database 1 (The Curriculum):** High-fidelity lesson plans optimized for teaching
- **Database 2 (The Library):** Official FAA manuals for verification and citations

This separation ensures we **teach from pedagogy** but **verify from law**.

---

## The Two Databases

### Database 1: The Curriculum ("The Anchor")

**Purpose:** Primary teaching source  
**Technology:** Vertex AI Search (Unstructured, Hybrid Search)  
**Content:** Markdown lesson plans mapped to ACS codes  
**Data Store ID:** `aviation-curriculum-v1`

**Content Structure:**
```markdown
### PA.I.A.K1: Certification requirements, recent flight experience

[Context: Preflight Preparation > Pilot Qualifications > Certification & Currency]

1. The Oral Standard (The Direct Answer)
To act as pilot in command, you must hold a valid pilot certificate 
and medical certificate appropriate for the operation...

4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 61.56, 14 CFR 61.57, 14 CFR 61.51
* **Docs:** AC 61-98D, PHAK Chapter 9
* **Keywords:** Flight Review, Solo Privileges, Currency
```

**Search Strategy:** Hybrid Search ONLY (no metadata filtering)
- Combines sparse keyword matching + dense vector similarity
- Relies on embedded ancestral context (Area > Task > Topic)
- Returns top 3-5 chunks per query

**Sidecar Schema (JSONL Manifest):**
```json
{
  "id": "lesson_pa_i_a_k1",
  "structData": {
    "acs_code": "PA.I.A.K1",
    "title": "Certification requirements, recent flight experience",
    "type": "lesson_chunk",
    "ancestral_context": "Preflight Preparation > Pilot Qualifications",
    "reg_keys": ["14 CFR 61.56", "14 CFR 61.57", "14 CFR 61.51"],
    "doc_keys": ["AC 61-98D", "FAA-H-8083-25C"],
    "keywords": ["Flight Review", "Solo", "Currency"]
  },
  "content": {
    "mimeType": "text/markdown",
    "uri": "gs://aviation-curriculum/lessons/lesson_pa_i_a_k1.md"
  }
}
```

---

### Database 2: The Library ("The Truth")

**Purpose:** Regulatory verification and citation source  
**Technology:** Vertex AI Search (Unstructured, Hybrid Search + Metadata Filtering)  
**Content:** Official FAA manuals (FAR/AIM, PHAK, AFH, ACs) in PDF  
**Data Store ID:** `aviation-library-v1`

**Document Types:**
- **Regulations:** 14 CFR (FAR), AIM
- **Handbooks:** PHAK, AFH, Helicopter Handbook
- **Advisory Circulars:** AC 61-98D, AC 91-73B
- **Safety Alerts:** NTSB, FAA Safety Briefs

**Search Strategy:** Hybrid Search + Metadata Filtering
- Filter by document type (regulation, handbook, advisory)
- Filter by specific regulation part (CFR 91, CFR 61)
- Wide search when no filters (catch edge cases)

**Sidecar Schema:**
```json
{
  "id": "doc_far_part_91",
  "structData": {
    "type": "regulation",
    "doc_id": "14 CFR 91",
    "title": "General Operating and Flight Rules",
    "section": "Part 91"
  },
  "content": {
    "mimeType": "application/pdf",
    "uri": "gs://aviation-library/regulations/far_part_91.pdf"
  }
}
```

---

## When to Use Which Database

### Use DB1 (Curriculum) When:

✅ **Teaching a concept**
- User asks: "What is VFR?"
- User asks: "Explain spin recovery"
- "Teach Me" button clicked

✅ **Generating quiz questions**
- Need ACS-aligned questions
- Need pedagogical explanations

✅ **Building lesson context**
- Pre-warming cache with topic overview
- Providing study material structure

**Tool:** `search_curriculum_hybrid(query)`

---

### Use DB2 (Library) When:

✅ **Verifying citations**
- Talker mentioned "14 CFR 91.205"
- Need exact regulation text

✅ **Finding safety risks**
- Wide search for NTSB alerts
- Advisory circulars on specific topics

✅ **Answering regulatory questions**
- User asks: "What does the FAR say about..."
- User asks: "Is that legal?"

**Tools:** 
- `search_library_hybrid(query, doc_type="regulation")`
- `search_library_hybrid(query, doc_type="handbook")`
- `search_library_hybrid(query)` (wide search, no filters)

---

### Use BOTH (Bridge Key Strategy) When:

✅ **Deep dive teaching**
- Curriculum provides pedagogy
- Library provides official backing

✅ **Verification workflow**
- DB1 provides answer + Bridge Keys
- DB2 verifies using those Bridge Keys

**Example:**
```python
# Step 1: Search curriculum
curriculum_result = search_curriculum_hybrid("medical certificate requirements")
# Returns: PA.I.A.K3 chunk with Bridge Keys ["14 CFR 61.23", "FAR/AIM"]

# Step 2: Extract Bridge Keys
bridge_keys = curriculum_result['structData']['reg_keys']
# ["14 CFR 61.23"]

# Step 3: Query library using Bridge Keys
for reg in bridge_keys:
    verification = search_library_hybrid(reg, doc_type="regulation")
    # Returns: Exact FAR text from Part 61
```

---

## The Bridge Key Strategy

**Problem:** Curriculum might be outdated or incomplete  
**Solution:** Embed regulatory sources in curriculum metadata, then cross-reference

### How It Works

1. **Curriculum Chunk Has Bridge Keys:**
```markdown
**Regs:** 14 CFR 61.56, 14 CFR 61.57, 14 CFR 61.51
```

2. **Extract During Retrieval:**
```python
result = search_curriculum_hybrid("flight review requirements")
reg_keys = result['structData']['reg_keys']
# ['14 CFR 61.56', '14 CFR 61.57', '14 CFR 61.51']
```

3. **Query Library for Verification:**
```python
for reg in reg_keys:
    exact_text = search_library_hybrid(
        query=reg,
        doc_type="regulation"
    )
    # Returns: Official CFR text
```

4. **Compare Curriculum vs. Library:**
- If they match → Verified ✓
- If they differ → Trigger Swap event

---

## Implementation: Librarian Tools

### Tool 1: `search_curriculum_hybrid`

```python
from google.cloud import discoveryengine_v1 as discoveryengine
from google.genai.tools import FunctionTool

def search_curriculum_hybrid(query: str, top_k: int = 5) -> list:
    """
    Searches Database 1 (Curriculum) using Hybrid Search.
    
    Args:
        query: Natural language or keyword search
        top_k: Number of results to return (default 5)
    
    Returns:
        list: Curriculum chunks with metadata
    """
    client = discoveryengine.SearchServiceClient()
    
    serving_config = client.serving_config_path(
        project=os.getenv("GCP_PROJECT_ID"),
        location="global",
        data_store="aviation-curriculum-v1",
        serving_config="default_config"
    )
    
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=top_k,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.CHUNKS,
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                max_snippet_count=3
            )
        )
    )
    
    response = client.search(request)
    
    results = []
    for result in response.results:
        chunk = result.document.derived_struct_data
        results.append({
            "id": result.document.id,
            "content": chunk.get("content", ""),
            "acs_code": chunk.get("acs_code", ""),
            "reg_keys": chunk.get("reg_keys", []),
            "doc_keys": chunk.get("doc_keys", []),
            "relevance_score": result.relevance_score
        })
    
    return results

# Register as ADK tool
search_curriculum_tool = FunctionTool(search_curriculum_hybrid)
```

---

### Tool 2: `search_library_hybrid`

```python
def search_library_hybrid(
    query: str,
    doc_type: str = None,
    top_k: int = 3
) -> list:
    """
    Searches Database 2 (Library) using Hybrid Search + Metadata Filtering.
    
    Args:
        query: Regulation citation or search term
        doc_type: Optional filter - "regulation", "handbook", "advisory_circular"
        top_k: Number of results to return (default 3)
    
    Returns:
        list: Library chunks with exact regulatory text
    """
    client = discoveryengine.SearchServiceClient()
    
    serving_config = client.serving_config_path(
        project=os.getenv("GCP_PROJECT_ID"),
        location="global",
        data_store="aviation-library-v1",
        serving_config="default_config"
    )
    
    # Build filter string if doc_type specified
    filter_str = None
    if doc_type:
        filter_str = f'type: "{doc_type}"'
    
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=top_k,
        filter=filter_str,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.CHUNKS
        )
    )
    
    response = client.search(request)
    
    results = []
    for result in response.results:
        chunk = result.document.derived_struct_data
        results.append({
            "id": result.document.id,
            "content": chunk.get("content", ""),
            "doc_id": chunk.get("doc_id", ""),
            "type": chunk.get("type", ""),
            "citation": chunk.get("doc_id", "") + " - " + chunk.get("title", ""),
            "relevance_score": result.relevance_score
        })
    
    return results

# Register as ADK tool
search_library_tool = FunctionTool(search_library_hybrid)
```

---

### Tool 3: `verify_with_bridge_keys`

```python
async def verify_with_bridge_keys(curriculum_chunk: dict) -> dict:
    """
    Uses Bridge Keys from curriculum to verify against library.
    
    Args:
        curriculum_chunk: Result from search_curriculum_hybrid
    
    Returns:
        dict: Verification results with regulatory backing
    """
    reg_keys = curriculum_chunk.get("reg_keys", [])
    doc_keys = curriculum_chunk.get("doc_keys", [])
    
    verification = {
        "curriculum_content": curriculum_chunk["content"],
        "regulatory_backing": [],
        "handbook_backing": []
    }
    
    # Query regulations
    for reg in reg_keys:
        results = search_library_hybrid(reg, doc_type="regulation", top_k=1)
        if results:
            verification["regulatory_backing"].append({
                "citation": reg,
                "text": results[0]["content"]
            })
    
    # Query handbooks
    for doc in doc_keys:
        results = search_library_hybrid(doc, doc_type="handbook", top_k=1)
        if results:
            verification["handbook_backing"].append({
                "citation": doc,
                "text": results[0]["content"]
            })
    
    return verification

verify_bridge_keys_tool = FunctionTool(verify_with_bridge_keys)
```

---

## Hybrid Search Configuration

### What is Hybrid Search?

Combines two retrieval methods:
1. **Sparse (Keyword):** BM25 algorithm, exact term matching
2. **Dense (Vector):** Semantic similarity, concept matching

**Example:**
- Query: "medical certificate class 3"
- Sparse matches: "medical", "certificate", "class", "3"
- Dense matches: Concepts like "pilot fitness", "FAA requirements"

### When to Use Hybrid vs. Pure Vector

✅ **Use Hybrid (Default):**
- Regulatory citations (need exact term "91.205")
- Technical terms (e.g., "empennage", "aileron")
- Acronyms (FAR, AIM, ACS)

❌ **Pure Vector (Not Implemented):**
- Conversational queries ("how do I get my license?")
- Paraphrased questions

**Why Hybrid?** Aviation has precise terminology. Missing "VFR" vs "IFR" changes the answer.

---

## Query Optimization Patterns

### Pattern 1: Topic Shift (Reactive Retrieval)

```python
async def handle_topic_shift(old_topic: str, new_topic: str, user_id: str):
    """
    User shifts from Airspace → Spin Recovery.
    Drop old cache, fetch new context.
    """
    # Clear old session cache
    session_service.clear_cache(user_id)
    
    # Fetch new curriculum context
    new_context = search_curriculum_hybrid(new_topic, top_k=3)
    
    # Pre-warm cache (write to InMemorySessionService)
    session_service.set_cache(user_id, "topic_context", new_context)
    
    # Log psychometric event (TA Agent)
    update_pilot_metrics(
        user_id,
        weakness_tags=[old_topic]  # User avoided this topic
    )
```

---

### Pattern 2: Pre-Game Warm-Up (Proactive Retrieval)

```python
async def pre_warm_on_login(user_id: str):
    """
    Between login and first message, pre-fetch likely topics.
    """
    # Get user profile
    profile = get_student_profile(user_id)
    weakness_tags = profile.get("pilot_metrics", {}).get("weakness_tags", [])
    
    # If user is weak on "weather", pre-fetch weather content
    for topic in weakness_tags:
        context = search_curriculum_hybrid(topic, top_k=5)
        session_service.set_cache(user_id, f"prefetch_{topic}", context)
    
    # Now when user asks about weather, cache hit!
```

---

### Pattern 3: Wide-Net Safety Search

```python
async def safety_audit(user_query: str) -> list:
    """
    Expert C: Wide search of DB2 to catch safety risks.
    """
    # No filters - search entire library
    results = search_library_hybrid(user_query, doc_type=None, top_k=10)
    
    safety_items = []
    for result in results:
        # Flag NTSB alerts, AC safety notices
        if "NTSB" in result["content"] or "Safety Alert" in result["content"]:
            safety_items.append(result)
    
    return safety_items
```

---

## Error Handling

### Database Timeout

```python
import asyncio

try:
    results = await asyncio.wait_for(
        search_curriculum_hybrid(query),
        timeout=3.0
    )
except asyncio.TimeoutError:
    # Fallback: Use cached response or generic answer
    results = session_service.get_cache(user_id, "last_query_results") or []
```

### Empty Results

```python
results = search_curriculum_hybrid("nonexistent topic")

if not results:
    # Graceful fallback
    fallback_message = "I don't have specific curriculum on that topic yet. Let me search the regulations..."
    results = search_library_hybrid("nonexistent topic")
```

### Malformed Bridge Keys

```python
reg_keys = curriculum_chunk.get("reg_keys", [])

# Validate format
valid_keys = []
for key in reg_keys:
    if re.match(r"14 CFR \d+\.\d+", key):
        valid_keys.append(key)
    else:
        logger.warning(f"Invalid Bridge Key format: {key}")

# Only query valid keys
```

---

## Performance Optimization

### Caching Strategy

**InMemorySessionService (15-minute TTL):**
```python
# Cache curriculum queries
cache_key = f"curriculum:{query_hash}"
cached = session_service.get(cache_key)

if cached:
    return cached

results = search_curriculum_hybrid(query)
session_service.set(cache_key, results, ttl=900)  # 15 min
```

**Don't Cache:**
- Library searches (regulations may update)
- Verification results (always verify fresh)

---

### Batch Queries

```python
async def batch_bridge_key_lookup(reg_keys: list) -> dict:
    """
    Query multiple regulations in parallel.
    """
    tasks = [
        search_library_hybrid(reg, doc_type="regulation")
        for reg in reg_keys
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        reg_keys[i]: results[i]
        for i in range(len(reg_keys))
    }
```

---

## Testing

### Test Case 1: Curriculum Search

```python
def test_curriculum_search():
    results = search_curriculum_hybrid("medical certificate requirements")
    
    assert len(results) > 0
    assert "PA.I.A.K3" in results[0]["acs_code"]
    assert "14 CFR 61.23" in results[0]["reg_keys"]
```

### Test Case 2: Library Filtering

```python
def test_library_filter():
    results = search_library_hybrid(
        "oxygen requirements",
        doc_type="regulation"
    )
    
    assert len(results) > 0
    assert results[0]["type"] == "regulation"
    assert "14 CFR" in results[0]["doc_id"]
```

### Test Case 3: Bridge Key Verification

```python
async def test_bridge_key_flow():
    # Step 1: Get curriculum
    curriculum = search_curriculum_hybrid("flight review")[0]
    
    # Step 2: Verify
    verification = await verify_with_bridge_keys(curriculum)
    
    # Step 3: Check backing
    assert len(verification["regulatory_backing"]) > 0
    assert "14 CFR 61.56" in verification["regulatory_backing"][0]["citation"]
```

---

## Related Skills

- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - How Experts A/B/C use these tools
- [regulatory-verification-protocol.md](../regulatory-verification-protocol/SKILL.md) - How to verify citations

---

## Summary

**Key Takeaways:**

1. **DB1 = Teaching, DB2 = Verification** - Different purposes, different content
2. **Bridge Keys** - Curriculum embeds regulatory sources for cross-referencing
3. **Hybrid Search** - Combines keyword + vector for aviation precision
4. **Three Librarian Tools** - `search_curriculum`, `search_library`, `verify_bridge_keys`
5. **Cache Curriculum, Not Library** - Regulations must always be fresh

The Dual-Store topology ensures we **teach effectively** while **verifying accurately**.
