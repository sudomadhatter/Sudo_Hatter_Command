---
description: Ensuring citation accuracy and preventing hallucinations in aviation content
---

# Regulatory Verification Protocol

**Skill Type:** Quality Assurance Pattern  
**Domain:** AviationChat-AGY  
**Use When:** Implementing Verifier agent, reviewing Talker output, or debugging citation errors

---

## The Golden Rule

> **NEVER fabricate FAR/AIM references. If uncertain, mark as unverified.**

Aviation is safety-critical. A fabricated regulation citation (e.g., "Per 14 CFR 99.999...") could:
- Cause a student to fail their checkride
- Lead to regulatory violations
- Create liability for the platform
- Destroy user trust

**Philosophy:** It's better to say **"unverified"** than to be **wrong**.

---

## Core Principle: Regulatory Accuracy Over Speed

From the Master PRD:
> "We prioritize regulatory accuracy over speed, ensuring the 'Fast Talker' is fact-checked against specific Legal, Pedagogical, and Safety standards."

This is AviationChat's **core differentiator**. Other chatbots are fast but unreliable. We are **both fast AND accurate** through the 3-lane pattern.

---

## What Must Be Verified

### ✅ Always Verify

1. **Regulatory Citations**
   - 14 CFR references (FAR)
   - AIM sections
   - Advisory Circulars (ACs)

2. **Safety-Critical Procedures**
   - Emergency procedures (spin recovery, engine failure)
   - Weather minimums (VFR, IFR)
   - Equipment requirements (91.205, 91.207)

3. **Legal Requirements**
   - Pilot certificate requirements
   - Medical certificate classes
   - Currency requirements (61.56, 61.57)

4. **Numerical Values**
   - Altitudes (e.g., "18,000 feet for Class A")
   - Speeds (e.g., "250 knots below 10,000 MSL")
   - Distances (e.g., "3 SM visibility for VFR")

### ❌ Don't Verify (Skip for Efficiency)

1. **Casual Conversation**
   - User: "Thank you!"
   - Talker: "You're welcome!"
   - **Action:** Skip verification (no regulatory content)

2. **Acknowledgments**
   - User: "Got it"
   - Talker: "Great! Let me know if you have questions."
   - **Action:** Skip verification

3. **Pedagogical Explanations**
   - Talker: "Think of lift as the force opposing weight..."
   - **Action:** Verify only if it references a specific regulation

4. **General Aviation Knowledge**
   - Talker: "The four forces of flight are lift, weight, thrust, and drag."
   - **Action:** Skip (common knowledge, not regulatory)

**Rule of Thumb:** If it mentions "14 CFR", "FAR", "AIM", or specific numbers/requirements, **verify**.

---

## The Verification Checklist

### Step 1: Extract Claims from Talker Output

```python
def extract_verifiable_claims(talker_text: str) -> list:
    """
    Identify claims that need verification.
    """
    claims = []
    
    # Look for regulatory citations
    far_matches = re.findall(r'14 CFR [\d.]+', talker_text)
    aim_matches = re.findall(r'AIM [\d-]+', talker_text)
    
    for citation in far_matches + aim_matches:
        claims.append({
            "type": "citation",
            "claim": citation,
            "context": extract_sentence_containing(talker_text, citation)
        })
    
    # Look for numerical requirements
    number_patterns = [
        r'(\d+,?\d*)\s*(feet|knots|miles|nautical miles|SM)',
        r'(\d+)\s*(hours|days|months)',
        r'Class\s+([123ABC])\s+medical'
    ]
    
    for pattern in number_patterns:
        matches = re.finditer(pattern, talker_text)
        for match in matches:
            claims.append({
                "type": "numerical",
                "claim": match.group(0),
                "context": extract_sentence_containing(talker_text, match.group(0))
            })
    
    return claims
```

---

### Step 2: Query Library for Evidence

```python
async def gather_verification_evidence(claims: list) -> dict:
    """
    For each claim, fetch regulatory backing from DB2.
    """
    evidence = {}
    
    for claim in claims:
        if claim["type"] == "citation":
            # Direct lookup of regulation
            results = search_library_hybrid(
                query=claim["claim"],
                doc_type="regulation",
                top_k=1
            )
            evidence[claim["claim"]] = results[0] if results else None
        
        elif claim["type"] == "numerical":
            # Broader search with context
            results = search_library_hybrid(
                query=claim["context"],
                doc_type="regulation",
                top_k=3
            )
            evidence[claim["claim"]] = results
    
    return evidence
```

---

### Step 3: Compare Talker vs. Evidence

