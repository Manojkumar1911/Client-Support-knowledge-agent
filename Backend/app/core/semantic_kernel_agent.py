"""Semantic kernel orchestrator for routing queries and generating responses."""
from typing import Optional, Dict, Any, List
import re
import logging
from app.core.rag_engine import rag_engine
from app.llm.llm_client import generate_response, classify_intent
from app.core import actions

logger = logging.getLogger(__name__)


def _extract_ticket_id(text: str) -> Optional[str]:
    """Extract a ticket ID from text."""
    # Simple extraction: look for a number (ticket id) in the text
    m = re.search(r"\b(\d{3,12})\b", text)
    return m.group(1) if m else None


def retrieve_relevant_docs(query: str, top_k: int = 3):
    """Module-level wrapper around rag_engine.retrieve_relevant_docs for easier testing."""
    return rag_engine.retrieve_relevant_docs(query, top_k=top_k)


async def semantic_kernel_orchestrator(user_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Orchestrate retrieval, intent detection, and action calls.
    
    The orchestrator now uses:
    1. Rule-based greeting detection
    2. LLM-based intent classification with few-shot examples
    3. Structured response formatting using templates
    
    Args:
        user_query: The user's question or request
        user_id: Optional user identifier
        
    Returns:
        Dict with fields:
            intent: The detected intent
            response: The response text
            source_docs: List of relevant documents
            confidence: Confidence score (0-1)
            action_invoked: Name of any action that was called
    """
    try:
        # 1. Classify intent using LLM (with rule-based greeting detection first)
        intent, confidence = await classify_intent(user_query)
        logger.info(f"Classified intent: {intent} ({confidence})")
        
        # 2. For greetings, generate quick response without RAG
        if intent == "greeting":
            return {
                "intent": intent,
                "response": generate_response(user_query, intent="greeting"),
                "source_docs": [],
                "confidence": confidence,
                "action_invoked": None
            }
        
        # 3. For other intents, retrieve context
        context_docs = retrieve_relevant_docs(user_query, top_k=3)
        
        # Sort by similarity score
        context_docs.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        context_text = "\n\n".join(doc['text'] for doc in context_docs)

        # Log relevant docs for debugging
        for doc in context_docs:
            logger.debug(f"Retrieved doc with score {doc.get('similarity_score', 0.0):.2f}: {doc['text'][:100]}...")

        # 4. Process intent-specific actions
        action_result = None
        action_name = None
        
        # Handle password reset
        if intent == "password_reset":
            result = actions.reset_password(user_id or "")
            action_name = "reset_password"
            action_result = result
        
        # Handle ticket status
        elif intent == "check_ticket_status":
            ticket_id = _extract_ticket_id(user_query)
            if ticket_id:
                result = actions.check_ticket_status(ticket_id)
                action_name = "check_ticket_status"
                action_result = result
        
        # Handle summarization
        elif intent == "generate_summary":
            docs_texts = [d['text'] for d in context_docs]
            result = actions.generate_summary(docs_texts)
            action_name = "generate_summary"
            action_result = result

        # 5. Generate final response using template
        response = generate_response(
            prompt=user_query,
            context=context_text,
            intent=intent,
            action_result=action_result or ""
        )

        return {
            "intent": intent,
            "response": response,
            "source_docs": context_docs,
            "confidence": confidence,
            "action_invoked": action_name
        }

    except Exception as exc:
        logger.exception("Error in semantic kernel orchestrator: %s", exc)
        # Safe fallback with proper error message
        try:
            fallback = "Sorry, I encountered an error while processing your request. " \
                      "Please try again or contact support if this persists."
            
        except Exception:
            fallback = "Sorry, something went wrong. Please try again later."
            
        return {
            "intent": "error",
            "response": fallback,
            "source_docs": [],
            "confidence": 0.0,
            "action_invoked": None
        }