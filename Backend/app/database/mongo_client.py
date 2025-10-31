"""MongoDB client for chat history logging."""
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import logging
from app.utils.config import settings
import os

logger = logging.getLogger(__name__)

# Flag to disable MongoDB in case of connection issues
MONGO_ENABLED = os.environ.get('MONGO_ENABLED', '1') == '1'

# Determine if we're running tests
IN_TEST = any('pytest' in arg for arg in sys.argv)

# Initialize with mock/empty values
client = None
db = None
chat_collection = None

def init_mongo():
    global client, db, chat_collection
    
    if not MONGO_ENABLED:
        logger.warning("MongoDB is disabled via MONGO_ENABLED environment variable")
        return False

    try:
        if IN_TEST:
            # Use in-memory mongomock for tests
            import mongomock
            client = mongomock.MongoClient()
            logger.info("Using in-memory MongoDB mock for tests")
        else:
            # Try DNS seed list connection string (mongodb+srv://)
            if not settings.MONGO_URI.startswith('mongodb+srv://'):
                # Convert standard URI to DNS SRV URI
                uri_parts = settings.MONGO_URI.replace('mongodb://', '').split('@')
                if len(uri_parts) == 2:
                    credentials, hosts = uri_parts
                    cluster = hosts.split('/')[0].split(',')[0]  # Get first host
                    base_domain = '.'.join(cluster.split('.')[1:])  # Get domain without first part
                    srv_uri = f'mongodb+srv://{credentials}@{base_domain}'
                    client = MongoClient(srv_uri, serverSelectionTimeoutMS=5000)
                else:
                    client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            else:
                client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
        db = client[settings.MONGO_DB_NAME]
        chat_collection = db["chats"]
        return True

    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        if IN_TEST:
            # In tests, fall back to mock
            import mongomock
            client = mongomock.MongoClient()
            db = client["testdb"]
            chat_collection = db["chats"]
            return True
        return False

# Try to initialize MongoDB, but don't fail if it doesn't work
mongo_available = init_mongo()

def save_chat(user_id: str, query: str, response: str, *, action_invoked: Optional[str] = None, confidence: Optional[float] = None, extra: Optional[Dict[str, Any]] = None):
    """Save chat message with metadata and timestamp.

    extra: optional dict for any additional metadata.
    """
    if not MONGO_ENABLED or not mongo_available:
        logger.warning("MongoDB is disabled or unavailable. Chat history will not be saved.")
        return

    try:
        chat_document = {
            "user_id": user_id,
            "query": query,
            "response": response,
            "action_invoked": action_invoked,
            "confidence": confidence,
            "extra": extra or {},
            "created_at": datetime.utcnow(),
        }
        if chat_collection is not None:
            chat_collection.insert_one(chat_document)
    except Exception as e:
        logger.error(f"Failed to save chat to MongoDB: {e}")
        # Continue execution even if MongoDB fails
