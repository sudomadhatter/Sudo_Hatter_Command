---
description: AviationChat's Dual-Store RAG topology with Vertex AI Search, Bridge Keys, and hybrid retrieval
---

# AviationChat RAG Implementation

**Domain:** AviationChat-AGY  
**Use When:** Implementing Librarian tools, debugging retrieval, or optimizing query performance

---

## Core Architecture: Dual-Store Topology

AviationChat uses **TWO separate databases** for different purposes:

- **DB1 (The Curriculum):** Teaching content, pedagogical explanations
- **DB2 (The Library):** Official regulations, FAA manuals, citations

**Why Two Databases?**
- ✅ **Teach from pedagogy** (DB1 lesson plans)
- ✅ **Verify from law** (DB2 regulatory text)
- ✅ **Prevent hallucinations** (cross-reference between databases)

See [dual-store-rag-patterns.md](../dual-store-rag-patterns/SKILL.md) for complete implementation.

---

## Technology Stack

### Vertex AI Search (NOT Custom Vector Store)

**Why Vertex AI Search?**
- Managed service (no infrastructure)
- Hybrid search built-in (sparse + dense)
- Metadata filtering for DB2
- Scales automatically

**Configuration:**
```python
from google.cloud import discoveryengine_v1 as discoveryengine

client = discoveryengine.SearchServiceClient()

# DB1: Aviation Curriculum
curriculum_datastore = "aviation-curriculum-v1"

# DB2: Aviation Library
library_datastore = "aviation-library-v1"
```

---

## Database 1: The Curriculum

### Content Structure

**Format:** Markdown with embedded metadata

```markdown
### PA.I.A.K1: Certification requirements, recent flight experience

[Context: Preflight Preparation > Pilot Qualifications]

1. The Oral Standard (The Direct Answer)
To act as pilot in command, you must hold a valid certificate...

4. Bridge Keys (Metadata)
* **Regs:** 14 CFR 61.56, 14 CFR 61.57
* **Docs:** PHAK Chapter 9
```

### JSONL Manifest (Sidecar)

```json
{
  "id": "lesson_pa_i_a_k1",
  "structData": {
    "acs_code": "PA.I.A.K1",
    "ancestral_context": "Preflight Preparation > Pilot Qualifications",
    "reg_keys": ["14 CFR 61.56", "14 CFR 61.57"],
    "doc_keys": ["PHAK Chapter 9"]
  },
  "content": {
    "mimeType": "text/markdown",
    "uri": "gs://aviation-curriculum/lessons/lesson_pa_i_a_k1.md"
  }
}
```

### Retrieval Strategy

**Hybrid Search ONLY** (no filters)
- Combines keyword + semantic search
- Returns top 5 chunks
- Used by Expert B (Curriculum Specialist)

```python
def search_curriculum_hybrid(query: str, top_k: int = 5):
    request = discoveryengine.SearchRequest(
        serving_config=f"projects/{project}/locations/global/dataStores/{curriculum_datastore}/servingConfigs/default_config",
        query=query,
        page_size=top_k
    )
    response = client.search(request)
    return [r.document for r in response.results]
```

---

## Database 2: The Library

### Content Structure

**Format:** PDFs (official FAA documents)

