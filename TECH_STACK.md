# DocuMind - Technical Stack Overview

## Architecture

DocuMind is a hybrid RAG (Retrieval-Augmented Generation) system composed of three independent services:

1. **PDF-to-Markdown Service** - Document preprocessing
2. **RAG Service** - Embedding and retrieval
3. **Reasoning Service** - Query processing and answer generation

---

## 1. PDF-to-Markdown Service

### Purpose
Converts PDF documents into structured markdown using vision-based table detection and dual conversion strategies.

### Tech Stack
- **Runtime**: Python 3.11
- **Table Detection**:
  - PyTorch 2.0+
  - Transformers (Hugging Face)
  - Microsoft Table Transformer (DETR-based)
  - pdf2image + Pillow (PDF → image for detection)
- **PDF Conversion**:
  - **Non-table PDFs**: PyMuPDF4LLM (native text extraction)
  - **Table PDFs**: OpenAI Vision API (GPT-4o-mini) + PyMuPDF (page rendering)
- **Container**: Docker

### Key Features
- Vision-based table detection (confidence threshold: 0.90)
- Dual conversion strategy:
  - PyMuPDF4LLM for text-heavy documents
  - OpenAI Vision for complex tables
- Early exit optimization (scans first 5 pages)
- DPI: 200 for table detection
- Max image width: 1800px

---

## 2. RAG Service

### Purpose
Handles document ingestion, embedding generation, entity extraction, and hybrid semantic retrieval.

### Tech Stack
- **Runtime**: Python 3.11
- **Web Framework**: FastAPI + Uvicorn
- **Vector Database**: Milvus 2.3.3 (standalone)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
  - Dimension: 384
  - Framework: Sentence-Transformers 2.7.0
- **Entity Extraction**: spaCy 3.7.2
  - Model: en_core_web_lg (560MB)
  - NER types: PERSON, ORG, GPE, LOC, DATE
- **Document Loading**:
  - Primary: Markdown files (.md)
- **Container**: Docker

### Key Features
- Hybrid search (vector similarity + entity filtering)
- Entity-based metadata filtering with exclusion list
- Recursive character text splitting
- Top-K retrieval (K=6)
- Real-time entity extraction during ingestion
- Excluded entities: generic legal terms (buyer, seller, llc, etc.)

---

## 3. Reasoning Service

### Purpose
Processes user queries using DSPy-optimized prompts with two-stage reasoning and verification.

### Tech Stack
- **Runtime**: Python 3.11
- **Web Framework**: FastAPI + Uvicorn
- **LLM Framework**: DSPy 2.4.9
- **Language Model**: OpenAI API 1.3.7
  - Configurable model (GPT-3.5/GPT-4)
  - Temperature: Configurable
  - Max tokens: 1000
- **Training**: BootstrapFewShot optimizer
- **HTTP Client**: httpx 0.25.0
- **Container**: Docker

### Key Features
- Two-stage process: Reason → Verify
- Prompt optimization via DSPy compilation
- Feedback loop (stores liked answers)
- UUID-based cache busting (prevents OpenAI prompt caching)
- Training sample management
- Recompilation with user feedback

---

## Supporting Infrastructure

### Vector Database
- **Milvus 2.3.3** (standalone mode)
  - Collection: `document_chunks`
  - Vector dimension: 384
  - Metadata: entity fields (person, org, location, date)
  - Port: 19530

### Orchestration
- **Docker Compose**: Multi-container orchestration
- **Shared Volumes**: Document data persistence across services

### Communication
- RESTful APIs (FastAPI)
- JSON request/response format
- Independent services (no direct dependencies)

---

## Data Flow

```
1. Document Processing:
   PDF → Table Detection (Vision) → Route Decision
                                      ↓
                      ┌───────────────┴──────────────┐
                      ↓                              ↓
              PyMuPDF4LLM                    OpenAI Vision
              (No tables)                    (Has tables)
                      ↓                              ↓
                      └───────────────┬──────────────┘
                                      ↓
                                  Markdown

2. Ingestion:
   Markdown → Chunking → Embeddings + Entity Extraction
                              ↓
                    Milvus (Vector + Metadata)

3. Query Processing:
   User Query → Entity Detection → Milvus Search (Hybrid)
                                          ↓
                                    Top-6 Chunks
                                          ↓
                          DSPy (Reason → Verify)
                                          ↓
                                  Verified Answer
```

---

## Model Specifications

| Service | Component | Model/Library | Size | Purpose |
|---------|-----------|---------------|------|---------|
| PDF-to-MD | Table Detection | microsoft/table-transformer-detection | ~100MB | Vision-based table detection |
| PDF-to-MD | Text Conversion | PyMuPDF4LLM | ~5MB | LLM-optimized PDF extraction |
| PDF-to-MD | Table Conversion | OpenAI GPT-4V | API | Complex table extraction |
| RAG | Embeddings | all-MiniLM-L6-v2 | ~90MB | 384-dim vector generation |
| RAG | Entity Extraction | en_core_web_lg | ~560MB | Multi-class NER |
| Reasoning | LLM | OpenAI GPT (3.5/4) | API | Answer generation |
| Reasoning | Optimizer | DSPy BootstrapFewShot | - | Prompt compilation |

---

## Performance Characteristics

### PDF-to-Markdown
- **Table Detection**: ~2-3 seconds (first 5 pages, DPI 200)
- **PyMuPDF4LLM**: ~1-2 seconds per document
- **OpenAI Vision**: ~5-10 seconds per document (depends on pages)

### RAG Service
- **Ingestion**: ~6-7 seconds per document (900 chunks from 29 docs)
- **Entity Extraction**: Real-time during ingestion
- **Retrieval**: <1 second (top-6 chunks)

### Reasoning Service
- **Query Processing**: ~6-7 seconds (2 LLM calls: Reason + Verify)
- **Caching**: Disabled via UUID injection

---

## Deployment

### Ports
- PDF-to-MD: 7000
- RAG Service: 8000
- Reasoning Service: 9000
- Milvus: 19530

### Volume Mounts
- Shared markdown storage between PDF-to-MD and RAG
- Persistent Milvus data

### Network
- Docker bridge network
- Inter-service HTTP communication
