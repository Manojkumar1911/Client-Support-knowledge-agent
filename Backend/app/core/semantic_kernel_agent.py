"""Semantic kernel orchestrator for routing queries and generating responses."""
from typing import Optional, Dict, Any, List
import re
import logging
from app.core.rag_engine import rag_engine
from app.llm.llm_client import generate_response
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


def semantic_kernel_orchestrator(user_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Orchestrate retrieval, intent detection, and action calls.
    
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
        # Retrieve context from RAG
        context_docs_raw = retrieve_relevant_docs(user_query, top_k=3)
        
        # Normalize docs: tests may return plain text strings, while RAG returns dicts
        context_docs: List[Dict[str, Any]] = []
        for item in (context_docs_raw or []):
            if isinstance(item, dict):
                context_docs.append(item)
            else:
                context_docs.append({"text": str(item), "metadata": {}, "similarity_score": 0.0})

        # Sort by similarity score if available
        context_docs.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        context_text = "\n".join(doc['text'] for doc in context_docs)

        # Log relevant docs for debugging
        for doc in context_docs:
            logger.debug(f"Retrieved doc with score {doc.get('similarity_score', 0.0):.2f}: {doc['text'][:100]}...")

        q_lower = user_query.lower()

        # Password reset (high priority, multiple patterns)
        password_patterns = [
            "reset password", "forgot password", "change password", 
            "can't login", "locked out", "reset my password",
            "forgot my password", "change my password",
            "lost access", "access to account"
        ]
        if any(pattern in q_lower for pattern in password_patterns):
            resp = actions.reset_password(user_id or "")
            return {
                "intent": "reset_password",
                "response": resp,
                "source_docs": context_docs,
                "confidence": 0.99,
                "action_invoked": "reset_password"
            }

        # Ticket status checking
        if any(pattern in q_lower for pattern in ["ticket", "status", "progress", "update on ticket"]):
            ticket_id = _extract_ticket_id(user_query)
            if ticket_id:
                resp = actions.check_ticket_status(ticket_id)
                return {
                    "intent": "check_ticket_status",
                    "response": resp,
                    "source_docs": context_docs,
                    "confidence": 0.95,
                    "action_invoked": "check_ticket_status"
                }
            elif "ticket" in q_lower:
                # Explicitly about tickets but no ID found
                return {
                    "intent": "check_ticket_status",
                    "response": "Please provide your ticket ID number to check its status.",
                    "source_docs": context_docs,
                    "confidence": 0.8,
                    "action_invoked": None
                }

        # Summary generation with expanded patterns
        summary_patterns = ["summarize", "summary", "tldr", "brief overview", "key points"]
        if any(pattern in q_lower for pattern in summary_patterns):
            # Extract just the text from context docs for summarization
            docs_texts = [d['text'] for d in context_docs]
            resp = actions.generate_summary(docs_texts)
            return {
                "intent": "generate_summary",
                "response": resp,
                "source_docs": context_docs,
                "confidence": 0.9,
                "action_invoked": "generate_summary"
            }

        # Fallback: generate answer using LLM and retrieved context
        ai_answer = generate_response(user_query, context_text)
        return {
            "intent": "general_query",
            "response": ai_answer,
            "source_docs": context_docs,
            "confidence": 0.85,
            "action_invoked": None
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