- FAR/AIM
- PHAK (Pilot's Handbook)
- AFH (Airplane Flying Handbook)
- Advisory Circulars (ACs)

### JSONL Manifest

```json
{
  "id": "doc_far_part_91",
  "structData": {
    "type": "regulation",
    "doc_id": "14 CFR 91",
    "section": "Part 91"
  },
  "content": {
    "mimeType": "application/pdf",
    "uri": "gs://aviation-library/regulations/far_part_91.pdf"
  }
}
```

### Retrieval Strategy

**Hybrid Search + Metadata Filtering**
- Filter by document type (regulation, handbook, advisory)
- Used by Expert A (Regulatory Hunter) and Expert C (Library Search)

```python
def search_library_hybrid(query: str, doc_type: str = None, top_k: int = 3):
    filter_str = f'type: "{doc_type}"' if doc_type else None
    
    request = discoveryengine.SearchRequest(
        serving_config=f"projects/{project}/locations/global/dataStores/{library_datastore}/servingConfigs/default_config",
        query=query,
        page_size=top_k,
        filter=filter_str
    )
    response = client.search(request)
    return [r.document for r in response.results]
```

---

## The Bridge Key Strategy

**Problem:** How do we know which regulations to verify?

**Solution:** Curriculum embeds regulatory sources as metadata.

### How It Works

1. **Curriculum has Bridge Keys:**
```markdown
**Regs:** 14 CFR 61.56, 14 CFR 61.57
```

2. **Extract during retrieval:**
```python
curriculum_result = search_curriculum_hybrid("flight review")
reg_keys = curriculum_result['structData']['reg_keys']
# ['14 CFR 61.56', '14 CFR 61.57']
```

3. **Query library using Bridge Keys:**
```python
for reg in reg_keys:
    library_result = search_library_hybrid(reg, doc_type="regulation")
    # Returns exact FAR text
```

4. **Compare for verification:**
- If curriculum matches library → Verified ✓
- If they differ → Trigger Swap event

---

## Hybrid Search Configuration

### What is Hybrid Search?

Combines two retrieval methods:
1. **Sparse (BM25):** Keyword matching (exact terms)
2. **Dense (Vector):** Semantic similarity (concepts)

### Why Hybrid for Aviation?

✅ **Precise terminology** - "VFR" vs "IFR"  
✅ **Regulatory citations** - "14 CFR 91.205"  
✅ **Acronyms** - "FAR", "AIM", "ACS"

**Pure vector search** might confuse similar concepts.  
**Hybrid search** ensures exact term matching.

---

## Query Optimization Patterns

### Pattern 1: Pre-Warm on Login

```python
async def pre_warm_user_topics(user_id: str):
    """Fetch likely topics before user asks."""
    profile = get_student_profile(user_id)
    weakness_tags = profile.get("pilot_metrics", {}).get("weakness_tags", [])
    
    for topic in weakness_tags:
        # Pre-fetch and cache
        context = search_curriculum_hybrid(topic, top_k=5)
        session_service.set_cache(user_id, f"topic_{topic}", context, ttl=900)
```

**Why?** User's first query on weak topics feels instant.

---

### Pattern 2: Parallel Expert Dispatch

```python
import asyncio

async def dispatch_investigation_swarm(query: str):
    """Run all three experts in parallel."""
    tasks = [
        search_library_hybrid(query, doc_type="regulation"),  # Expert A
        search_curriculum_hybrid(query),                       # Expert B
        search_library_hybrid(query)                           # Expert C (wide)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "regulatory": results[0],
        "curriculum": results[1],
        "wide_search": results[2]
    }
```

**Timing:** All three complete in ~2-3s (parallel), not 6-9s (sequential).

---

### Pattern 3: Cache Curriculum, Not Library

```python
# ✅ CACHE curriculum queries (content stable)
cache_key = f"curriculum:{query_hash}"
cached = session_service.get(cache_key)
if cached:
    return cached

results = search_curriculum_hybrid(query)
session_service.set(cache_key, results, ttl=900)  # 15 min

# ❌ DON'T cache library queries (regulations may update)
results = search_library_hybrid(query)
return results  # Always fresh
```

---

## Sharp Edges & Solutions

### Issue 1: Empty Results

**Problem:** Query returns 0 results

**Solutions:**
```python
results = search_curriculum_hybrid("obscure topic")

if not results:
    # Fallback 1: Try library wide search
    results = search_library_hybrid("obscure topic")
    
if not results:
    # Fallback 2: Use cached generic answer
    results = session_service.get_cache(user_id, "last_results")
    
if not results:
    # Fallback 3: Graceful message
    return {"message": "I don't have specific content on that yet."}
```

---

### Issue 2: Query Timeout

**Problem:** Vertex AI query takes > 3s

**Solution:**
```python
import asyncio

try:
    results = await asyncio.wait_for(
        search_curriculum_hybrid(query),
        timeout=3.0
    )
except asyncio.TimeoutError:
    logger.warning(f"Query timeout: {query}")
    # Show unverified response
    yield {"type": "badge", "status": "unverified"}
```

---

### Issue 3: Irrelevant Results

**Problem:** Top result doesn't match query intent

**Solution: Reranking with LLM**
```python
async def rerank_results(query: str, results: list) -> list:
    """Use LLM to score relevance."""
    prompt = f"""
    Query: {query}
    
    Results:
    {json.dumps([r['content'][:200] for r in results])}
    
    Rank these results by relevance (1 = most relevant).
    Return JSON: {{"rankings": [3, 1, 2]}}
    """
    
    rankings = await gemini.generate(prompt)
    return [results[i] for i in rankings]
```

**Trade-off:** Adds 500ms latency, but improves accuracy.

---

## Anti-Patterns

### ❌ Querying Both DBs with Same Query

```python
# BAD: Same query for curriculum and library
curriculum = search_curriculum_hybrid("VFR weather minimums")
library = search_library_hybrid("VFR weather minimums")
# Wastes tokens, redundant results
```

### ✅ Correct: Use Bridge Keys

```python
# GOOD: Curriculum first, then targeted library lookup
curriculum = search_curriculum_hybrid("VFR weather minimums")
reg_keys = curriculum['structData']['reg_keys']

for reg in reg_keys:
    library = search_library_hybrid(reg, doc_type="regulation")
    # Precise regulatory backing
```

---

### ❌ Not Using Metadata Filters

```python
# BAD: Wide search when you need regulations
results = search_library_hybrid("14 CFR 91.205")
# Returns handbooks, ACs, everything
```

### ✅ Correct: Filter by Type

```python
# GOOD: Filter to regulations only
results = search_library_hybrid("14 CFR 91.205", doc_type="regulation")
# Returns only FAR text
```

---

## Related Skills

- [dual-store-rag-patterns.md](../dual-store-rag-patterns/SKILL.md) - Complete dual-store implementation
- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - How Investigation Swarm uses RAG
- [regulatory-verification-protocol.md](../regulatory-verification-protocol/SKILL.md) - Using DB2 for verification

---

## Summary

**Key Principles:**
1. **Dual-Store Topology** - DB1 for teaching, DB2 for verification
2. **Bridge Keys** - Curriculum embeds regulatory sources
3. **Hybrid Search** - Combines keyword + semantic for precision
4. **Parallel Retrieval** - Run all experts simultaneously
5. **Cache Curriculum** - Don't cache regulations (always fresh)

This ensures **accurate teaching** backed by **verified regulations**.
