"""Utility to build and maintain the ChromaDB knowledge base index."""

import os
from pathlib import Path
from typing import List
import chromadb
from sentence_transformers import SentenceTransformer
from app.utils.config import Config

# Constants
CHUNK_SIZE = 500  # characters per chunk
OVERLAP = 50      # character overlap between chunks
KB_PATH = Path(__file__).parents[1] / "kb" / "kb.txt"
CHROMA_INDEX_PATH = Path(__file__).parents[1] / "kb" / "chroma_index"


def load_knowledge_base() -> str:
    """Load the knowledge base text file."""
    with open(KB_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        # Find the end of this chunk
        end = start + chunk_size
        
        # If not at the end of the text, try to break at a sentence or paragraph
        if end < text_len:
            # Look for a good breaking point
            break_chars = ['\n\n', '. ', '? ', '! ']
            best_break = end
            
            for char in break_chars:
                # Look for break char in the overlap region
                pos = text[end-overlap:end+overlap].find(char)
                if pos != -1:
                    best_break = end - overlap + pos + len(char)
                    break
            
            end = best_break

        # Add this chunk
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)

        # Move to next chunk, accounting for overlap
        start = end - overlap if end < text_len else text_len

    return chunks


def build_chroma_index(chunks: List[str]) -> None:
    """Build ChromaDB index from text chunks."""
    from app.core.rag_engine import rag_engine
    try:
        # Try to clear existing documents (defensive: not all collection implementations support get/delete)
        try:
            if hasattr(rag_engine.collection, 'get') and callable(rag_engine.collection.get):
                results = rag_engine.collection.get()
                # results format from Chroma usually contains an 'ids' list
                ids = []
                if isinstance(results, dict) and 'ids' in results:
                    ids = results.get('ids') or []
                # Some collection implementations may return list of dicts; be defensive
                if not ids and isinstance(results, list):
                    # try to extract ids from items
                    try:
                        ids = [item.get('id') for item in results if isinstance(item, dict) and 'id' in item]
                    except Exception:
                        ids = []

                if ids:
                    # Delete all existing documents by id
                    if hasattr(rag_engine.collection, 'delete') and callable(rag_engine.collection.delete):
                        rag_engine.collection.delete(ids=ids)
                        print(f"Cleared {len(ids)} existing documents")
        except Exception as e:
            # Non-fatal: continue to rebuild index
            print(f"Warning: Could not clear existing documents: {e}")

        # Add documents with metadata
        for i, chunk in enumerate(chunks):
            rag_engine.add_document(
                doc_id=f"chunk_{i}",
                text=chunk,
                metadata={
                    "source": "kb.txt",
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )

        # Log collection stats
        stats = rag_engine.get_collection_stats()
        print(f"✅ Built index with {stats.get('document_count', 0)} chunks")
    except Exception as e:
        print(f"❌ Error building index: {e}")
        raise


def rebuild_index():
    """Rebuild the entire knowledge base index."""
    # Load and chunk the knowledge base
    kb_text = load_knowledge_base()
    chunks = chunk_text(kb_text)
    
    # Build the index
    build_chroma_index(chunks)


if __name__ == "__main__":
    rebuild_index()