---
description: Real-time streaming and verification events for AviationChat
---

# SSE Streaming Patterns

**Skill Type:** Frontend-Backend Integration  
**Domain:** AviationChat-AGY  
**Use When:** Implementing streaming responses, Verifier corrections, or debugging UI updates

---

## Core Concept: Server-Sent Events (SSE)

**What is SSE?**
- One-way communication from server → client
- Long-lived HTTP connection
- Server pushes updates as they happen
- Browser automatically reconnects if disconnected

**Why SSE for AviationChat?**
- **Talker streams immediately** (Lane 1)
- **Verifier sends corrections later** (Lane 3)
- **Single connection** handles both streaming + verification

---

## The Three Event Types

### Event 1: `delta` (Streaming Text)

**Purpose:** Stream Talker response token-by-token

**Format:**
```json
{
  "type": "delta",
  "content": "VFR weather minimums ",
  "timestamp": "2026-01-28T14:30:00.123Z"
}
```

**Frontend Behavior:**
- Append `content` to current message
- Show typing indicator while streaming
- Update UI immediately (no batching)

---

### Event 2: `swap` (Correction)

**Purpose:** Replace incorrect text with verified correction

**Format:**
```json
{
  "type": "swap",
  "original": "Strobes are required for day VFR operations.",
  "correction": "Strobes are NOT required for day VFR, only night VFR per 14 CFR 91.205(c)(3).",
  "citation": "14 CFR 91.205(b) and (c)(3)",
  "severity": "high",
  "timestamp": "2026-01-28T14:30:05.456Z"
}
```

**Frontend Behavior:**
- Find `original` text in displayed message
- Cross out with strikethrough
- Show `correction` in green below
- Add citation badge

---

### Event 3: `badge` (Verification Status)

**Purpose:** Show verification result without changing text

**Format:**
```json
{
  "type": "badge",
  "status": "verified",
  "citation": "14 CFR 61.56(a)",
  "timestamp": "2026-01-28T14:30:04.789Z"
}
```

**Possible Statuses:**
- `verified` - Matches regulation (green checkmark)
- `unverified` - No evidence found (yellow warning)
- `checking` - Verification in progress (spinner)

**Frontend Behavior:**
- Append badge icon to message
- Show citation on hover
- No text modification

---

## Backend Implementation (FastAPI)

### SSE Endpoint

