---
description: AviationChat deployment on Cloud Run with FastAPI + ADK, secrets management, and SSE streaming
---

# AviationChat Cloud Run Deployment

**Domain:** AviationChat-AGY  
**Use When:** Deploying backend, configuring production environment, or troubleshooting deployment issues

---

## Core Architecture

AviationChat backend runs as a **Cloud Run service** (NOT Cloud Functions):

- **Framework:** FastAPI (Python 3.11+)
- **Agent Runtime:** Google ADK
- **Streaming:** SSE via StreamingResponse
- **Authentication:** Service account (Firestore, Vertex AI)

---

## Technology Stack

### Python + FastAPI

**Why FastAPI?**
- ✅ Async/await native (required for ADK)
- ✅ Built-in SSE support (StreamingResponse)
- ✅ Fast startup (critical for cold starts)
- ✅ Type hints (Pydantic validation)

### Google ADK

**Why ADK?**
- ✅ Multi-agent orchestration
- ✅ Tool calling framework
- ✅ Gemini 3.0 integration
- ✅ Memory management

---

## Dockerfile

### Production Dockerfile

```dockerfile
# AviationChat Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY secrets/ ./secrets/

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Key Points:**
- Python 3.11 (ADK requirement)
- System dependencies for ADK (gcc, g++)
- Unbuffered output for Cloud Logging
- Uvicorn ASGI server

---

## FastAPI Application

### Main App Structure

```python
# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI(title="AviationChat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aviationchat.vercel.app"],  # Production frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (REQUIRED for Cloud Run)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# SSE Streaming endpoint
@app.post("/api/chat/specialist/stream")
async def specialist_stream(request: ChatRequest):
    async def event_generator():
        # Lane 1: Stream Talker
        async for chunk in talker_agent.stream():
            yield f"data: {json.dumps({'type': 'delta', 'content': chunk})}\n\n"
        
        # Lane 3: Verify
        verification = await verify_response(...)
        yield f"data: {json.dumps(verification)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
```

---

## Environment Variables & Secrets

### Required Environment Variables

```bash
# .env (for local development)
GCP_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-key
GOOGLE_APPLICATION_CREDENTIALS=secrets/service-account.json
PORT=8080
```

### Cloud Run Deployment (Secrets)

```bash
# Deploy with secrets
gcloud run deploy aviationchat-backend \
  --image gcr.io/your-project/aviationchat:latest \
  --region us-central1 \
  --set-env-vars "GCP_PROJECT_ID=your-project" \
  --set-secrets "GEMINI_API_KEY=gemini-key:latest" \
  --set-secrets "SERVICE_ACCOUNT_JSON=service-account-json:latest" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10
```

**Secrets Management:**
- Store API keys in **Secret Manager** (NOT environment variables)
- Mount service account JSON as secret
- Never commit `.env` or `secrets/` to Git

---

## Deployment Configuration

### Cloud Run Settings

```yaml
# service.yaml (Cloud Run configuration)
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: aviationchat-backend
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"  # Always allocate CPU (SSE)
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300  # 5 min for long SSE streams
      containers:
      - image: gcr.io/your-project/aviationchat:latest
        resources:
          limits:
            memory: 1Gi
            cpu: "2"
        env:
        - name: GCP_PROJECT_ID
          value: your-project-id
        - name: PORT
          value: "8080"
```

**Key Settings:**
- **Min instances: 1** - Avoid cold starts (users expect instant response)
- **CPU always allocated** - Required for SSE streaming
- **Timeout: 300s** - Allow long verification workflows
- **Concurrency: 80** - Balance throughput vs. latency

---

## SSE Streaming Configuration

### Why "CPU Always Allocated"?

**Problem:** Cloud Run throttles CPU when NOT handling requests.

**Impact on SSE:**
```python
# With CPU throttling (default):
async for chunk in talker_stream:
    yield chunk  # Streaming slows down between requests

# With CPU always allocated:
async for chunk in talker_stream:
    yield chunk  # Consistent streaming speed
```

**Solution:**
```bash
gcloud run deploy aviationchat-backend \
  --cpu-throttling=false  # Always allocate CPU
```

**Cost Trade-off:**
- ❌ Higher cost (CPU always billable)
- ✅ Better user experience (consistent streaming)
- ✅ Simpler debugging (no throttling issues)

---

## Cold Start Optimization

### Pattern 1: Min Instances

```bash
gcloud run deploy aviationchat-backend \
  --min-instances 1  # Always keep one instance warm
