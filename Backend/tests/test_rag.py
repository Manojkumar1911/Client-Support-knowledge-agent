import pytest
from typing import List, Dict, Any

class DummyCollection:
    def __init__(self):
        self.docs = {}
        self.metadata = {}
        self.name = "test_collection"
        self.metadata = {"description": "Test collection"}

    def add(self, documents: List[str], ids: List[str], embeddings=None, metadatas=None):
        for i, (_id, doc) in enumerate(zip(ids, documents)):
            self.docs[_id] = doc
            self.metadata[_id] = metadatas[i] if metadatas else {}

    def query(self, query_embeddings=None, n_results=3, include=None) -> Dict[str, Any]:
        # Simulate basic retrieval - in reality would use embeddings
        documents = list(self.docs.values())[:n_results]
        metadatas = list(self.metadata.values())[:n_results]
        
        # Add fake distances
        distances = [0.1 * i for i in range(len(documents))]
        
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }
    
    def count(self) -> int:
        return len(self.docs)


@pytest.fixture
def mock_rag_engine(monkeypatch):
    """Create a RAG engine with mocked ChromaDB collection."""
    from app.core.rag_engine import RAGEngine
    
    # Create RAG engine instance
    engine = RAGEngine()
    
    # Replace collection with dummy
    engine.collection = DummyCollection()
    
    return engine


def test_add_document_with_metadata(mock_rag_engine):
    """Test adding a document with metadata."""
    doc_text = "How to reset dashboard metrics"
    metadata = {"source": "kb.txt", "section": "metrics"}
    
    mock_rag_engine.add_document("doc1", doc_text, metadata)
    
    # Get collection stats
    stats = mock_rag_engine.get_collection_stats()
    assert stats["document_count"] == 1


def test_retrieve_docs_with_scores(mock_rag_engine):
    """Test retrieving documents with similarity scores."""
    # Add test documents
    mock_rag_engine.add_document("doc1", "How to reset dashboard metrics")
    mock_rag_engine.add_document("doc2", "Understanding API rate limits")
    
    # Retrieve docs
    results = mock_rag_engine.retrieve_relevant_docs("reset metrics", top_k=2)
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Check result structure
    first_result = results[0]
    assert "text" in first_result
    assert "metadata" in first_result
    assert "similarity_score" in first_result
    
    # Check text content
    assert any("reset dashboard metrics" in d["text"].lower() for d in results)
