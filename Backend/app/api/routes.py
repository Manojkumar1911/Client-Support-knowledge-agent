from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from app.models.schemas import QueryRequest, QueryResponse
from app.database.mongo_client import save_chat
from app.core.semantic_kernel_agent import semantic_kernel_orchestrator

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(payload: QueryRequest):
    # Run orchestrator in a threadpool to avoid blocking the event loop
    result = await run_in_threadpool(semantic_kernel_orchestrator, payload.query, payload.user_id)
    # Save chat asynchronously (fire-and-forget is fine here), but keep simple sync save
    try:
        await run_in_threadpool(
            save_chat,
            payload.user_id,
            payload.query,
            result.get("response", ""),
            action_invoked=result.get("action_invoked"),
            confidence=result.get("confidence"),
        )
    except Exception:
        # Don't fail the API if saving the chat fails
        pass
    return QueryResponse(**result)
