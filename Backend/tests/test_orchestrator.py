"""Test the semantic kernel orchestrator with all intent paths."""
import pytest
from typing import Dict, Any

from Backend.app.core import semantic_kernel_orchestrator as orchestrator
from app.llm import llm_client
from app.core.rag_engine import rag_engine


@pytest.fixture
def mock_rag_docs(monkeypatch):
    """Mock RAG to return predictable docs."""
    docs = [
        {
            "text": "To reset your password, click the 'Forgot Password' link on the login page.",
            "metadata": {"source": "kb.txt"},
            "similarity_score": 0.95
        },
        {
            "text": "API rate limits are 1000 requests per hour for Pro plan.",
            "metadata": {"source": "kb.txt"},
            "similarity_score": 0.85
        }
    ]
    monkeypatch.setattr(orchestrator, "retrieve_relevant_docs", lambda q, top_k=3: docs)
    return docs


@pytest.fixture
def mock_llm(monkeypatch):
    """Mock LLM to return predictable responses."""
    def mock_generate(prompt: str, context: str = "") -> str:
        return f"Based on the context: {context[:50]}..."
    monkeypatch.setattr(llm_client, "generate_response", mock_generate)


def test_reset_password_intent(mock_rag_docs, mock_llm):
    """Test password reset intent detection and handling."""
    queries = [
        "I forgot my password",
        "How do I reset my password?",
        "Need to change password",
        "Lost access to account"
    ]
    
    for q in queries:
        res = orchestrator.semantic_kernel_orchestrator(q, user_id="test_user")
        assert res["intent"] == "reset_password", f"Failed on query: {q}"
        assert res["action_invoked"] == "reset_password"
        assert res["confidence"] > 0.9
        assert "reset" in res["response"].lower()


def test_ticket_intent_with_id(mock_rag_docs, mock_llm):
    """Test ticket status checking with valid ticket ID."""
    res = orchestrator.semantic_kernel_orchestrator(
        "What's the status of ticket 123456?",
        user_id="test_user"
    )
    assert res["intent"] == "check_ticket_status"
    assert res["action_invoked"] == "check_ticket_status"
    assert "123456" in res["response"]


def test_summarize_intent(mock_rag_docs, mock_llm):
    """Test document summarization intent."""
    res = orchestrator.semantic_kernel_orchestrator(
        "Can you summarize the documentation about rate limits?",
        user_id="test_user"
    )
    assert res["intent"] == "generate_summary"
    assert res["action_invoked"] == "generate_summary"
    assert any(d["text"] in res["response"] for d in mock_rag_docs)


def test_general_query_intent(mock_rag_docs, mock_llm):
    """Test general query handling with LLM."""
    res = orchestrator.semantic_kernel_orchestrator(
        "How do API rate limits work?",
        user_id="test_user"
    )
    assert res["intent"] == "general_query"
    assert res["action_invoked"] is None
    assert res["confidence"] > 0.8
    assert "Based on the context" in res["response"]


def test_error_handling(monkeypatch):
    """Test error handling when things go wrong."""
    def raise_error(*args, **kwargs):
        raise Exception("Simulated error")
    
    # Make everything fail
    monkeypatch.setattr(orchestrator, "retrieve_relevant_docs", raise_error)
    monkeypatch.setattr(llm_client, "generate_response", raise_error)
    
    res = orchestrator.semantic_kernel_orchestrator(
        "This should trigger error handling",
        user_id="test_user"
    )
    assert res["intent"] == "error"
    assert res["confidence"] == 0.0
    assert "sorry" in res["response"].lower()
    assert not res["source_docs"]