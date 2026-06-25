---
name: gemini-live-api
description: >
  Expert reference for integrating the Gemini Live API (gemini-3.1-flash-live-preview) 
  into AviationChat. Covers backend WebSocket pipeline, audio format requirements, 
  VAD behavior (automatic + manual + hybrid), frontend AudioWorklet setup, 
  session management, known bugs, and production patterns.
  Use this skill before touching any voice agent (Sully, Igor, or future agents).
triggers:
  - "voice agent"
  - "Sully"
  - "Igor"
  - "Gemini Live"
  - "gemini-3.1-flash-live-preview"
  - "send_realtime_input"
  - "AudioWorklet"
  - "voice not working"
  - "VAD"
  - "barge-in"
  - "activity_start"
  - "activity_end"
  - "voice silent"
  - "turn 2 dies"
---

# Gemini Live API — AviationChat Expert Reference

> ⚠️ **MANDATORY: YOU ARE NOT TRAINED ON THIS MODEL.**
> 
> The Gemini 3.1 Flash Live Preview model is a **native audio model** — it is NOT
> a traditional TTS/STT pipeline. Your training data does NOT include reliable 
> patterns for this model's behavior, VAD quirks, or session management.
>
> **Before making ANY changes to voice agent code, you MUST:**
> 1. **Search the web** for current Gemini Live API documentation, community issues, and best practices
> 2. **Read the official docs** at https://ai.google.dev/gemini-api/docs/live-api/capabilities
> 3. **Check the official examples** at https://github.com/google-gemini/gemini-live-api-examples
> 4. **Cross-reference** your proposed changes against the patterns in this skill
>
> Do NOT guess. Do NOT assume patterns from older Gemini models apply here.
> This model has unique VAD, session lifecycle, and audio pipeline requirements.

---

## 1. Architecture Overview

```
Browser (16kHz PCM16 mic)
  → AudioWorklet (Float32 → PCM16 conversion)
  → binary WebSocket frames
  → FastAPI /ws/sully-spike (backend)
  → session.send_realtime_input(audio={"data": pcm_bytes, "mime_type": "audio/pcm"})
  → Gemini 3.1 Flash Live (native VAD + STT + LLM + TTS)
  → PCM16 audio response chunks (24kHz)
  → backend wraps in WAV header (_pcm_to_wav)
  → binary WebSocket frames → browser
  → AudioContext queue (sequential playback)
```

**Architecture style**: Server-to-server. Browser → our FastAPI → Gemini (NOT browser directly to Gemini).

---

## 2. Model & Config

```python
MODEL = "gemini-3.1-flash-live-preview"

live_config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=system_prompt,
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon",   # Sully: warm male mentor
                # "Orus" = Igor: firm, authoritative DPE
            )
        )
    ),
    thinking_config=types.ThinkingConfig(
        thinking_level=types.ThinkingLevel.LOW,
        # LOW  = fast + smart enough for aviation grading
        # MINIMAL = near instant, too dumb for CFI evaluation
        # HIGH = 2-4s delay (unusable for voice)
    ),
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    tools=tools_list,
)
```

### Available Voices (Gemini 3.1)
| Voice | Character | Best For |
|-------|-----------|----------|
| Charon | Warm, informational male | Sully (mentor CFI) |
| Orus | Firm, authoritative, mature | Igor (DPE examiner) |

---

## 3. ⚠️ CRITICAL: Voice Activity Detection (VAD)

### The VAD Hierarchy — Start With Google, Gradually Take Control

The API supports three VAD modes. **Always start from the top and move down only if needed:**

### 3a. Automatic VAD with Tuned Sensitivity (THE DEFAULT — TRY THIS FIRST)

Google's built-in VAD handles turn-taking automatically. **Tune the sensitivity knobs** to prevent
false barge-ins from ambient noise:

