"""API request/response schemas."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for /api/ask endpoint."""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., min_length=1, description="User's question")


class RetrievedDocument(BaseModel):
    """Schema for a retrieved document from RAG."""
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """Response schema for /api/ask endpoint."""
    intent: str
    response: str
    source_docs: Optional[List[Union[str, RetrievedDocument]]] = Field(
        default=[],
        description="Retrieved context documents, either as strings or structured docs"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score for intent classification"
    )
    action_invoked: Optional[str] = Field(
        default=None,
        description="Name of any action function that was called"
    )
