from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from importlib import import_module
from models.schemas import (
    QuestionRequest,
    AnswerResponse,
    FeedbackRequest,
    CompileRequest,
    CompileResponse
)

# Import runtime functions (needed for main functionality)
get_context_module = import_module('handlers.runtime.2_get_context')
get_context = get_context_module.get_context

load_dspy_module = import_module('handlers.runtime.3_load_dspy')
load_compiled_dspy = load_dspy_module.load_compiled_dspy

configure_model_module = import_module('handlers.runtime.4_configure_model')
configure_dspy_model = configure_model_module.configure_dspy_model

store_feedback_module = import_module('handlers.runtime.7_store_feedback')
store_feedback = store_feedback_module.store_feedback

# NOTE: Offline modules (compile, recompile) are imported lazily in endpoints
# to avoid loading training dependencies at startup


router = APIRouter()

# Global variable to cache the loaded model
_rag_model = None


def get_rag_model():
    """Load and cache the RAG model"""
    global _rag_model
    if _rag_model is None:
        configure_dspy_model()
        _rag_model = load_compiled_dspy()
    return _rag_model


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Main endpoint to ask a question and get an answer using RAG pipeline.

    Flow:
    1. Receive question
    2. Get context (6 chunks)
    3. Load compiled DSPy
    4. Configure model
    5. Reason + Verify (2 LLM calls)
    6. Return answer
    """
    try:
        question = request.question

        # Step 1: Get context chunks
        context = get_context(question)

        # Step 2: Get RAG model
        rag = get_rag_model()

        # Step 3: Run Reason + Verify
        result = rag.forward(context=context, question=question)

        # Extract answer
        answer = result.verified_answer if hasattr(result, 'verified_answer') else str(result)

        return AnswerResponse(
            question=question,
            answer=answer,
            context_used=context,
            reasoning=None  # Can add reasoning trace if needed
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Store user feedback (liked answers) for future recompilation.

    When users like an answer, store it to feedback.jsonl
    """
    try:
        store_feedback(
            question=request.question,
            context=request.context,
            answer=request.answer,
            liked=request.liked
        )

        return {
            "status": "success",
            "message": "Feedback stored successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing feedback: {str(e)}")


@router.post("/compile", response_model=CompileResponse)
async def compile_model(request: CompileRequest):
    """
    Trigger DSPy compilation (offline training phase).

    This is typically run periodically, not on every request.
    """
    try:
        # Lazy import of compilation module
        compile_dspy_module = import_module('handlers.offline.2_compile_dspy')
        compile_dspy_model = compile_dspy_module.compile_dspy_model

        num_samples = request.num_samples

        model_path = compile_dspy_model(num_samples=num_samples)

        # Clear cached model so it reloads
        global _rag_model
        _rag_model = None

        return CompileResponse(
            status="success",
            model_path=model_path,
            num_samples_used=num_samples
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compiling model: {str(e)}")


@router.post("/recompile", response_model=CompileResponse)
async def recompile_model():
    """
    Recompile model with feedback data merged into training samples.

    This merges feedback.jsonl into training_samples.json and recompiles.
    """
    try:
        # Lazy import of recompile module
        recompile_module = import_module('handlers.offline.3_recompile')
        recompile_with_feedback = recompile_module.recompile_with_feedback

        model_path = recompile_with_feedback()

        # Clear cached model so it reloads
        global _rag_model
        _rag_model = None

        return CompileResponse(
            status="success",
            model_path=model_path,
            num_samples_used=-1  # Unknown until we check
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recompiling model: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DSPy RAG Pipeline"
    }