```python
def verify_claim(talker_claim: str, evidence: dict) -> dict:
    """
    Returns verification result.
    """
    if not evidence:
        return {
            "status": "unverified",
            "reason": "no_evidence_found",
            "action": "badge"
        }
    
    # Extract key facts
    talker_facts = extract_facts(talker_claim)
    evidence_facts = extract_facts(evidence["content"])
    
    # Check for contradictions
    contradictions = find_contradictions(talker_facts, evidence_facts)
    
    if contradictions:
        return {
            "status": "incorrect",
            "reason": "contradicts_regulation",
            "action": "swap",
            "correction": build_correction(evidence),
            "contradictions": contradictions
        }
    
    # Check for missing safety info
    missing = find_missing_critical_info(talker_claim, evidence["content"])
    
    if missing:
        return {
            "status": "incomplete",
            "reason": "missing_safety_info",
            "action": "elaborate",
            "addition": build_elaboration(missing)
        }
    
    # All good!
    return {
        "status": "verified",
        "reason": "matches_regulation",
        "action": "confirm",
        "citation": evidence["citation"]
    }
```

---

## Citation Formatting Rules

### Correct Formats

✅ **14 CFR (FAR) Citations:**
- `14 CFR 61.56` - Regulation with section
- `14 CFR 61.56(a)` - Regulation with subsection
- `14 CFR 91.205(b)(4)` - Regulation with nested subsections

✅ **AIM Citations:**
- `AIM 3-2-1` - Chapter-Section-Subsection
- `AIM Paragraph 3-2-1` - With "Paragraph" prefix

✅ **Advisory Circular Citations:**
- `AC 61-98D` - Advisory Circular with version
- `Advisory Circular 91-73B` - Full name with version

✅ **Handbook Citations:**
- `PHAK Chapter 7, page 12` - Pilot's Handbook with page
- `FAA-H-8083-25C, Chapter 4` - Full document ID

### Incorrect Formats (Red Flags)

❌ **Vague References:**
- "The FAR says..." (Which FAR?)
- "According to regulations..." (Which regulation?)
- "Part 91 requires..." (Which section of Part 91?)

❌ **Missing Version Numbers:**
- `AC 61-98` should be `AC 61-98D`
- `PHAK Chapter 7` should include version `FAA-H-8083-25C`

❌ **Paraphrased Regulations:**
- "The rule about flight reviews..." should cite `14 CFR 61.56`
- "Medical currency..." should specify `14 CFR 61.23`

