# Deployment Guide - DSPy RAG Pipeline

## Prerequisites

- Docker and Docker Compose installed
- Retrieval API running on `http://localhost:8000` (with `/retrieve` endpoint)
- OpenAI API key configured in `.env`

## Quick Start with Docker

### 1. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The API will be available at: `http://localhost:8001`

### 2. Build and Run with Docker (Manual)

```bash
# Build the image
docker build -t dspy-rag-api .

# Run the container
docker run -d \
  --name dspy-rag-api \
  --network host \
  -p 8001:8001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/artifacts:/app/artifacts \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  dspy-rag-api
```

### 3. Stop the Container

```bash
# With docker-compose
docker-compose down

# With docker
docker stop dspy-rag-api
docker rm dspy-rag-api
```

## Without Docker (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

Or with uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Testing the API

### Test with curl

```bash
# Test the health endpoint
curl http://localhost:8001/api/v1/health

# Ask a question
curl -X POST http://localhost:8001/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What did WESTDALE do in June 2022?"
  }'
```

### Expected Response

```json
{
  "question": "What did WESTDALE do in June 2022?",
  "answer": "In June 2022, WESTDALE entered into interest rate cap transactions...",
  "context_used": [
    "TO: Bethany Shay, Westdale Asset Management...",
    "..."
  ],
  "reasoning": null
}
```

## API Endpoints

All endpoints are prefixed with `/api/v1`

- `GET /api/v1/health` - Health check
- `POST /api/v1/ask` - Ask a question (main endpoint)
- `POST /api/v1/feedback` - Submit feedback for liked answers
- `POST /api/v1/compile` - Trigger DSPy compilation (requires training data)
- `POST /api/v1/recompile` - Recompile with feedback

## Interactive API Documentation

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Ports

- **8000**: Retrieval API (must be running separately)
- **8001**: DSPy RAG API (this application)

## Architecture

```
┌─────────────────────┐
│   User Request      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  DSPy RAG API       │ Port 8001
│  (Docker Container) │
└─────────┬───────────┘
          │
          ├──────────────────────┐
          │                      │
          ▼                      ▼
┌──────────────────┐   ┌─────────────────┐
│ Retrieval API    │   │  OpenAI GPT-4o  │
│ localhost:8000   │   │     (2 calls)   │
└──────────────────┘   └─────────────────┘
          │                      │
          │                      │
          └──────────┬───────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Final Answer  │
            └────────────────┘
```

## Flow per Query

1. **Receive question** from user
2. **Call retrieval API** at `http://localhost:8000/retrieve` to get 3-6 chunks
3. **Load compiled DSPy model** (or use uncompiled if not available)
4. **LLM Call #1 (Reason)**: Generate draft answer from context
5. **LLM Call #2 (Verify)**: Check and correct the answer
6. **Return verified answer** to user

**Total LLM calls per query: 2**

## Volume Mounts

The Docker container mounts these directories:

- `./data` → `/app/data` - Training samples and feedback
- `./artifacts` → `/app/artifacts` - Compiled DSPy models
- `./logs` → `/app/logs` - Application logs

## Environment Variables

Required in `.env`:

```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
```

## Troubleshooting

### Can't connect to retrieval API

- Ensure retrieval API is running on `localhost:8000`
- The container uses `network_mode: "host"` to access localhost services
- Test: `curl http://localhost:8000/retrieve`

### OpenAI API errors

- Check your API key in `.env`
- Verify your OpenAI account has credits
- Check the model name is correct (e.g., `gpt-4o-mini`)

### Container logs

```bash
# View logs
docker-compose logs -f

# Or with docker
docker logs -f dspy-rag-api
```

## Performance

- **Cold start**: ~1-2 seconds (loading model)
- **Query latency**: ~2-4 seconds (2 LLM calls + retrieval)
- **Cost per query**: <$0.001 (using gpt-4o-mini)

## Production Considerations

1. **Remove `--reload`** flag in production
2. **Use proper secrets management** (not `.env` files)
3. **Add rate limiting** to prevent abuse
4. **Use Redis caching** for frequently asked questions
5. **Monitor with logging and metrics**
6. **Set up health checks** in your orchestrator