```python
# backend/app.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json

app = FastAPI()

@app.post("/api/chat/specialist/stream")
async def specialist_chat_stream(request: ChatRequest):
    """
    SSE endpoint for streaming Specialist responses.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Lane 1: Start Talker streaming immediately
            talker_stream = talker_agent.stream_response(request.message)
            full_response = ""
            
            # Stream delta events
            async for chunk in talker_stream:
                full_response += chunk
                event_data = {
                    "type": "delta",
                    "content": chunk,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            
            # Lane 2: Investigation swarm (runs in parallel with Lane 1)
            evidence = await dispatch_investigation_swarm(request.message)
            
            # Lane 3: Verifier
            verification = await verify_response(full_response, evidence)
            
            # Send verification event
            if verification["action"] == "swap":
                swap_event = {
                    "type": "swap",
                    "original": verification["original"],
                    "correction": verification["correction"],
                    "citation": verification["citation"],
                    "severity": verification["severity"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                yield f"data: {json.dumps(swap_event)}\n\n"
            
            elif verification["action"] == "confirm":
                badge_event = {
                    "type": "badge",
                    "status": "verified",
                    "citation": verification["citation"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                yield f"data: {json.dumps(badge_event)}\n\n"
            
            else:  # unverified
                badge_event = {
                    "type": "badge",
                    "status": "unverified",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                yield f"data: {json.dumps(badge_event)}\n\n"
            
        except Exception as e:
            error_event = {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

---

### Event Formatting

```python
def format_sse_event(event_type: str, data: dict) -> str:
    """
    Format data as SSE event.
    
    SSE format:
    data: {json}\n\n
    """
    event_json = json.dumps({
        "type": event_type,
        **data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    return f"data: {event_json}\n\n"
```

---

## Frontend Implementation (React + TypeScript)

### EventSource Connection

```typescript
// frontend/src/hooks/useSSEStream.ts
import { useEffect, useState } from 'react';

interface SSEEvent {
  type: 'delta' | 'swap' | 'badge' | 'error';
  content?: string;
  original?: string;
  correction?: string;
  citation?: string;
  status?: string;
  message?: string;
  timestamp: string;
}

export function useSSEStream(url: string, enabled: boolean) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SSEEvent;
        setEvents((prev) => [...prev, data]);
      } catch (err) {
        console.error('Failed to parse SSE event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      setIsConnected(false);
      setError('Connection lost. Reconnecting...');
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [url, enabled]);

  return { events, isConnected, error };
}
```

---

### Message Component with Swap/Badge Rendering

```typescript
// frontend/src/components/StreamedMessage.tsx
import React, { useEffect, useState } from 'react';
import { SSEEvent } from '@/hooks/useSSEStream';

interface Props {
  events: SSEEvent[];
}

export function StreamedMessage({ events }: Props) {
  const [fullText, setFullText] = useState('');
  const [corrections, setCorrections] = useState<SSEEvent[]>([]);
  const [badge, setBadge] = useState<SSEEvent | null>(null);

  useEffect(() => {
    let text = '';
    const swaps: SSEEvent[] = [];
    
    for (const event of events) {
      if (event.type === 'delta') {
        text += event.content || '';
      } else if (event.type === 'swap') {
        swaps.push(event);
      } else if (event.type === 'badge') {
        setBadge(event);
      }
    }
    
    setFullText(text);
    setCorrections(swaps);
  }, [events]);

  return (
    <div className="message-container">
      {/* Original streaming text */}
      <div className="message-text">
        {renderWithSwaps(fullText, corrections)}
      </div>
      
      {/* Verification badge */}
      {badge && <VerificationBadge badge={badge} />}
    </div>
  );
}

function renderWithSwaps(text: string, swaps: SSEEvent[]) {
  if (swaps.length === 0) return text;
  
  // Find and replace each swap
  let rendered = text;
  for (const swap of swaps) {
    if (!swap.original || !swap.correction) continue;
    
    const parts = rendered.split(swap.original);
    rendered = parts.join(`
      <span class="swap-container">
        <span class="incorrect-text">${swap.original}</span>
        <span class="correct-text">${swap.correction}</span>
        <cite class="citation">${swap.citation}</cite>
      </span>
    `);
  }
  
  return <div dangerouslySetInnerHTML={{ __html: rendered }} />;
}

function VerificationBadge({ badge }: { badge: SSEEvent }) {
  if (badge.status === 'verified') {
    return (
      <div className="badge verified">
        ✓ Verified
        {badge.citation && <span className="citation">{badge.citation}</span>}
      </div>
    );
  } else if (badge.status === 'unverified') {
    return (
      <div className="badge unverified">
        ⚠ Unverified
      </div>
    );
  }
  return null;
}
```

---

### CSS Styling

```css
/* Swap event styling */
.swap-container {
  display: block;
  margin: 8px 0;
  padding: 8px;
  background: #fef3c7; /* yellow background */
  border-left: 4px solid #f59e0b;
  border-radius: 4px;
}

.incorrect-text {
  display: block;
  text-decoration: line-through;
  color: #dc2626;
  opacity: 0.7;
  margin-bottom: 4px;
}

.correct-text {
  display: block;
  color: #16a34a;
  font-weight: 500;
}

.citation {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: #3b82f6;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-style: normal;
}

/* Badge styling */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.badge.verified {
  background: #d1fae5;
  color: #065f46;
}

.badge.unverified {
  background: #fef3c7;
  color: #92400e;
}

.badge.checking {
  background: #e0e7ff;
  color: #3730a3;
}
```

---

## Timing Expectations

| Event Type | When Sent | Expected Latency |
|------------|-----------|------------------|
| `delta` | Immediately (Lane 1) | 50-500ms (first token) |
| `delta` (streaming) | Continuous | 20-50ms per token |
| `badge` | After verification (Lane 3) | 3-5s from first token |
| `swap` | If error found (Lane 3) | 3-5s from first token |

**User Experience:**
- User sees text streaming < 500ms (feels instant)
- User sees verification badge ~4s later (acceptable delay)
- User sees swap event if needed (rare, but critical)

---

## Error Handling

### Connection Lost

```typescript
// frontend/src/hooks/useSSEStream.ts
eventSource.onerror = (err) => {
  console.error('SSE error:', err);
  
  // Attempt reconnection after 2 seconds
  setTimeout(() => {
    if (eventSource.readyState === EventSource.CLOSED) {
      window.location.reload();  // Hard reload
    }
  }, 2000);
};
```

---

### Malformed Event

```typescript
eventSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    setEvents((prev) => [...prev, data]);
  } catch (err) {
    console.error('Failed to parse event:', event.data);
    // Don't crash, just skip this event
  }
};
```

---

### Backend Timeout

```python
# backend/app.py
async def event_generator():
    try:
        # Set max timeout for entire stream
        async with asyncio.timeout(30):  # 30 seconds max
            async for chunk in talker_stream:
                yield format_sse_event("delta", {"content": chunk})
    except asyncio.TimeoutError:
        yield format_sse_event("error", {"message": "Response timeout"})
