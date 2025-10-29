"""Tests for the semantic kernel agent with improved intent detection and response formatting."""
import pytest
from app.core.semantic_kernel_agent import semantic_kernel_orchestrator
from app.llm.llm_client import is_greeting, parse_intent_response

# Test greeting detection
@pytest.mark.parametrize("text,expected", [
    ("hi there", True),
    ("hello, how are you?", True),
    ("good morning", True),
    ("I need help with my password", False),
    ("what are your pricing plans?", False),
])
def test_greeting_detection(text, expected):
    assert is_greeting(text) == expected

# Test intent response parsing
@pytest.mark.parametrize("response,expected", [
    ("greeting (1.0)", ("greeting", 1.0)),
    ("password_reset (0.95)", ("password_reset", 0.95)),
    ("invalid response", ("general_query", 0.5)),  # fallback case
])
def test_intent_parsing(response, expected):
    intent, confidence = parse_intent_response(response)
    assert intent == expected[0]
    assert confidence == expected[1]

# Test full orchestrator with different query types
@pytest.mark.asyncio
async def test_greeting_query():
    result = await semantic_kernel_orchestrator("hi there")
    assert result["intent"] == "greeting"
    assert result["confidence"] > 0.9
    assert len(result["source_docs"]) == 0  # No context needed for greetings
    assert "help" in result["response"].lower()  # Should mention being helpful

@pytest.mark.asyncio
async def test_password_reset_query():
    result = await semantic_kernel_orchestrator("I need to reset my password")
    assert result["intent"] == "password_reset"
    assert result["confidence"] > 0.8
    assert len(result["source_docs"]) > 0  # Should have context
    assert "Sources:" in result["response"]  # Should include sources section

@pytest.mark.asyncio
async def test_general_query():
    result = await semantic_kernel_orchestrator("what are your pricing plans?")
    assert result["intent"] in ["billing_inquiry", "general_query"]
    assert result["confidence"] > 0
    assert len(result["source_docs"]) > 0
    # Check response formatting
    response = result["response"]
    assert any(marker in response for marker in ["Summary:", "•", "Sources:"])

# Test error handling
@pytest.mark.asyncio
async def test_error_handling():
    # Test with empty query
    result = await semantic_kernel_orchestrator("")
    assert result["intent"] in ["error", "unknown", "no_intent", "general_query"]  # Accept any error-like state
    assert result["confidence"] <= 0.5  # Low confidence for error states
    assert any(marker in result["response"].lower() for marker in ["sorry", "try again", "couldn't process"])
    
    # Test with very long query
    result = await semantic_kernel_orchestrator("x" * 10000)
    assert result["confidence"] <= 0.5
    assert any(marker in result["response"].lower() for marker in ["sorry", "try again", "couldn't process"])