❌ **Invented Citations:**
- `14 CFR 99.999` (doesn't exist)
- `FAR 22.5` (wrong format, should be 14 CFR)

---

## Verifier Agent Implementation

### Verifier Prompt

```python
verifier_agent = LlmAgent(
    name="verifier",
    model=Gemini(model="gemini-3.0-pro-preview"),  # Use Pro for reasoning
    instruction="""You are the Verifier Agent.

YOUR ROLE:
- Fact-check the Talker's output against regulatory evidence
- Identify contradictions, missing safety info, or unclear citations
- Issue corrections via Swap events when needed

YOUR INPUTS:
- TALKER OUTPUT: The streaming response from Lane 1
- REGULATORY EVIDENCE: Search results from DB2 (Experts A, B, C)
- CURRICULUM EVIDENCE: Search results from DB1

YOUR OUTPUTS:
- "confirm" + citation → Append [Verified ✓] badge
- "elaborate" + addition → Add missing context below
- "swap" + correction → Cross out error, show correction

VERIFICATION RULES:
1. Check for regulatory contradictions (most critical)
2. Check for missing safety warnings
3. Check citation format (e.g., "14 CFR 61.56" not "Part 61.56")
4. Verify numerical values (altitudes, speeds, distances)

DO NOT SWAP FOR:
- Stylistic differences
- Pedagogical explanations (unless factually wrong)
- Minor wording variations

ALWAYS:
- Cite the source of your correction (e.g., "Per 14 CFR 91.205(b)...")
- Be specific about what's wrong
- Provide the exact correct text
"""
)
```

---

### Swap Event Structure

```python
{
  "type": "swap",
  "timestamp": "2026-01-28T14:30:00Z",
  "original_text": "Strobes are required for day VFR operations.",
  "correction": "Strobes are NOT required for day VFR operations (only night VFR per 14 CFR 91.205(c)(3)).",
  "citation": "14 CFR 91.205(b) and 91.205(c)(3)",
  "severity": "high",  // high, medium, low
  "reason": "contradicts_regulation"
}
```

---

### Frontend Swap Rendering

```typescript
// React component handling Swap events
function renderSwapEvent(event: SwapEvent) {
  return (
    <div className="verification-correction">
      <span className="incorrect-text strikethrough">
        {event.original_text}
      </span>
      <span className="correct-text">
        {event.correction}
      </span>
      <cite className="citation-badge">
        {event.citation}
      </cite>
    </div>
  );
}
```

**CSS:**
```css
.incorrect-text {
  text-decoration: line-through;
  color: #dc2626; /* red */
  opacity: 0.7;
}

.correct-text {
  color: #16a34a; /* green */
  font-weight: 500;
}

.citation-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: #3b82f6;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}
```

---

## Red Flags (Common Hallucination Patterns)

### Flag 1: Overly Specific Numbers

❌ **Talker says:** "You must log exactly 47.3 hours of cross-country time."  
✅ **Reality:** 14 CFR 61.109 requires "50 hours" (round number)

**Pattern:** LLMs sometimes generate precise decimals for regulatory requirements that are always round numbers.

---

### Flag 2: Combining Multiple Regulations

❌ **Talker says:** "14 CFR 91.155 requires 3 SM visibility below 10,000 feet MSL."  
✅ **Reality:** 
- 91.155 covers VFR weather minimums
- The 10,000 ft threshold is in 91.117 (speed limits)

**Pattern:** Confusing requirements from different FARs.

---

### Flag 3: Outdated Information

❌ **Talker says:** "BasicMed requires a medical exam every 4 years."  
✅ **Reality:** 14 CFR 61.23 requires exam every 48 months (functionally same, but check latest FAR)

**Pattern:** Verify against CURRENT regulations, not older versions.

---

### Flag 4: Missing Exceptions

❌ **Talker says:** "All aircraft must have a transponder."  
✅ **Reality:** 14 CFR 91.215 has MANY exceptions (e.g., non-towered airports, below Mode C veil)

**Pattern:** Overgeneralizing without mentioning exceptions.

---

## Testing the Verifier

### Test Case 1: Correct Citation (Confirm)

**Talker Output:**
> "Per 14 CFR 61.56, you must complete a flight review every 24 calendar months."

**Evidence from DB2:**
> "14 CFR 61.56(a): No person may act as pilot in command unless... within the preceding 24 calendar months, that person has accomplished a flight review..."

**Expected Verifier Action:**
```json
{
  "action": "confirm",
  "citation": "14 CFR 61.56(a)"
}
```

**UI Result:** Append [Verified ✓ 14 CFR 61.56(a)]

---

### Test Case 2: Incorrect Fact (Swap)

**Talker Output:**
> "Strobes are required for day VFR operations."

**Evidence from DB2:**
> "14 CFR 91.205(b): Day VFR equipment requirements... (no mention of strobes)"
> "14 CFR 91.205(c)(3): Night VFR requires anti-collision lights."

**Expected Verifier Action:**
```json
{
  "action": "swap",
  "original": "Strobes are required for day VFR operations.",
  "correction": "Strobes are NOT required for day VFR, only night VFR per 14 CFR 91.205(c)(3).",
  "citation": "14 CFR 91.205(b) and (c)(3)"
}
```

**UI Result:** Cross out original, show correction with citation

---

### Test Case 3: Missing Safety Info (Elaborate)

**Talker Output:**
> "You can fly in Class B airspace as a student pilot."

**Evidence from DB2:**
> "14 CFR 61.95: A student pilot must have specific endorsement AND meet training requirements for Class B."

**Expected Verifier Action:**
```json
{
  "action": "elaborate",
  "addition": "⚠️ Important: You need a specific CFI endorsement (14 CFR 61.95) and training in that specific Class B before solo operations."
}
```

**UI Result:** Show Talker text, append safety warning below

---

## Performance Considerations

### Verifier Timeout

```python
# Allow max 3 seconds for verification
try:
    verification = await asyncio.wait_for(
        verify_response(talker_text, evidence),
        timeout=3.0
    )
except asyncio.TimeoutError:
    # Show as unverified rather than blocking
    yield {"type": "badge", "status": "unverified"}
```

**Rationale:** Don't make users wait forever for verification. 3 seconds is acceptable for background process.

---

### Prioritize Critical Verifications

```python
def prioritize_claims(claims: list) -> list:
    """
    Verify safety-critical claims first.
    """
    priority_order = {
        "emergency_procedure": 1,
        "weather_minimum": 2,
        "legal_requirement": 3,
        "equipment_requirement": 4,
        "general_knowledge": 5
    }
    
    return sorted(claims, key=lambda c: priority_order.get(c["catigory"], 99))
```

---

## Related Skills

- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - Lane 3 (Verifier) in the 3-lane pattern
- [dual-store-rag-patterns.md](../dual-store-rag-patterns/SKILL.md) - How to query DB2 for evidence
- [sse-streaming-patterns.md](../sse-streaming-patterns/SKILL.md) - How to send Swap events

---

## Summary

**Key Takeaways:**

1. **The Golden Rule:** Never fabricate citations
2. **Always Verify:** Regulatory citations, safety procedures, legal requirements, numerical values
3. **Skip Verification:** Casual conversation, acknowledgments, general knowledge
4. **Swap Event:** Cross out incorrect text, show correction with citation
5. **3-Second Timeout:** Don't block user experience waiting for verification

Following this protocol ensures **AviationChat maintains its core value proposition: regulatory accuracy**.
