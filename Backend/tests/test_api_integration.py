"""Test the FastAPI endpoints with async test client."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import mongomock
from typing import Dict, Any

# Fixtures for mocking dependencies
@pytest.fixture
def mock_mongo(monkeypatch):
    """Replace MongoDB with mock for testing."""
    from app.database import mongo_client
    
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["testdb"]
    mongo_client.chat_collection = mock_db["chats"]
    return mock_db["chats"]

@pytest.fixture
def client(mock_mongo):
    """Create test client with mocked dependencies."""
    from app.main import app
    return TestClient(app)

@pytest.fixture
def sample_queries() -> Dict[str, Dict[str, Any]]:
    """Sample queries and their expected results."""
    return {
        "password_reset": {
            "query": "I forgot my password",
            "expected_intent": "reset_password",
            "expected_action": "reset_password"
        },
        "ticket_status": {
            "query": "What's the status of ticket 123456?",
            "expected_intent": "check_ticket_status",
            "expected_action": "check_ticket_status"
        },
        "general_query": {
            "query": "What are the API rate limits?",
            "expected_intent": "general_query",
            "expected_action": None
        }
    }

def test_root_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "running successfully" in response.json()["message"].lower()

def test_ask_endpoint_responses(client, sample_queries, mock_mongo):
    """Test /api/ask with different query types."""
    for query_type, test_data in sample_queries.items():
        # Make request
        response = client.post("/api/ask", json={
            "user_id": "test_user",
            "query": test_data["query"]
        })
        
        # Check response
        assert response.status_code == 200, f"Failed on {query_type}"
        data = response.json()
        
        # Verify response structure
        assert "intent" in data
        assert "response" in data
        assert "confidence" in data
        assert "action_invoked" in data
        assert isinstance(data["source_docs"], list)
        
        # Check specific expectations if provided
        if "expected_intent" in test_data:
            assert data["intent"] == test_data["expected_intent"]
        if "expected_action" in test_data:
            assert data["action_invoked"] == test_data["expected_action"]
            
        # Verify chat was logged
        saved_chat = mock_mongo.find_one({
            "user_id": "test_user",
            "query": test_data["query"]
        })
        assert saved_chat is not None
        assert "created_at" in saved_chat
        assert isinstance(saved_chat["created_at"], datetime)

def test_ask_endpoint_invalid_requests(client):
    """Test /api/ask with invalid requests."""
    test_cases = [
        # Missing user_id
        ({"query": "test question"}, 422),
        # Missing query
        ({"user_id": "test_user"}, 422),
        # Empty query
        ({"user_id": "test_user", "query": ""}, 422),
        # Invalid types
        ({"user_id": 123, "query": "test"}, 422),
        ({"user_id": "test_user", "query": ["not a string"]}, 422),
    ]
    
    for payload, expected_status in test_cases:
        response = client.post("/api/ask", json=payload)
        assert response.status_code == expected_status

def test_chat_logging(client, mock_mongo):
    """Test that chats are properly logged with all fields."""
    payload = {
        "user_id": "test_user",
        "query": "I forgot my password"
    }
    
    # Make request
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 200
    
    # Check logged chat
    chat = mock_mongo.find_one({"user_id": "test_user"})
    assert chat is not None
    
    # Verify all expected fields
    assert "query" in chat
    assert "response" in chat
    assert "created_at" in chat
    assert "action_invoked" in chat
    assert "confidence" in chat
    assert isinstance(chat["created_at"], datetime)
    
    # Should match response
    data = response.json()
    assert chat["response"] == data["response"]
    assert chat["action_invoked"] == data["action_invoked"]