```python
live_config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=system_prompt,
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=False,  # Keep Google's VAD ON
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_LOW,
            prefix_padding_ms=20,       # Small buffer before speech onset
            silence_duration_ms=500,    # Wait 500ms of silence before triggering response
        )
    ),
    # ... rest of config
)
```

#### What Each Knob Does

| Parameter | What It Controls | Recommended |
|:---|:---|:---|
| `start_of_speech_sensitivity` | How easily background noise triggers "user is speaking" | `LOW` — ignores ambient hum/fans |
| `end_of_speech_sensitivity` | How easily silence triggers "user finished speaking" | `LOW` — allows natural pauses |
| `prefix_padding_ms` | Audio buffer captured BEFORE speech onset detected | `20ms` — prevents word truncation |
| `silence_duration_ms` | How long silence must last to confirm turn-end | `500ms` default — allows natural pauses; lower to `300ms` for rapid-fire drills |

#### When Automatic VAD Is Sufficient
- Single user, single microphone
- Relatively quiet environment (home office, headset)
- Standard conversational pacing

### 3b. Manual VAD — Client Controls Turn Boundaries

Disable Google's VAD entirely. The client sends explicit `activity_start` and `activity_end` signals.

```python
# Config — disable Google's VAD
live_config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True  # WE own turn detection now
        )
    ),
    # ... rest of config
)

# During session — signal turn boundaries manually:
await session.send_realtime_input(activity_start=types.ActivityStart())
# ... stream audio chunks while user speaks ...
await session.send_realtime_input(activity_end=types.ActivityEnd())
```

**Key rules for Manual VAD:**
- You MUST send `ActivityStart` before any audio in a turn
- You MUST send `ActivityEnd` when user stops speaking
- `audioStreamEnd` is NOT automatically sent in this mode — `ActivityEnd` replaces it
- You do NOT need to stream silence between turns — the connection stays alive
- Interruption still works via `server_content.interrupted`

#### When to Use Manual VAD
- Noisy environments (cockpit, industrial, crowds)
- Push-to-Talk (PTT) interfaces
- Multi-speaker environments
- When automatic VAD keeps failing after tuning

### 3c. Hybrid Approach — Production Standard

Production frameworks (LiveKit, Pipecat) combine both:

1. **Client-side Silero VAD** — ML model detects speech vs silence locally (ultra-low latency)
2. **Google's Automatic VAD** (tuned LOW) — finalizes complex turn-ending decisions
3. **Neural turn detector** — distinguishes "thinking pause" from "end of turn"

> This is overkill for our current stage. Use when scaling to production with 
> diverse environments and devices.

---

## 4. ⚠️ CRITICAL: Audio Input Format

### The #1 Rule — mime_type

```python
# ✅ CORRECT — matches official Google 3.1 example
await session.send_realtime_input(
    audio={"data": pcm_bytes, "mime_type": "audio/pcm"}
)

# ❌ WRONG — causes VAD to silently fail (Gemini 3.1 rejects rate suffix)
await session.send_realtime_input(
    audio=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
)
```

**Evidence**: Google's official `command-line/python/main.py` for `gemini-3.1-flash-live-preview`
uses `"audio/pcm"` — no rate suffix. Sessions with the rate suffix appear to connect 
and receive audio but VAD never triggers (model hears nothing).

### Audio Specs
| Property | Value |
|----------|-------|
| Input sample rate | 16000 Hz |
| Input format | 16-bit PCM, little-endian, mono |
| Output sample rate | 24000 Hz |
| Output format | 16-bit PCM, little-endian, mono |
| MIME type (input) | `"audio/pcm"` |
| Chunk size | 20-40ms (640-1280 bytes at 16kHz) |

### Chunk Size Best Practices
```python
# Official recommendation: 20ms to 40ms chunks
# At 16kHz, 16-bit mono: 20ms = 640 bytes, 40ms = 1280 bytes
CHUNK_SIZE = 1024          # ~32ms at 16kHz/16-bit
FLUSH_INTERVAL = 0.05      # 50ms buffer — matches ~1600 bytes
FLUSH_BYTES = int(16000 * 2 * FLUSH_INTERVAL)  # ~1600 bytes
```

