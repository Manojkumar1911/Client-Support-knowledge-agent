import asyncio
from Backend.app.core.semantic_kernel_orchestrator import process_query
from app.database.mongo_client import save_chat
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_integration():
    # Test cases
    test_queries = [
        "Hi there!",  # Test greeting
        "How do I reset my password?",  # Test knowledge base query
        "What's the process for updating billing information?",  # Test another knowledge query
    ]
    
    for query in test_queries:
        logger.info(f"\nTesting query: {query}")
        try:
            # Process with semantic kernel
            result = await process_query(query, "test_user")
            
            # Log to MongoDB
            save_chat(
                user_id="test_user",
                query=query,
                response=result.response,
                action_invoked=result.action,
                confidence=result.confidence
            )
            
            logger.info(f"Response: {result.response}")
            logger.info(f"Action: {result.action}")
            logger.info(f"Confidence: {result.confidence}")
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(test_integration())