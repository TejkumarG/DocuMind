from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
from .ingestion_service import IngestionService
from .retrieval_service import RetrievalService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Ingestion and Retrieval Service", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
ingestion_service: Optional[IngestionService] = None
retrieval_service: Optional[RetrievalService] = None


class IngestRequest(BaseModel):
    file_name: Optional[str] = None


class IngestResponse(BaseModel):
    message: str
    status: str
    results: Optional[dict] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ingestion_service, retrieval_service

    milvus_host = os.getenv("MILVUS_HOST", "milvus-standalone")
    milvus_port = os.getenv("MILVUS_PORT", "19530")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    logger.info("Initializing Ingestion Service...")
    try:
        ingestion_service = IngestionService(
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            embedding_model=embedding_model
        )
        logger.info("Ingestion Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ingestion Service: {e}")
        raise

    logger.info("Initializing Retrieval Service...")
    try:
        retrieval_service = RetrievalService(
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            embedding_model=embedding_model
        )
        logger.info("Retrieval Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Retrieval Service: {e}")
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RAG Ingestion and Retrieval Service"}


@app.get("/milvus-health")
async def check_milvus_health():
    """Proxy endpoint to check Milvus health (with CORS)"""
    try:
        # Check if retrieval_service can connect to Milvus
        if retrieval_service and retrieval_service.milvus_client:
            return {"status": "healthy", "service": "Milvus"}
        else:
            raise HTTPException(status_code=503, detail="Milvus not initialized")
    except Exception as e:
        logger.error(f"Milvus health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get ingestion statistics"""
    if not ingestion_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        stats = ingestion_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents into the system from the default data directory.

    - **file_name**: Optional specific file name to ingest (if not provided, ingests all files)
    """
    if not ingestion_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Default data directory
    data_directory = "/app/data"

    if not os.path.exists(data_directory):
        raise HTTPException(status_code=404, detail=f"Data directory not found: {data_directory}")

    try:
        # Ingest from directory (with optional specific file)
        results = ingestion_service.ingest_directory(data_directory, request.file_name)

        # Prepare response
        total_ingested = len(results["ingested"])
        total_skipped = len(results["skipped"])
        total_failed = len(results["failed"])

        if request.file_name:
            message = f"File '{request.file_name}' processed"
        else:
            message = f"Processed all files from data directory"

        return IngestResponse(
            message=message,
            status="completed",
            results={
                "ingested": total_ingested,
                "skipped": total_skipped,
                "failed": total_failed,
                "details": results
            }
        )

    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class RetrieveRequest(BaseModel):
    query: str
    min_chunks: Optional[int] = 3
    max_chunks: Optional[int] = 6


@app.post("/retrieve")
async def retrieve_chunks(request: RetrieveRequest):
    """
    Hybrid Retrieval: Combines two scenarios for optimal results

    **Scenario 1 (Direct Semantic)**: 5 chunks
    - Step 1: Semantic search on ALL documents → top 3
    - Step 2: Extract document_ids from those 3 chunks
    - Step 3: Semantic search ONLY within those documents → top 5

    **Scenario 2 (Entity-filtered)**: 3 chunks
    - Step 1: Extract entities from query (persons, orgs, dates, etc.)
    - Step 2: Find documents containing those entities
    - Step 3: Semantic search within entity-matched documents → top 3

    **Final**: Combine and deduplicate → Max 8 unique chunks

    - **query**: The search query
    """
    if not retrieval_service:
        raise HTTPException(status_code=503, detail="Retrieval service not initialized")

    try:
        # Use Hybrid approach (Scenario 1 + Scenario 2)
        results = retrieval_service.retrieve_hybrid(query=request.query)
        return results

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
