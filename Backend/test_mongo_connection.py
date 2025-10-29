from pymongo import MongoClient
from app.utils.config import settings

def test_connection():
    try:
        # Create a MongoDB client
        client = MongoClient(settings.MONGO_URI)
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas!")
        
        # Print database info
        db = client[settings.MONGO_DB_NAME]
        print(f"Connected to database: {settings.MONGO_DB_NAME}")
        print("Collections:", db.list_collection_names())
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_connection()