```

**Why?** Users expect < 500ms first token. Cold start = 2-3s.

---

### Pattern 2: Startup CPU Boost

```bash
gcloud run deploy aviationchat-backend \
  --startup-cpu-boost  # Extra CPU during startup
```

**Reduces cold start from 3s → 1.5s**

---

### Pattern 3: Lazy Load Heavy Dependencies

```python
# backend/app.py

# ✅ GOOD: Lazy load ADK agents
_specialist_agent = None

def get_specialist_agent():
    global _specialist_agent
    if _specialist_agent is None:
        from backend.agents.orchestrators.specialist.agent import specialist_agent
        _specialist_agent = specialist_agent
    return _specialist_agent

# Only import when needed
@app.post("/api/chat/specialist")
async def specialist_chat(request: ChatRequest):
    agent = get_specialist_agent()  # Lazy load
    response = await agent.generate(request.message)
    return response
```

**Reduces cold start from 2s → 1s** (defers ADK initialization)

---

## Deployment Workflow

### Local Build & Test

```bash
# 1. Build Docker image locally
docker build -t aviationchat-backend .

# 2. Run locally
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project \
  -e GEMINI_API_KEY=your-key \
  -v $(pwd)/secrets:/app/secrets \
  aviationchat-backend

# 3. Test endpoint
curl http://localhost:8080/health
```

---

### Push to Google Container Registry

```bash
# 1. Tag image
docker tag aviationchat-backend gcr.io/your-project/aviationchat:latest

# 2. Push to GCR
docker push gcr.io/your-project/aviationchat:latest
```

---

### Deploy to Cloud Run

```bash
# Deploy from GCR
gcloud run deploy aviationchat-backend \
  --image gcr.io/your-project/aviationchat:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --cpu-throttling=false \
  --startup-cpu-boost \
  --timeout 300 \
  --set-env-vars "GCP_PROJECT_ID=your-project" \
  --set-secrets "GEMINI_API_KEY=gemini-key:latest"
```

---

## Monitoring & Logging

### Cloud Logging

```python
import logging
import sys

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='{"severity": "%(levelname)s", "message": "%(message)s"}',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# In your code
logger.info("User query received", extra={"user_id": user_id})
logger.error("Firestore timeout", extra={"error": str(e)})
```

**Cloud Logging parses JSON automatically.**

---

### Error Tracking (Sentry)

```python
# backend/app.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    integrations=[FastApiIntegration()]
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    sentry_sdk.capture_exception(exc)
    return {"error": "Internal server error"}
```

---

## Anti-Patterns

### ❌ Blocking I/O in Async Endpoints

```python
# BAD: Sync Firestore call blocks event loop
@app.post("/api/profile")
async def get_profile(user_id: str):
    profile = db.collection("users").document(user_id).get()  # Blocks!
    return profile.to_dict()
```

**Why Bad:** Firestore sync call blocks other requests.

### ✅ Correct: Use Async

```python
# GOOD: Async tool call
@app.post("/api/profile")
async def get_profile(user_id: str):
    profile = await get_student_profile_async(user_id)  # Non-blocking
    return profile
```

---

### ❌ No Health Check Endpoint

```python
# BAD: No /health endpoint
# Cloud Run can't verify service is ready
```

**Why Bad:** Cloud Run won't route traffic until health check passes.

### ✅ Correct: Add Health Check

```python
# GOOD: Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### ❌ Storing State in Memory

```python
# BAD: In-memory cache persists across requests
conversation_cache = {}  # Lost on instance shutdown!

@app.post("/api/chat")
async def chat(message: str):
    if user_id in conversation_cache:
        history = conversation_cache[user_id]
```

**Why Bad:** Cloud Run instances can be replaced anytime.

### ✅ Correct: Use Redis or Firestore

```python
# GOOD: External cache
@app.post("/api/chat")
async def chat(message: str):
    history = await redis.get(f"history:{user_id}")  # Persistent
```

---

## Related Skills

- [sse-streaming-patterns.md](../sse-streaming-patterns/SKILL.md) - FastAPI SSE implementation
- [backend-dev-guidelines.md](../backend-dev-guidelines/SKILL.md) - Node.js patterns (if migrating)

---

## Summary

**Key Principles:**
1. **FastAPI + ADK** - Async framework for multi-agent orchestration
2. **Min instances: 1** - Avoid cold starts
3. **CPU always allocated** - Required for SSE streaming
4. **Secrets in Secret Manager** - Never in environment variables
5. **Lazy load heavy deps** - Reduce cold start time

This ensures **fast startup**, **consistent streaming**, and **secure deployment**.