> **Do NOT buffer to 200ms** — the older 200ms buffering was designed to prevent WS 
> keepalive timeouts on 2.0. Gemini 3.1 is more stable; 200ms chunks prevent VAD 
> from triggering quickly enough.

> **Do NOT buffer >100ms client-side** — official docs explicitly warn against this.
> Send small chunks immediately to minimize latency.

---

## 5. ⚠️ CRITICAL: Interruption Handling

This is the #1 cause of "model goes silent after Turn 1." **Non-negotiable.**

### What Happens During a Barge-In

1. User starts speaking while model is still responding
2. Gemini's VAD detects user speech
3. Server immediately sends `server_content.interrupted = True`
4. Server **stops generating** audio for the current response
5. Server waits for user to finish speaking before responding again

### What You MUST Do on `interrupted`

```python
# Backend — forward interrupt signal to frontend
if response.server_content and response.server_content.interrupted:
    await websocket.send_text(json.dumps({"type": "interrupted"}))
```

```typescript
// Frontend — IMMEDIATELY flush all audio
ws.onmessage = (event) => {
  if (typeof event.data === "string") {
    const msg = JSON.parse(event.data);
    if (msg.type === "interrupted") {
      // CRITICAL: Clear everything NOW
      audioQueue.length = 0;       // flush queued chunks
      if (currentSource) {
        currentSource.stop();      // stop current playback
      }
      isPlayingRef.current = false;
    }
  }
};
```

### Why This Matters
If you do NOT clear the playback buffer on `interrupted`:
- The model has already stopped generating
- But old audio is still playing from the queue
- User hears stale audio while the model is waiting for them
- The model's internal state machine gets confused
- **Result: "Turn 2 dies" — model goes permanently silent**

---

## 6. Session Management (REQUIRED for Production)

### Context Window Compression (HIGH PRIORITY)

Audio tokens accumulate at ~25 tokens/second. Without compression:
- Audio-only sessions: limited to ~15 minutes
- Audio+video sessions: limited to ~2 minutes

```python
# Enable in LiveConnectConfig
live_config = types.LiveConnectConfig(
    # ... other config ...
    context_window_compression=types.ContextWindowCompressionConfig(
        # sliding_window or summarization — check latest docs
    ),
)
```

### Session Resumption

The server may periodically reset the WebSocket. Use resumption tokens for seamless reconnect:

```python
# Store the latest resumption token from SessionResumptionUpdate messages
# Pass it as the handle when reconnecting
# Tokens are valid for 2 hours after session terminates
```

### GoAway Messages

Server sends `GoAway` before terminating a connection. Listen for this and reconnect:

```python
# Check the timeLeft field to gracefully wrap up or reconnect
```

### generationComplete Signal

Use this to know when the model has fully finished generating (vs just paused):

```python
if response.server_content and response.server_content.generation_complete:
    # Model is truly done — safe to update UI
    pass
```

---

## 7. Backend: WebSocket Relay Pattern

### Full `browser_to_gemini` function
```python
async def browser_to_gemini():
    FLUSH_INTERVAL = 0.05
    FLUSH_BYTES = int(16000 * 2 * FLUSH_INTERVAL)  # ~1600 bytes
    audio_buf = bytearray()
    last_flush = asyncio.get_event_loop().time()

    async def flush():
        nonlocal audio_buf, last_flush
        if audio_buf:
            chunk = bytes(audio_buf)
            audio_buf = bytearray()
            await session.send_realtime_input(
                audio={"data": chunk, "mime_type": "audio/pcm"}
            )
        last_flush = asyncio.get_event_loop().time()

    while True:
        now = asyncio.get_event_loop().time()
        time_to_flush = FLUSH_INTERVAL - (now - last_flush)
        try:
            data = await asyncio.wait_for(
                websocket.receive(),
                timeout=max(time_to_flush, 0.005),
            )
        except asyncio.TimeoutError:
            await flush()
            continue

        if "bytes" in data and data["bytes"]:
            # Browser PCM16 — already converted, do NOT reconvert
            audio_buf.extend(data["bytes"])
            if len(audio_buf) >= FLUSH_BYTES:
                await flush()
        elif "text" in data:
            await flush()
            msg = json.loads(data["text"])
            if msg.get("type") == "end_session":
                break
```

