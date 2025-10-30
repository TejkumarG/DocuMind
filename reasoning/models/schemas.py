from pydantic import BaseModel, Field
from typing import List, Optional


class QuestionRequest(BaseModel):
    """Request model for asking a question"""
    question: str = Field(..., description="The question to answer")


class AnswerResponse(BaseModel):
    """Response model for the answer"""
    question: str
    answer: str
    context_used: List[str]
    reasoning: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Request model for storing feedback"""
    question: str
    context: List[str]
    answer: str
    liked: bool = True


class CompileRequest(BaseModel):
    """Request to trigger compilation"""
    num_samples: Optional[int] = 100


class CompileResponse(BaseModel):
    """Response after compilation"""
    status: str
    model_path: str
    num_samples_used: int
