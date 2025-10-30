from pymongo import MongoClient
from app.utils.config import settings

def test_connection():
    try:
        # Try DNS seed list connection string (mongodb+srv://)
        if not settings.MONGO_URI.startswith('mongodb+srv://'):
            # Convert standard URI to DNS SRV URI
            uri_parts = settings.MONGO_URI.replace('mongodb://', '').split('@')
            if len(uri_parts) == 2:
                credentials, hosts = uri_parts
                cluster = hosts.split('/')[0].split(',')[0]  # Get first host
                base_domain = '.'.join(cluster.split('.')[1:])  # Get domain without first part
                srv_uri = f'mongodb+srv://{credentials}@{base_domain}'
                client = MongoClient(srv_uri)
            else:
                client = MongoClient(settings.MONGO_URI)
        else:
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