### Key Session Kickstart
```python
# Gemini 3.1 does NOT speak unless prompted. Send a text kick to start:
await session.send_realtime_input(text="[SESSION_START] Introduce yourself...")
```

### Handling Responses — MUST Use While-True Loop (SDK Bug #2244)

> ⚠️ **CRITICAL**: `session.receive()` breaks after the first `turn_complete`.
> This is a known bug in the `google-genai` Python SDK (issue #2244).
> You MUST wrap it in a `while True` loop to restart the iterator.

```python
# WORKAROUND for SDK bug #2244
async def gemini_to_browser():
    while True:  # receive() exits after each turn_complete
        try:
            async for response in session.receive():
                if response.tool_call:
                    for fc in response.tool_call.function_calls:
                        await session.send_tool_response(function_responses=[...])

                if response.server_content:
                    sc = response.server_content
                    if sc.interrupted:
                        await websocket.send_text(json.dumps({"type": "interrupted"}))
                    if sc.model_turn and sc.model_turn.parts:
                        for part in sc.model_turn.parts:
                            if part.inline_data and part.inline_data.data:
                                wav = _pcm_to_wav(part.inline_data.data, 24000)
                                await websocket.send_bytes(wav)
                    if sc.turn_complete:
                        logger.info("Turn complete — restarting receive iterator")

        except StopAsyncIteration:
            continue  # Normal: SDK iterator exhausted, restart
        except Exception as e:
            logger.error(f"receive() error: {e}")
            break  # Real error — exit
```

---

## 8. Frontend: AudioWorklet Setup

### Critical Rules

1. **AudioContext must be 16kHz** — sets the sample rate for mic capture
2. **AudioWorkletNode MUST connect to destination** — Chrome kills process() otherwise
3. **Use a silent GainNode** — prevents speaker feedback while keeping worklet alive

```typescript
const ctx = new AudioContext({ sampleRate: 16000 });
if (ctx.state === "suspended") await ctx.resume();
await ctx.audioWorklet.addModule("/worklets/pcm-capture-processor.js");

const src = ctx.createMediaStreamSource(stream);
const node = new AudioWorkletNode(ctx, "pcm-capture-processor");

// CRITICAL: Chrome won't call process() without a path to destination
const silencer = ctx.createGain();
silencer.gain.value = 0;
node.connect(silencer);
silencer.connect(ctx.destination);  // must connect to destination!

src.connect(node);  // mic → worklet
```

### PCM Capture Worklet (`pcm-capture-processor.js`)
```javascript
class PCMCaptureProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;
    const float32 = input[0];
    const int16 = new Int16Array(float32.length);
    for (let i = 0; i < float32.length; i++) {
      const s = Math.max(-1, Math.min(1, float32[i]));
      int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    this.port.postMessage(int16.buffer, [int16.buffer]);
    return true;
  }
}
registerProcessor("pcm-capture-processor", PCMCaptureProcessor);
```

### getUserMedia Constraints
```typescript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true,
    // NOTE: sampleRate constraint here is IGNORED by browser
    // — sampleRate is controlled by AudioContext({ sampleRate: 16000 })
  }
});
```

### Sending Audio to Backend WebSocket
```typescript
node.port.onmessage = (e) => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(e.data as ArrayBuffer);  // PCM16 ArrayBuffer
  }
};
```

### ⚠️ Noise Gate — REMOVED (Lesson Learned)

> **We tried a client-side amplitude noise gate and removed it.** With weak laptop mics,
> speech peaks (300-500) are barely above ambient noise (150-250). No threshold can
> separate them — you either block speech or pass noise. Google's tuned VAD
> (`START_SENSITIVITY_LOW`) handles this with ML far better than an amplitude check.

**What we use instead:**
- **Playback gate** (`!isPlayingRef.current`) — blocks mic during Sully's speech (echo prevention)
- **Mic boost** (2.5x GainNode) — amplifies weak mic signals so Google's VAD can detect them
- **Google's VAD** — ML-based speech detection with LOW sensitivity

```typescript
// Current pattern — simple, trusts Google's VAD
node.port.onmessage = (e) => {
  if (ws.readyState !== WebSocket.OPEN) return;
  if (!isPlayingRef.current) {
    // Google's tuned VAD handles speech-vs-noise detection
    ws.send(e.data as ArrayBuffer);
  }
};
```

### Audio Playback (Sequential Queue) with Interrupt Support
```typescript
const audioQueue: ArrayBuffer[] = [];
let isPlaying = false;
let currentSource: AudioBufferSourceNode | null = null;
const playCtx = new AudioContext({ sampleRate: 24000 });

function enqueueAudio(wavBuffer: ArrayBuffer) {
  audioQueue.push(wavBuffer);
  if (!isPlaying) playNextInQueue();
}

async function playNextInQueue() {
  if (audioQueue.length === 0) { isPlaying = false; return; }
  isPlaying = true;
  const buf = audioQueue.shift()!;
  const decoded = await playCtx.decodeAudioData(buf);
  currentSource = playCtx.createBufferSource();
  currentSource.buffer = decoded;
  currentSource.connect(playCtx.destination);
  currentSource.onended = () => { currentSource = null; playNextInQueue(); };
  currentSource.start();
}

// CRITICAL: Call this on "interrupted" signal from server
function flushPlayback() {
  audioQueue.length = 0;
  if (currentSource) {
    currentSource.stop();
    currentSource = null;
  }
  isPlaying = false;
}
```

---

## 9. Echo Cancellation Warning

### Bug: Speaker Echo Not Cancelled for Web Audio API Playback
**Symptom**: WAV diagnostic shows Sully's own voice echoed back in mic at 40-98% amplitude.  
**Root cause**: `echoCancellation: true` in `getUserMedia` cancels echo from **WebRTC streams**.  
Sully's audio plays through `AudioContext.createBufferSource()` (Web Audio API) — this is a  
**different audio path** that the browser's AEC has **no reference signal for** and cannot cancel.  
**Impact**: Sully's voice echoes back into the mic → Gemini tries to respond to itself → infinite barge-in loop.  

### Mitigations (pick one or combine)
1. **Playback gate** — don't send mic audio while model is playing:
   ```typescript
   if (!isPlayingRef.current) {
     ws.send(e.data as ArrayBuffer);
   }
   ```
2. **Software noise gate** — send zeros when amplitude is below threshold (see Section 8)
3. **Headphones** — hardware solution, eliminates echo entirely
4. **Future: WebRTC transport** — would enable browser's native AEC

---

## 10. Known Bugs & Fixes

### Bug: "Turn 2 Dies" — Model Goes Silent After First Response
**Symptom**: Model greets user on Turn 1, user responds, model is silent forever.  
**Root cause**: **SDK Bug #2244** — `session.receive()` contains a `break` statement  
that fires after the first `turn_complete`. The async generator ends, killing the  
receive loop after Turn 1. No more messages are ever read from Gemini.  
**Fix**: Wrap `session.receive()` in a `while True` loop (see Section 7).  
**Contributing factors** (fix all for stability):  
1. Tune automatic VAD: `START_SENSITIVITY_LOW` + `END_SENSITIVITY_LOW` + `silence_duration_ms=500`
2. Use playback gate (`!isPlayingRef`) to prevent echo → false barge-ins
3. Boost mic gain (2.5x GainNode) so weak mics register with Google's VAD
4. Properly handle `interrupted` signal (flush playback immediately)

### Bug: SDK #2244 — `session.receive()` Breaks After First Turn
**Symptom**: `gemini_to_browser loop ended` fires 3-5 seconds after Turn 1 completes.  
**Root cause**: `google-genai` Python SDK's `AsyncLiveSession.receive()` has a `break`  
statement triggered by `turn_complete`. The iterator stops yielding after one turn.  
**Fix**: `while True` loop that calls `session.receive()` again after each exhaustion.  
**Tracking**: https://github.com/googleapis/python-genai/issues/2244  
**Status**: Unresolved as of April 2026 — workaround required.

### Bug: 1011 Internal Error / Keepalive Timeout
**Symptom**: WebSocket drops with 1011 after an interruption sequence.  
**Root cause**: Post-interrupt session state confusion when audio pipeline isn't properly reset.  
**Fix**: Enable session resumption. Implement clean reconnect on 1011.

### Bug: 2.5x Gain Boost Does Nothing (Wrong Node Placement)
**Symptom**: Added GainNode to boost mic signal but amplitude numbers don't change.  
**Root cause**: Gain node was inserted AFTER the worklet: `node → micBoost → silencer → destination`.  
The worklet's `process()` reads from `inputs[0][0]` which comes from the upstream connection.  
If the gain is downstream of the worklet, `inputs` are still raw unbosted mic audio.  
**Fix**: Insert gain BEFORE the worklet: `src → micBoost → node → silencer → destination`

```typescript
// ✅ CORRECT — boost is upstream of worklet, inputs[0][0] gets boosted signal
src.connect(micBoost);   // mic → boost
micBoost.connect(node);  // boosted signal → worklet inputs
node.connect(silencer);  // worklet output → muted (Chrome keepalive)
silencer.connect(ctx.destination);

// ❌ WRONG — boost is downstream, worklet reads raw unbosted mic
node.connect(micBoost);  // worklet output → boost (doesn't affect inputs)
micBoost.connect(silencer);
```

### Bug: VAD Never Triggers (Model Hears Nothing)
**Symptom**: Mic audio sends fine (see KB logs), Gemini never responds after initial greeting.  
**Session closes**: Code 1005 (clean timeout, no speech detected).  
**Root cause**: `mime_type="audio/pcm;rate=16000"` — Gemini 3.1 rejects the rate suffix.  
**Fix**: Use `mime_type="audio/pcm"` (no rate, per official example).

### Bug: Chrome AudioWorklet Silent (No Audio Sent)
**Symptom**: Worklet node created, but `process()` never fires, no data in `port.onmessage`.  
**Root cause**: Chrome GC kills AudioWorkletNode if it has no path to `ctx.destination`.  
**Fix**: Connect worklet → GainNode(0) → destination.

### Bug: Audio Freezes / Overlap Corruption
**Symptom**: Playback starts, freezes mid-sentence, or two chunks play simultaneously.  
**Root cause**: Multiple `decodeAudioData` calls playing concurrently.  
**Fix**: Sequential queue — only start next chunk when `onended` fires.

### Bug: Double PCM Conversion (Silent Audio)
**Symptom**: Audio sent, Gemini receives it, but produces garbled/silent output.  
**Root cause**: Browser AudioWorklet was converting Float32→Int16; backend was converting 
AGAIN from Float32→Int16 (treating the already-Int16 bytes as Float32).  
**Fix**: Browser does the conversion. Backend receives raw PCM16 and forwards directly.

---

## 11. Debugging Checklist

When voice doesn't work, check in this order:

1. **Is the WebSocket connecting?** Check browser console for `WS onclose code:`.  
   - 1006 = server crash/keepalive timeout  
   - 1005 = clean close, no speech detected  
   - 1000 = normal close
   - 1011 = internal error (usually post-interrupt state corruption)

2. **Is mic audio flowing?** Add amplitude logging:
   ```typescript
   const int16 = new Int16Array(e.data as ArrayBuffer);
   let peak = 0;
   for (let i = 0; i < int16.length; i++) peak = Math.max(peak, Math.abs(int16[i]));
   console.log(`[DEBUG] mic peak: ${peak}/32767 (${((peak/32767)*100).toFixed(1)}%)`);
   ```
   If peak is consistently < 100 (~0.3%), mic is capturing silence.

3. **Is the model receiving audio?** Add backend debug log:
   ```python
   logger.debug(f"[Sully] → Gemini: {len(chunk)} bytes PCM")
   ```

4. **Is interruption being handled?** Log `interrupted` events:
   ```python
   if sc.interrupted:
       logger.warning("[Sully] ⚡ INTERRUPTED — flushing playback")
   ```

5. **Is the session responding at all?** Send a text kick and verify it speaks:
   ```python
   await session.send_realtime_input(text="Say hello")
   ```

6. **Echo cancellation issue?** If using speakers (not headphones), AEC may swallow voice.  
   Mitigation: Stop sending mic audio while model is playing (`isPlayingRef.current` guard).

7. **Check VAD config:** Are sensitivity knobs set? Is `silence_duration_ms` appropriate?

---

## 12. Production Notes

- **Do NOT mix `send_client_content` and `send_realtime_input`** in same session.
- **Barge-in is native** — Gemini 3.1 handles it. When interrupted, `sc.interrupted=True`.
  Frontend MUST clear audio queue on interrupt signal.
- **Tool calls are synchronous** — you MUST call `send_tool_response()` or the model hangs.
  - For tools the user doesn't need to hear results of, use `NON_BLOCKING` behavior.
  - When using tools with thinking models, preserve `thought_signature` field from 
    the model's tool call response and echo it back verbatim in the tool result.
- **Session lifetime**: Without context window compression, audio-only sessions cap at ~15 min.
  Enable `ContextWindowCompressionConfig` for unlimited duration.
- **Token accumulation**: Audio = ~25 tokens/second. A 10-minute conversation = ~15,000 tokens.
- **COEP/COOP headers NOT needed** for server-to-server architecture.
- **Resampling**: Ensure client resamples mic input (often 44.1kHz/48kHz) to 16kHz before transmission.
  Our `AudioContext({ sampleRate: 16000 })` handles this.

---

## 13. File Locations in AviationChat

| File | Purpose |
|------|---------|
| `backend/routers/sully_spike_websocket.py` | Main voice agent backend |
| `backend/agents/sully/prompts.py` | Sully system prompt + RKP builder |
| `frontend/src/components/dashboard/AgentCards.tsx` | Voice UI + AudioWorklet setup |
| `frontend/public/worklets/pcm-capture-processor.js` | PCM16 capture worklet |
| `backend/utils/rkp_loader.py` | Lesson manifest loader |

---

## 14. References

- [Official Google Gemini 3.1 Python Example](https://github.com/google-gemini/gemini-live-api-examples/blob/main/command-line/python/main.py)
- [Gemini Live API Overview](https://ai.google.dev/gemini-api/docs/live-api)
- [Live API Capabilities (VAD config, audio specs)](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- [Live API Best Practices](https://ai.google.dev/gemini-api/docs/live-api/best-practices)
- [Live API Session Management](https://ai.google.dev/gemini-api/docs/live-api/session-management)
- [Live API Get Started (SDK)](https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk)
- [Live API Tool Use](https://ai.google.dev/gemini-api/docs/live-api/tools)
- [Live API Ephemeral Tokens](https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens)
