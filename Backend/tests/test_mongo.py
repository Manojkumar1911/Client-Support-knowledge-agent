"""Test MongoDB connection and chat logging."""
import pytest
from datetime import datetime, timedelta
from app.database.mongo_client import save_chat, chat_collection

@pytest.fixture
def cleanup_test_chats():
    """Remove test chats before and after test."""
    # Remove any existing test chats
    chat_collection.delete_many({"user_id": "test_user"})
    yield
    # Cleanup after test
    chat_collection.delete_many({"user_id": "test_user"})

def test_mongo_connection(cleanup_test_chats):
    """Test MongoDB connection and basic operations."""
    # Save a test chat
    test_chat = {
        "user_id": "test_user",
        "query": "Test query",
        "response": "Test response",
        "confidence": 0.95,
        "action_invoked": None
    }
    
    # Save chat using our utility
    save_chat(**test_chat)
    
    # Verify it was saved
    saved = chat_collection.find_one({
        "user_id": "test_user",
        "query": "Test query"
    })
    
    assert saved is not None
    assert saved["response"] == "Test response"
    assert saved["confidence"] == 0.95
    assert "created_at" in saved
    
    # Verify timestamp is recent
    assert datetime.utcnow() - saved["created_at"] < timedelta(minutes=1)