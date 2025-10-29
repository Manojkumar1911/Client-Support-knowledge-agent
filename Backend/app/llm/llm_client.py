"""LLM client helpers: embeddings + generation with Gemini and safe fallback."""
from typing import List, Optional, Dict, Any, Tuple
import logging
import re

logger = logging.getLogger(__name__)

from app.utils.config import Config

# Intent classification prompt with few-shot examples
INTENT_PROMPT = """You are an AI support assistant classifying user queries into intents. Return ONLY the intent and confidence, no other text.

Examples:
Q: hi there
Intent: greeting (1.0)

Q: hello, how are you?
Intent: greeting (1.0)

Q: I need to reset my password
Intent: password_reset (0.95)

Q: what are your pricing plans?
Intent: billing_inquiry (0.9)

Q: how do I create an API key?
Intent: api_help (0.85)

Q: I'm having trouble with authentication
Intent: auth_issue (0.8)

Q: the model is giving wrong results
Intent: model_issue (0.75)

Now classify this query:
Q: {query}"""

# Response generation prompt
FINAL_RESPONSE_PROMPT = """
You are InextLabs' friendly AI Support Assistant.

Your goal: Give the user a clear, natural, and easy-to-understand answer — like how a real human support expert would explain it, not robotic or over-technical.

Tone:
- Be friendly, confident, and conversational.
- Use short sentences and simple phrasing.
- Avoid jargon unless necessary, and explain any technical terms in plain language.

Response Structure:
1️⃣ **Start with a short summary (1–2 sentences)** clearly explaining the main answer.
2️⃣ **Then list up to 3 bullet points** — each with the most relevant or actionable information. Write them naturally, not like documentation.
3️⃣ **End with "Sources:"** listing the top document titles, sections, or KB IDs used (if any).
4️⃣ If an "Action Result" is passed (like password reset info), include it before the summary under **Action Result:**.

Important:
- Make the response helpful and engaging.
- Avoid robotic words like "according to the context" or "based on the documents".
- Instead, say things like "Here's what you can do" or "Here's how it works".

Context:
{context}

User Question:
{user_query}
"""

# Greeting response prompt (shorter and more casual)
GREETING_PROMPT = """
You are InextLabs' friendly AI Support Assistant responding to a greeting.

Keep your response:
- Warm and welcoming
- Short (1-2 sentences)
- Include a brief mention that you're here to help with support questions
- Natural and conversational

User's greeting: {greeting}
"""

def is_greeting(text: str) -> bool:
    """Rule-based greeting detection. Returns True if text appears to be a greeting."""
    # Normalize text: lowercase, remove punctuation
    text = re.sub(r'[^\w\s]', '', text.lower().strip())
    
    # Common greeting patterns
    greetings = {
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
        'morning', 'afternoon', 'evening', 'hola', 'greetings'
    }
    
    # Check if any word or phrase matches greetings
    return any(g in text for g in greetings)

def parse_intent_response(text: str) -> Tuple[str, float]:
    """Parse intent and confidence from LLM classification response."""
    try:
        # Extract "intent_name (confidence)" pattern
        match = re.search(r'(\w+)\s*\(([0-9.]+)\)', text)
        if match:
            intent, confidence = match.groups()
            return intent.strip(), float(confidence)
    except Exception as e:
        logger.warning(f"Failed to parse intent response: {e}")
    
    # Fallback: return generic intent with low confidence
    return "general_query", 0.5

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


async def classify_intent(query: str) -> Tuple[str, float]:
    """Classify query intent using LLM. Returns (intent, confidence)."""
    # Handle empty queries
    if not query.strip():
        return "no_intent", 0.1
        
    # First check for greetings with rule-based detection
    if is_greeting(query):
        return "greeting", 1.0
        
    # Use LLM for more complex intent classification
    try:
        if _use_gemini and _gemini_model is not None:
            full_prompt = INTENT_PROMPT.format(query=query)
            resp = _gemini_model.generate_content(full_prompt)
            text = getattr(resp, "text", None) or str(resp)
            return parse_intent_response(text)
    except Exception as e:
        logger.warning(f"Intent classification failed: {e}")
    
    # Very long queries might be problematic
    if len(query) > 1000:
        return "error", 0.3
        
    # Default fallback
    return "general_query", 0.5

def generate_response(prompt: str, context: str = "", intent: str = "general_query", action_result: str = "") -> str:
    """Generate an answer for prompt using Gemini if available, otherwise fallback.
    
    Args:
        prompt: User's question
        context: Retrieved context documents
        intent: Classified intent (e.g., "greeting", "password_reset")
        action_result: Optional result from any action taken (e.g., password reset confirmation)
    
    Returns:
        Formatted response text
    """
    if _use_gemini and _gemini_model is not None:
        try:
            if intent == "greeting":
                # Use shorter greeting prompt
                full_prompt = GREETING_PROMPT.format(greeting=prompt)
            else:
                # Use full response prompt with context
                full_prompt = FINAL_RESPONSE_PROMPT.format(
                    context=context,
                    user_query=prompt,
                    action_result=action_result if action_result else ""
                )
            
            resp = _gemini_model.generate_content(full_prompt)
            # genai responses may carry .text or structured content
            text = getattr(resp, "text", None) or str(resp)
            return text
        except Exception as e:
            logger.warning("Gemini generation failed: %s", e)
            # Fall through to fallback

    # Fallback generator: use template-based response
    try:
        if intent == "greeting":
            return "Hello! I'm here to help with your support questions. What can I assist you with?"
        
        if intent in ["error", "unknown", "no_intent"] or not prompt.strip():
            return """Summary: I apologize, but I couldn't process your request properly.

• Please try asking your question again
• Make sure your question is clear and complete
• If the problem persists, contact our support team

Sources: Error handling system"""
            
        # For other intents, format a structured response
        parts = []
        
        # 1. Action Result (if any)
        if action_result:
            parts.append(f"Action Result: {action_result}")
        
        # 2. Summary section
        if context:
            # Extract most relevant part of context
            snippet = context[:800]
            parts.append(f"Summary: {snippet[:200]}...")
        else:
            parts.append("Summary: I don't have specific information about that, but I'll try to help.")
        
        # 3. Bullet points from context or fallback
        if context:
            # Create bullet points from context
            lines = [line.strip() for line in context.split('\n') if line.strip()]
            bullet_points = []
            
            for line in lines:
                if len(line) > 10 and len(bullet_points) < 3:
                    bullet_points.append(f"• {line}")
            
            if bullet_points:
                parts.append("\n".join(bullet_points))
        else:
            parts.append("• Please try to rephrase your question\n• Check our documentation for more details")
        
        # 4. Sources section
        if context:
            parts.append("Sources: Support knowledge base" + 
                (" (Note: Using fallback system due to LLM unavailability)" if not _use_gemini else ""))
        else:
            parts.append("Sources: Fallback system")
        
        # Combine all parts with double newlines
        return "\n\n".join(parts)
            
    except Exception as e:
        logger.error("Fallback generation failed: %s", e)
        return """Summary: I encountered an error while processing your request.

• Please try again in a moment
• If this persists, contact our support team
• You can also check our documentation for immediate help

Sources: Error handling system"""
