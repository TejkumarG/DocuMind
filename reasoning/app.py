from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="DSPy RAG Pipeline",
    description="Two-stage Reason + Verify RAG system using DSPy",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["rag"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DSPy RAG Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "ask": "/api/v1/ask",
            "feedback": "/api/v1/feedback",
            "compile": "/api/v1/compile",
            "recompile": "/api/v1/recompile",
            "health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
