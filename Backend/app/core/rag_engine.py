import logging
from typing import List, Optional
try:
    import chromadb
    from chromadb.api.models.Collection import Collection
except Exception:
    chromadb = None
    Collection = None
from app.utils.config import Config
from app.llm.llm_client import get_embeddings

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        # Use a generic object type for collection to avoid import-time typing issues
        self.collection: Optional[object] = None
        self._initialize_chroma()

    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Use PersistentClient for local persistent storage
            client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
            logger.info(f"Using local Chroma with persistent storage at: {Config.CHROMA_DIR}")
            self.collection = client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "Support knowledge base"}
            )
        except Exception as exc:
            # If ChromaDB is unavailable or initialization fails, fall back to an
            # in-memory collection implementation so the system remains usable
            logger.exception("Failed to initialize Chroma client: %s", exc)
            logger.warning("Falling back to in-memory collection. This is not persistent and intended for dev/testing.")

            class InMemoryCollection:
                def __init__(self):
                    self._docs = {}
                    self.name = "inmemory_knowledge_base"
                    self.metadata = {"description": "In-memory fallback collection"}

                def add(self, documents, ids, embeddings=None, metadatas=None):
                    for i, (_id, doc) in enumerate(zip(ids, documents)):
                        self._docs[_id] = doc

                def query(self, query_embeddings=None, n_results=3, include=None):
                    # Very naïve retrieval: return first n_results documents
                    docs = list(self._docs.values())[:n_results]
                    metadatas = [{} for _ in docs]
                    distances = [0.0 for _ in docs]
                    return {"documents": [docs], "metadatas": [metadatas], "distances": [distances]}

                def count(self):
                    return len(self._docs)

            self.collection = InMemoryCollection()

    def add_document(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> None:
        """Add a new document to the knowledge base.

        Args:
            doc_id: Unique identifier for the document
            text: The document text
            metadata: Optional metadata about the document
        """
        try:
            if not text.strip():
                logger.warning(f"Skipping empty document: {doc_id}")
                return

            embedding = get_embeddings([text])[0]
            self.collection.add(
                documents=[text],
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata or {}]
            )
            logger.debug(f"Successfully added document: {doc_id}")
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            raise

    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[dict]:
        """Retrieve relevant document chunks for a query.
        
        Args:
            query: The user's question
            top_k: Number of relevant chunks to return
            
        Returns:
            List of dicts containing document text and metadata
        """
        try:
            query_embedding = get_embeddings([query])[0]
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['metadatas', 'distances', 'documents']
            )

            # Combine results into a list of dicts
            docs = []
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    'text': doc,
                    'metadata': results["metadatas"][0][i],
                    'similarity_score': max(0.0, 1 - abs(results["distances"][0][i]))  # Convert distance to similarity and ensure non-negative
                })
            return docs

        except Exception as e:
            logger.error(f"Error retrieving docs: {e}")
            return []

    def get_collection_stats(self) -> dict:
        """Get statistics about the knowledge base collection."""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection.name,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

# Initialize global RAG engine instance
rag_engine = RAGEngine()