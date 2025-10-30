"""API routes for the chatbot."""
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.models.schemas import QueryRequest, QueryResponse
from app.database.mongo_client import save_chat

# Import the REAL Semantic Kernel orchestrator
from app.core.semantic_kernel_orchestrator import semantic_kernel_orchestrator

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(payload: QueryRequest):
    """Process user query using Semantic Kernel orchestration.
    
    This endpoint uses Microsoft Semantic Kernel with:
    - Automatic function calling
    - Native plugin system
    - RAG integration
    - Action execution
    
    Args:
        payload: QueryRequest with query and user_id
        
    Returns:
        QueryResponse with intent, response, and metadata
    """
    try:
        # Call the REAL SK orchestrator (no fallbacks!)
        logger.info(f"Processing query for user {payload.user_id}: {payload.query[:50]}...")
        
        result = await semantic_kernel_orchestrator(
            user_query=payload.query,
            user_id=payload.user_id
        )
        
        logger.info(f"✓ Query processed: intent={result.get('intent')}, action={result.get('action_invoked')}")
        
        # Save chat history asynchronously (don't fail if this errors)
        try:
            await run_in_threadpool(
                save_chat,
                payload.user_id,
                payload.query,
                result.get("response", ""),
                action_invoked=result.get("action_invoked"),
                confidence=result.get("confidence", 0.0),
            )
        except Exception as save_error:
            logger.warning(f"Failed to save chat history: {save_error}")
            # Don't fail the request if saving fails
        
        # Return the response
        return QueryResponse(**result)
        
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        
        # Return user-friendly error
        raise HTTPException(
            status_code=500,
            detail="Failed to process your query. Please try again."
        )


@router.get("/health")
async def health_check():
    """Health check endpoint to verify SK is initialized."""
    try:
        from app.core.semantic_kernel_orchestrator import get_kernel
        kernel = get_kernel()
        
        # Check if kernel has services
        services = kernel.services
        has_chat = any("chat" in str(type(s)).lower() for s in services.values())
        
        # Check plugins
        plugins = list(kernel.plugins.keys()) if hasattr(kernel, 'plugins') else []
        
        return {
            "status": "healthy",
            "semantic_kernel": "initialized",
            "chat_service": "available" if has_chat else "missing",
            "plugins": plugins
        }
    except Exception as e:
        logger.exception("Health check failed")
        return {
            "status": "unhealthy",
            "error": str(e)
        }