"""MongoDB client for chat history logging."""
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import logging
from app.utils.config import settings

logger = logging.getLogger(__name__)

# Determine if we're running tests
IN_TEST = any('pytest' in arg for arg in sys.argv)

try:
    if IN_TEST:
        # Use in-memory mongomock for tests
        import mongomock
        client = mongomock.MongoClient()
        logger.info("Using in-memory MongoDB mock for tests")
    else:
        # Real MongoDB connection
        client = MongoClient(settings.MONGO_URI)
        # Test connection
        client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
    db = client[settings.MONGO_DB_NAME]
    chat_collection: Collection = db["chats"]

except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    if not IN_TEST:
        raise  # Re-raise in production
    # In tests, fall back to mock
    import mongomock
    client = mongomock.MongoClient()
    db = client["testdb"]
    chat_collection = db["chats"]


def save_chat(user_id: str, query: str, response: str, *, action_invoked: Optional[str] = None, confidence: Optional[float] = None, extra: Optional[Dict[str, Any]] = None):
    """Save chat message with metadata and timestamp.

    extra: optional dict for any additional metadata.
    """
    chat_document = {
        "user_id": user_id,
        "query": query,
        "response": response,
        "action_invoked": action_invoked,
        "confidence": confidence,
        "extra": extra or {},
        "created_at": datetime.utcnow(),
    }
    chat_collection.insert_one(chat_document)