```

---

## Testing

### Test Case 1: Delta Streaming

```python
async def test_delta_streaming():
    # Simulate streaming
    async def mock_stream():
        for word in ["Hello", " ", "world"]:
            yield word
    
    events = []
    async for chunk in mock_stream():
        event = {"type": "delta", "content": chunk}
        events.append(event)
    
    # Verify
    assert len(events) == 3
    assert events[0]["content"] == "Hello"
    assert events[2]["content"] == "world"
```

---

### Test Case 2: Swap Event

```python
async def test_swap_event():
    talker_output = "Strobes are required for day VFR."
    evidence = {
        "regulatory": "14 CFR 91.205(b): No strobe requirement for day VFR"
    }
    
    verification = await verify_response(talker_output, evidence)
    
    assert verification["action"] == "swap"
    assert "NOT required" in verification["correction"]
    assert "14 CFR 91.205" in verification["citation"]
```

---

### Test Case 3: Frontend Rendering

```typescript
// frontend/tests/StreamedMessage.test.tsx
import { render } from '@testing-library/react';
import { StreamedMessage } from '@/components/StreamedMessage';

test('renders swap correction', () => {
  const events = [
    { type: 'delta', content: 'Strobes required for day VFR' },
    { 
      type: 'swap',
      original: 'Strobes required for day VFR',
      correction: 'Strobes NOT required for day VFR',
      citation: '14 CFR 91.205(b)'
    }
  ];
  
  const { container } = render(<StreamedMessage events={events} />);
  
  expect(container.querySelector('.incorrect-text')).toHaveTextContent('Strobes required');
  expect(container.querySelector('.correct-text')).toHaveTextContent('NOT required');
  expect(container.querySelector('.citation')).toHaveTextContent('14 CFR 91.205(b)');
});
```

---

## Advanced Patterns

### Pattern 1: Chunked Deltas (Batching)

```python
# Backend: Batch small tokens for efficiency
buffer = ""
buffer_size = 10  # Send every 10 characters

async for token in talker_stream:
    buffer += token
    
    if len(buffer) >= buffer_size:
        yield format_sse_event("delta", {"content": buffer})
        buffer = ""

# Flush remaining buffer
if buffer:
    yield format_sse_event("delta", {"content": buffer})
```

**Trade-off:** Slightly less real-time, but reduces network overhead.

---

### Pattern 2: Progressive Badge Updates

```python
# Send "checking" badge immediately
yield format_sse_event("badge", {"status": "checking"})

# Run verification
verification = await verify_response(talker_output, evidence)

# Update to final status
if verification["action"] == "confirm":
    yield format_sse_event("badge", {
        "status": "verified",
        "citation": verification["citation"]
    })
```

**UX Benefit:** User sees immediate feedback ("checking..."), then final result.

---

### Pattern 3: Multiple Swaps

```python
# If multiple errors found
for error in verification["errors"]:
    yield format_sse_event("swap", {
        "original": error["incorrect_text"],
        "correction": error["correct_text"],
        "citation": error["citation"],
        "severity": error["severity"]
    })
```

**Frontend:** Apply swaps in order received.

---

## Performance Optimization

### Backend: Use Async Generators

```python
# ✅ GOOD: Async generator maintains connection
async def event_generator():
    async for chunk in stream:
        yield format_sse_event("delta", {"content": chunk})
```

```python
# ❌ BAD: Sync loop blocks
def event_generator():
    for chunk in stream:  # Blocks event loop
        yield format_sse_event("delta", {"content": chunk})
```

---

### Frontend: Debounce State Updates

```typescript
// Avoid re-rendering on every single delta
const [fullText, setFullText] = useState('');

useEffect(() => {
  const text = events
    .filter(e => e.type === 'delta')
    .map(e => e.content)
    .join('');
  
  setFullText(text);
}, [events]);  // React batches these updates
```

---

## Related Skills

- [multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md) - 3-lane pattern that generates these events
- [regulatory-verification-protocol.md](../regulatory-verification-protocol/SKILL.md) - When to send swap events

---

## Summary

**Key Takeaways:**

1. **Three Event Types:** `delta` (streaming), `swap` (correction), `badge` (status)
2. **FastAPI StreamingResponse:** Backend sends SSE events
3. **EventSource:** Frontend listens for events
4. **Swap Rendering:** Strikethrough original, show correction
5. **Timing:** Delta < 500ms, Badge/Swap ~4s

**Golden Rule:** Always send `delta` events first (Lane 1), verification events later (Lane 3).
