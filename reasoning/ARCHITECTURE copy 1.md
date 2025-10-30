# DSPy RAG Pipeline - Complete Architecture

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Application Flow](#application-flow)
3. [File Structure & Responsibilities](#file-structure--responsibilities)
4. [Request Flow Diagram](#request-flow-diagram)
5. [LLM Call Sequence](#llm-call-sequence)
6. [Data Flow](#data-flow)
7. [Component Details](#component-details)

---

## System Overview

**DSPy RAG Pipeline** is a two-stage Retrieval-Augmented Generation system that:
- Retrieves relevant context from your document store
- Uses DSPy's Reason + Verify pattern with 2 LLM calls
- Returns verified, accurate answers to questions

### Key Features
- ✅ **2 LLM calls per query**: Reason (draft) → Verify (correct)
- ✅ **Context retrieval**: Integrates with external retrieval API
- ✅ **OpenAI GPT-4o-mini**: Fast, cheap, accurate
- ✅ **Optional training**: Can be optimized with DSPy compilation
- ✅ **Feedback loop**: Store liked answers for future training

---

## Application Flow

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
└────────────────────┬────────────────────────────────────────┘
                     │ POST /api/v1/ask
                     │ {"question": "..."}
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (Port 8001)                │
│                     app.py + api/routes.py                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
┌──────────────────┐    ┌──────────────────────┐
│  Retrieval API   │    │  OpenAI API          │
│  (Port 8000)     │    │  (gpt-4o-mini)       │
│                  │    │                      │
│  Returns 3-6     │    │  2 LLM Calls:        │
│  context chunks  │    │  1. Reason (draft)   │
└──────────────────┘    │  2. Verify (final)   │
                        └──────────────────────┘
```

---

## File Structure & Responsibilities

```
reasoning/
│
├── app.py                              # FastAPI app entry point
│   └─> Creates FastAPI instance
│   └─> Includes routes from api/routes.py
│   └─> Configures CORS
│
├── api/
│   └── routes.py                       # API endpoint handlers
│       ├─> /ask          → Main question answering endpoint
│       ├─> /feedback     → Store user feedback
│       ├─> /compile      → Trigger DSPy compilation
│       ├─> /recompile    → Recompile with feedback
│       └─> /health       → Health check
│
├── config/
│   └── settings.py                     # Configuration management
│       └─> Loads .env variables
│       └─> OpenAI API key, model, temperature
│       └─> File paths for models, data
│
├── models/
│   └── schemas.py                      # Pydantic request/response models
│       ├─> QuestionRequest
│       ├─> AnswerResponse
│       ├─> FeedbackRequest
│       ├─> CompileRequest
│       └─> CompileResponse
│
├── handlers/
│   │
│   ├── runtime/                        # ONLINE PHASE (per query)
│   │   │
│   │   ├── 2_get_context.py           # Retrieve context chunks
│   │   │   └─> Calls retrieval API (localhost:8000/retrieve)
│   │   │   └─> Extracts "text" from response chunks
│   │   │   └─> Returns List[str] (3-6 chunks)
│   │   │
│   │   ├── 3_load_dspy.py             # Load DSPy model
│   │   │   └─> Tries to load compiled model from artifacts/
│   │   │   └─> Falls back to ReasonVerifyRAG() if not found
│   │   │
│   │   ├── 4_configure_model.py       # Configure OpenAI
│   │   │   └─> Sets up dspy.OpenAI with API key
│   │   │   └─> Configures temperature, model name
│   │   │
│   │   ├── 5_reason_verify.py         # Two-stage RAG pipeline
│   │   │   ├─> ReasonSignature: Generate draft answer
│   │   │   ├─> VerifySignature: Verify and correct
│   │   │   └─> ReasonVerifyRAG.forward(): Execute both stages
│   │   │
│   │   └── 7_store_feedback.py        # Store user feedback
│   │       └─> Appends to data/feedback.jsonl
│   │
│   └── offline/                        # OFFLINE PHASE (training)
│       │
│       ├── 1_prepare_samples.py       # Prepare training data
│       │   └─> Load training_samples.json
│       │   └─> Create sample data if needed
│       │
│       ├── 2_compile_dspy.py          # Compile DSPy model
│       │   └─> Load training samples
│       │   └─> Use optimizer (MIPROv2/MIPRO/BootstrapFewShot)
│       │   └─> Save compiled model to artifacts/
│       │
│       └── 3_recompile.py             # Recompile with feedback
│           └─> Merge feedback.jsonl into training_samples.json
│           └─> Run compile_dspy_model()
│
├── data/                               # Data storage
│   ├── training_samples.json          # Training examples (100+)
│   └── feedback.jsonl                 # User feedback (append-only)
│
├── artifacts/                          # Model artifacts
│   └── compiled_rag_v1.dspy           # Compiled DSPy model
│
└── logs/                               # Application logs
```

---

## Request Flow Diagram

### Complete Flow: User Question → Answer

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User sends question                                       │
│    POST /api/v1/ask                                          │
│    {"question": "What did WESTDALE do in June 2022?"}        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. FastAPI Route Handler (api/routes.py:ask_question)       │
│    • Validates request with QuestionRequest schema          │
│    • Extracts question string                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Get Context (handlers/runtime/2_get_context.py)          │
│    • POST to http://localhost:8000/retrieve                 │
│    • Payload: {"query": "...", "min_chunks": 3, "max": 6}   │
│    • Response: {"chunks": [{"text": "..."}, ...]}            │
│    • Extracts text from each chunk                          │
│    • Returns: List[str] with 3-6 context strings            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Get RAG Model (api/routes.py:get_rag_model)              │
│    • Checks if model is cached in _rag_model global var     │
│    • If not cached:                                          │
│      a. Configure OpenAI (handlers/runtime/4_configure...)   │
│         └─> dspy.settings.configure(lm=dspy.OpenAI(...))    │
│      b. Load DSPy model (handlers/runtime/3_load_dspy.py)   │
│         └─> Load compiled model OR create ReasonVerifyRAG() │
│    • Cache model for future requests                        │
│    • Returns: ReasonVerifyRAG instance                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Execute Reason + Verify (handlers/runtime/5_reason_...)  │
│                                                              │
│    Step 5a: REASON (LLM Call #1)                            │
│    ┌────────────────────────────────────────────┐           │
│    │ • Signature: ReasonSignature                │           │
│    │ • Input: context + question                 │           │
│    │ • LLM generates DRAFT answer                │           │
│    │ • Uses ChainOfThought reasoning             │           │
│    └────────────┬───────────────────────────────┘           │
│                 │                                            │
│                 ▼                                            │
│    Step 5b: VERIFY (LLM Call #2)                            │
│    ┌────────────────────────────────────────────┐           │
│    │ • Signature: VerifySignature                │           │
│    │ • Input: context + question + draft_answer  │           │
│    │ • LLM verifies and corrects draft           │           │
│    │ • Returns VERIFIED answer                   │           │
│    └────────────┬───────────────────────────────┘           │
│                 │                                            │
└─────────────────┴──────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Format Response (api/routes.py:ask_question)             │
│    • Extract verified_answer from result                    │
│    • Create AnswerResponse object                           │
│    • Include: question, answer, context_used                │
│    • Return JSON response                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. Response to User                                          │
│    {                                                         │
│      "question": "What did WESTDALE do in June 2022?",      │
│      "answer": "In June 2022, WESTDALE entered into...",    │
│      "context_used": ["chunk1", "chunk2", ...],             │
│      "reasoning": null                                      │
│    }                                                         │
└──────────────────────────────────────────────────────────────┘
```

---

## LLM Call Sequence

### Two LLM Calls Per Query

```
Question: "What did WESTDALE do in June 2022?"
Context: [3-6 chunks of retrieved text]

┌─────────────────────────────────────────────────────────────┐
│ LLM CALL #1: REASON                                         │
├─────────────────────────────────────────────────────────────┤
│ Signature: ReasonSignature                                  │
│ Method: dspy.ChainOfThought                                 │
│                                                             │
│ Input:                                                      │
│   • context: "TO: Bethany Shay, Westdale...\n\n..."        │
│   • question: "What did WESTDALE do in June 2022?"         │
│                                                             │
│ LLM Process:                                                │
│   1. Read and understand context                           │
│   2. Identify relevant information                         │
│   3. Generate draft answer                                 │
│                                                             │
│ Output:                                                     │
│   • answer: "In June 2022, Westdale entered into..."       │
│                                                             │
│ Cost: ~0.5¢ per 1000 tokens (gpt-4o-mini)                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ draft_answer
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM CALL #2: VERIFY                                         │
├─────────────────────────────────────────────────────────────┤
│ Signature: VerifySignature                                  │
│ Method: dspy.ChainOfThought                                 │
│                                                             │
│ Input:                                                      │
│   • context: "TO: Bethany Shay, Westdale...\n\n..."        │
│   • question: "What did WESTDALE do in June 2022?"         │
│   • draft_answer: "In June 2022, Westdale entered..."      │
│                                                             │
│ LLM Process:                                                │
│   1. Re-read context                                       │
│   2. Compare draft_answer with context                     │
│   3. Check for accuracy, completeness                      │
│   4. Correct any errors or omissions                       │
│   5. Generate verified answer                              │
│                                                             │
│ Output:                                                     │
│   • verified_answer: "In June 2022, WESTDALE entered..."   │
│                                                             │
│ Cost: ~0.5¢ per 1000 tokens (gpt-4o-mini)                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ verified_answer
                         ▼
                   Final Answer ✓
```

**Total Cost Per Query**: ~$0.001 (less than 1 cent)

---

## Data Flow

### Runtime Data Flow (Per Query)

```
User Question
    ↓
┌────────────────────┐
│ "What did WESTDALE  │
│ do in June 2022?"   │
└────────┬───────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 1: Context Retrieval          │
│ POST localhost:8000/retrieve       │
│                                    │
│ Request:                           │
│ {                                  │
│   "query": "What did WESTDALE...", │
│   "min_chunks": 3,                 │
│   "max_chunks": 6                  │
│ }                                  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Response from Retrieval API:       │
│ {                                  │
│   "query": "...",                  │
│   "chunks": [                      │
│     {"text": "TO: Bethany...",     │
│      "document_id": "...", ...},   │
│     {"text": "POWELL COLEMAN...",  │
│      "document_id": "...", ...},   │
│     ...                            │
│   ]                                │
│ }                                  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 2: Extract Text               │
│ context = [                        │
│   "TO: Bethany Shay...",           │
│   "POWELL COLEMAN...",             │
│   "•Fidelity...",                  │
│   "ASSIGNMENT AND..."              │
│ ]                                  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 3: Reason (LLM Call #1)       │
│                                    │
│ Input to OpenAI:                   │
│ {                                  │
│   "context": "TO: Bethany...\n\n"  │
│   "question": "What did..."        │
│ }                                  │
│                                    │
│ LLM Response:                      │
│ {                                  │
│   "answer": "In June 2022,         │
│              Westdale entered..."  │
│ }                                  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 4: Verify (LLM Call #2)       │
│                                    │
│ Input to OpenAI:                   │
│ {                                  │
│   "context": "TO: Bethany...\n\n"  │
│   "question": "What did..."        │
│   "draft_answer": "In June 2022..." │
│ }                                  │
│                                    │
│ LLM Response:                      │
│ {                                  │
│   "verified_answer": "In June..."  │
│ }                                  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Final Response to User:            │
│ {                                  │
│   "question": "What did...",       │
│   "answer": "In June 2022...",     │
│   "context_used": [...],           │
│   "reasoning": null                │
│ }                                  │
└────────────────────────────────────┘
```

---

## Component Details

### 1. FastAPI Application (app.py)

**Purpose**: Main entry point for the application

**Key Features**:
- Creates FastAPI instance with title, description, version
- Configures CORS middleware (allows all origins)
- Includes routes from `api/routes.py`
- Exposes root endpoint with API information
- Runs on port 8001

**Code Location**: `/app.py`

---

### 2. API Routes (api/routes.py)

**Purpose**: Define all API endpoints

**Endpoints**:

| Endpoint | Method | Description | Handler |
|----------|--------|-------------|---------|
| `/api/v1/ask` | POST | Answer questions | `ask_question()` |
| `/api/v1/feedback` | POST | Store feedback | `submit_feedback()` |
| `/api/v1/compile` | POST | Compile DSPy | `compile_model()` |
| `/api/v1/recompile` | POST | Recompile with feedback | `recompile_model()` |
| `/api/v1/health` | GET | Health check | `health_check()` |

**Code Location**: `/api/routes.py`

---

### 3. Context Retrieval (handlers/runtime/2_get_context.py)

**Purpose**: Retrieve relevant context chunks from external API

**Process**:
1. Receives question from user
2. Calls external retrieval API at `localhost:8000/retrieve`
3. Sends: `{"query": question, "min_chunks": 3, "max_chunks": 6}`
4. Receives: `{"chunks": [{"text": "...", ...}, ...]}`
5. Extracts "text" field from each chunk
6. Returns: `List[str]` with 3-6 context strings

**Configuration**:
- Uses `RETRIEVAL_API_URL` env var (defaults to `localhost:8000`)
- Timeout: 30 seconds
- Returns empty list on error

**Code Location**: `/handlers/runtime/2_get_context.py`

---

### 4. DSPy Model Loading (handlers/runtime/3_load_dspy.py)

**Purpose**: Load compiled DSPy model or create new instance

**Process**:
1. Check if compiled model exists at `artifacts/compiled_rag_v1.dspy`
2. If exists:
   - Load using `dspy.load(model_path)`
   - Return compiled model
3. If not exists or load fails:
   - Import `ReasonVerifyRAG` class
   - Create new instance
   - Return uncompiled model

**Code Location**: `/handlers/runtime/3_load_dspy.py`

---

### 5. OpenAI Configuration (handlers/runtime/4_configure_model.py)

**Purpose**: Configure DSPy to use OpenAI

**Process**:
1. Read settings from `config/settings.py`
2. Create `dspy.OpenAI` instance with:
   - Model: `gpt-4o-mini`
   - API Key: from `.env`
   - Temperature: `0.0`
3. Configure DSPy globally: `dspy.settings.configure(lm=lm)`

**Code Location**: `/handlers/runtime/4_configure_model.py`

---

### 6. Reason + Verify Pipeline (handlers/runtime/5_reason_verify.py)

**Purpose**: Two-stage RAG pipeline with reasoning and verification

**Components**:

**ReasonSignature**:
- Input: context (str), question (str)
- Output: answer (str)
- Purpose: Generate draft answer

**VerifySignature**:
- Input: context (str), question (str), draft_answer (str)
- Output: verified_answer (str)
- Purpose: Verify and correct draft

**ReasonVerifyRAG Class**:
- Inherits from `dspy.Module`
- Method: `forward(context, question)`
- Process:
  1. Join context list into single string
  2. Call `self.reason()` → LLM call #1
  3. Call `self.verify()` → LLM call #2
  4. Return verified result

**Code Location**: `/handlers/runtime/5_reason_verify.py`

---

### 7. Feedback Storage (handlers/runtime/7_store_feedback.py)

**Purpose**: Store user feedback for future training

**Process**:
1. Receive: question, context, answer, liked (bool)
2. If `liked=True`:
   - Create JSON entry
   - Append to `data/feedback.jsonl`
3. If `liked=False`:
   - Ignore (don't store negative feedback)

**Code Location**: `/handlers/runtime/7_store_feedback.py`

---

## Training Phase (Optional)

### Offline Compilation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Prepare Training Data                                    │
│    • Create data/training_samples.json                      │
│    • Format: [{"question": "...", "context": [...],         │
│                "answer": "..."}, ...]                       │
│    • Need: 100+ examples                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Run Compilation                                          │
│    $ python handlers/offline/2_compile_dspy.py              │
│                                                             │
│    Process:                                                 │
│    • Load training_samples.json                             │
│    • Configure OpenAI                                       │
│    • Create ReasonVerifyRAG instance                        │
│    • Initialize optimizer (MIPROv2/MIPRO/BootstrapFewShot)  │
│    • Run optimizer.compile(rag, trainset)                   │
│    • Makes 300-600 LLM calls to optimize prompts            │
│    • Save to artifacts/compiled_rag_v1.dspy                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Compiled Model Created                                   │
│    • File: artifacts/compiled_rag_v1.dspy                   │
│    • Optimized prompts for Reason + Verify                  │
│    • Improved accuracy and consistency                      │
│    • API will auto-use this on next restart                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `OPENAI_TEMPERATURE` | `0.0` | Temperature for LLM |
| `RETRIEVAL_API_URL` | `http://localhost:8000` | Retrieval API base URL |

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| LLM Calls per Query | 2 |
| Average Latency | 2-4 seconds |
| Cost per Query | < $0.001 |
| Context Chunks | 3-6 |
| Max Context Length | ~6000 tokens |
| Compilation Cost | $0.50-1.00 (one-time) |

---

## Next Steps

1. **Test the API**: `curl http://localhost:8001/api/v1/health`
2. **Ask Questions**: See QUICKSTART.md
3. **Deploy**: See DEPLOYMENT.md
4. **Train Model**: When you have 100+ examples, compile DSPy

---

## Support

- **API Docs**: http://localhost:8001/docs
- **Logs**: `docker logs -f dspy-rag-api`
- **Issues**: Check error messages in logs
