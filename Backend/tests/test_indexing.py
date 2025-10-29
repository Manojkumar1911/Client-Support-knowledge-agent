"""Test knowledge base loading and chunking."""
from pathlib import Path
from app.utils.build_index import (
    load_knowledge_base,
    chunk_text,
    build_chroma_index,
    KB_PATH
)

def test_kb_file_exists():
    """Test that knowledge base file exists and is readable."""
    assert KB_PATH.exists()
    assert KB_PATH.is_file()
    
def test_load_knowledge_base():
    """Test loading the knowledge base text."""
    kb_text = load_knowledge_base()
    assert isinstance(kb_text, str)
    assert len(kb_text) > 100  # Should have meaningful content
    
def test_chunk_text():
    """Test text chunking with overlap."""
    sample = """First paragraph about metrics and monitoring.
    
    Second paragraph about authentication and security.
    
    Third paragraph about API rate limits."""
    
    chunks = chunk_text(sample, chunk_size=50, overlap=10)
    assert len(chunks) >= 3
    # Check overlap
    assert any(c1.strip() and c2.strip() and 
              (c1[-10:].strip() in c2 or c2[:10].strip() in c1)
              for c1, c2 in zip(chunks, chunks[1:]))
    
def test_build_index():
    """Test building the ChromaDB index."""
    # Small test content
    chunks = [
        "How to reset your password",
        "API rate limits and quotas",
        "Authentication and security best practices"
    ]
    
    build_chroma_index(chunks)
    
    # Import here to avoid circular import in main code
    from app.core.rag_engine import rag_engine
    
    # Verify chunks were indexed
    stats = rag_engine.get_collection_stats()
    assert stats["document_count"] >= len(chunks)
    
    # Test retrieval
    results = rag_engine.retrieve_relevant_docs("reset password")
    assert len(results) > 0
    assert any("reset" in doc["text"].lower() for doc in results)