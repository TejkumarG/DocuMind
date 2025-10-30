# DSPy RAG Pipeline - FastAPI Application

Two-stage Reason + Verify RAG system using DSPy with FastAPI.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
```

### 3. Replace Context Retriever

The file `handlers/runtime/2_get_context.py` currently returns mock data. Replace the `get_context()` function with your actual retriever that returns a list of strings (6 chunks as per the plan).

## Usage

### Start the FastAPI Server

```bash
python app.py
```

Or with uvicorn:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Ask a Question (Main Endpoint)

```bash
POST /api/v1/ask
Content-Type: application/json

{
  "question": "Who founded Tesla Motors?"
}
```

Response:
```json
{
  "question": "Who founded Tesla Motors?",
  "answer": "Tesla Motors was founded by Martin Eberhard and Marc Tarpenning.",
  "context_used": ["context chunk 1", "context chunk 2", ...],
  "reasoning": null
}
```

### 2. Submit Feedback (Store Liked Answers)

```bash
POST /api/v1/feedback
Content-Type: application/json

{
  "question": "Who founded Tesla Motors?",
  "context": ["context chunk 1", "context chunk 2"],
  "answer": "Tesla Motors was founded by Martin Eberhard and Marc Tarpenning.",
  "liked": true
}
```

### 3. Compile DSPy Model (Offline Training)

```bash
POST /api/v1/compile
Content-Type: application/json

{
  "num_samples": 100
}
```

### 4. Recompile with Feedback

```bash
POST /api/v1/recompile
```

### 5. Health Check

```bash
GET /api/v1/health
```

## Workflow

### Offline Phase (First Time Setup)

1. **Prepare Training Data**: Create `data/training_samples.json` with 100 examples:

```python
python handlers/offline/1_prepare_samples.py
```

2. **Compile DSPy Model**:

```python
python handlers/offline/2_compile_dspy.py
```

This will:
- Use MIPROv2 optimizer
- Make 300-600 LLM calls
- Save compiled model to `artifacts/compiled_rag_v1.dspy`

### Online Phase (Runtime)

1. **Start the API**:

```bash
python app.py
```

2. **Ask Questions** via `/api/v1/ask` endpoint

3. **Submit Feedback** for liked answers via `/api/v1/feedback`

4. **Periodically Recompile** when you have enough feedback (50+ new examples):

```bash
curl -X POST http://localhost:8000/api/v1/recompile
```

## Architecture

### Flow per Query

```
User Question
    ↓
Get Context (6 chunks) ← handlers/runtime/2_get_context.py
    ↓
Load Compiled DSPy ← handlers/runtime/3_load_dspy.py
    ↓
Configure Model ← handlers/runtime/4_configure_model.py
    ↓
Reason + Verify (2 LLM calls) ← handlers/runtime/5_reason_verify.py
    ↓
Return Answer
```

### File Structure

```
reasoning/
├── app.py                          # Main FastAPI application
├── requirements.txt                # Dependencies
├── .env                            # Environment variables
│
├── api/
│   └── routes.py                   # API routes
│
├── config/
│   └── settings.py                 # Settings management
│
├── models/
│   └── schemas.py                  # Pydantic models
│
├── handlers/
│   ├── runtime/                    # Online phase handlers
│   │   ├── 2_get_context.py       # Context retrieval
│   │   ├── 3_load_dspy.py         # Load compiled model
│   │   ├── 4_configure_model.py   # Model configuration
│   │   ├── 5_reason_verify.py     # Reason + Verify logic
│   │   └── 7_store_feedback.py    # Feedback storage
│   │
│   └── offline/                    # Offline phase handlers
│       ├── 1_prepare_samples.py   # Prepare training data
│       ├── 2_compile_dspy.py      # Compile DSPy model
│       └── 3_recompile.py         # Recompile with feedback
│
├── data/                           # Data storage
│   ├── training_samples.json      # Training examples
│   └── feedback.jsonl             # User feedback
│
├── artifacts/                      # Model artifacts
│   └── compiled_rag_v1.dspy       # Compiled model
│
└── logs/                           # Logs
```

## Key Components

### ReasonVerifyRAG Pipeline

Two-stage DSPy module:

1. **Reason**: Generate draft answer from context
2. **Verify**: Check and correct the answer

### Model Compilation

- Uses MIPROv2 optimizer
- Trains on 100 examples
- Optimizes prompts automatically
- Cost: ~$0.50-1.00 per compilation (on gpt-4o-mini)

### Runtime Costs

- 2 LLM calls per query (Reason + Verify)
- ~1.5k tokens per query
- Cost: <$0.001 per query

## Next Steps

1. ✅ Replace `handlers/runtime/2_get_context.py` with your actual retriever
2. ✅ Create training data in `data/training_samples.json`
3. ✅ Set your OpenAI API key in `.env`
4. ✅ Run compilation: `python handlers/offline/2_compile_dspy.py`
5. ✅ Start the API: `python app.py`
6. ✅ Test with questions!

## Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
