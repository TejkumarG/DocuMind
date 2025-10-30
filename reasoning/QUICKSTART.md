# Quick Start Guide

## Prerequisites

✅ Docker and Docker Compose installed
✅ Retrieval API running on `http://localhost:8000`
✅ OpenAI API key already configured in `.env`

## Start the Application

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Option 2: Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## Test the Application

Run the test script:

```bash
python test_api.py
```

Or manually test with curl:

```bash
# Test with the WESTDALE question
curl -X POST http://localhost:8001/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What did WESTDALE do in June 2022?"
  }'
```

## Expected Flow

1. **Your question** → DSPy RAG API (port 8001)
2. **Retrieval API call** → Get 3-6 context chunks from localhost:8000
3. **LLM Call #1 (Reason)** → Generate draft answer using OpenAI GPT-4o-mini
4. **LLM Call #2 (Verify)** → Check and correct the answer
5. **Return answer** → Final verified response

**Total: 2 LLM calls per query, ~$0.001 cost**

## API Endpoints

- `GET /api/v1/health` - Check if API is running
- `POST /api/v1/ask` - Ask a question (main endpoint)
- `POST /api/v1/feedback` - Store liked answers for future training
- `POST /api/v1/compile` - Train/compile DSPy model (requires training data)

## Interactive Documentation

Open in your browser:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## What Happens When You Ask a Question?

```
┌────────────────────────────────────────────────────────────┐
│ POST /api/v1/ask                                           │
│ { "question": "What did WESTDALE do in June 2022?" }       │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Step 1: Get Context (handlers/runtime/2_get_context.py)   │
│ → Calls http://localhost:8000/retrieve                    │
│ → Returns 3-6 chunks with "text" field extracted          │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Step 2: Load DSPy Model (handlers/runtime/3_load_dspy.py) │
│ → Loads compiled model if exists                          │
│ → Otherwise uses uncompiled ReasonVerifyRAG               │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Step 3: Configure OpenAI (handlers/runtime/4_configure...py)│
│ → Sets up gpt-4o-mini with your API key                   │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Step 4: Reason + Verify (handlers/runtime/5_reason_...py) │
│ → LLM Call #1: Generate draft answer from context         │
│ → LLM Call #2: Verify and correct the answer              │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Response:                                                  │
│ {                                                          │
│   "question": "What did WESTDALE do in June 2022?",        │
│   "answer": "In June 2022, WESTDALE entered into...",     │
│   "context_used": ["chunk 1", "chunk 2", ...],            │
│   "reasoning": null                                        │
│ }                                                          │
└────────────────────────────────────────────────────────────┘
```

## Currently Running in Uncompiled Mode

Right now, the system works **without training/compilation**. It uses:

- ✅ Base DSPy Reason + Verify pipeline
- ✅ 2 LLM calls per query
- ✅ Your retrieval API for context
- ⚠️ Prompts are NOT optimized yet

### To Enable Compiled/Optimized Mode (Later):

1. Create training data in `data/training_samples.json` (100 examples)
2. Run: `python handlers/offline/2_compile_dspy.py`
3. Compiled model saved to `artifacts/compiled_rag_v1.dspy`
4. Restart API - it will automatically use the compiled version

**Don't worry about training now - the system works fine without it!**

## Stop the Application

```bash
# If using docker-compose
docker-compose down

# If using docker
docker stop dspy-rag-api

# If running locally (Ctrl+C to stop)
```

## Next Steps

1. ✅ Test with the provided question
2. ✅ Try other questions from your documents
3. ✅ Submit feedback for good answers via `/api/v1/feedback`
4. ⏰ Later: Collect 100 training examples and compile the model

## Need Help?

- Check logs: `docker-compose logs -f`
- View API docs: http://localhost:8001/docs
- Read full docs: `README.md` and `DEPLOYMENT.md`
