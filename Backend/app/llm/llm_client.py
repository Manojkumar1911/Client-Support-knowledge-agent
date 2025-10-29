"""LLM client helpers: embeddings + generation with Gemini and safe fallback."""
from typing import List
import logging

logger = logging.getLogger(__name__)

from app.utils.config import Config

# Try to set up embeddings model
try:
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    logger.warning("Failed to load sentence-transformers embedder: %s", e)
    _embedder = None

# Try to configure Gemini (google-generativeai). If unavailable or API key not set,
# we'll fall back to a simple template-based responder.
_use_gemini = False
_gemini_model = None
try:
    if Config.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        _use_gemini = True
        logger.info("Gemini model configured for generation.")
except Exception as e:
    logger.warning("Gemini not available or failed to configure: %s", e)
    _use_gemini = False


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of texts. Falls back to simple hashing if embedder missing."""
    if not texts:
        return []

    if _embedder is None:
        # Fallback: use a very small deterministic pseudo-embedding (not suitable for real RAG)
        logger.debug("Using fallback embeddings (not semantic).")
        embeddings = []
        for t in texts:
            # simple feature: length and sum of char codes normalized
            s = sum(ord(c) for c in t[:256])
            embeddings.append([float((s % 1000) / 1000.0)])
        return embeddings

    try:
        arr = _embedder.encode(texts, convert_to_numpy=True)
        # Ensure lists for downstream callers
        return arr.tolist()
    except Exception as e:
        logger.error("Error generating embeddings: %s", e)
        # As fallback, return the simple pseudo-embeddings
        return get_embeddings(texts)


def generate_response(prompt: str, context: str = "") -> str:
    """Generate an answer for prompt using Gemini if available, otherwise fallback.

    The function returns plain text.
    """
    full_prompt = f"Context:\n{context}\n\nUser Query:\n{prompt}"

    if _use_gemini and _gemini_model is not None:
        try:
            resp = _gemini_model.generate_content(full_prompt)
            # genai responses may carry .text or structured content
            text = getattr(resp, "text", None) or str(resp)
            return text
        except Exception as e:
            logger.warning("Gemini generation failed: %s", e)

    # Fallback generator: concise templated reply that references context
    try:
        if context:
            snippet = context[:800]
            return f"Based on the context: {snippet}...\n\nAnswer: {prompt} (This is a fallback response; enable Gemini for a richer answer.)"
        else:
            return f"I don't have access to the hosted LLM right now. Here's a short reply: {prompt}"
    except Exception as e:
        logger.error("Fallback generation failed: %s", e)
        return "Sorry, I couldn't generate a response at this time."
