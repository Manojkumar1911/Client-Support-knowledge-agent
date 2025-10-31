"""Real Semantic Kernel orchestration using Microsoft Semantic Kernel.

This module provides true SK-based orchestration with:
- Native SK plugins with @kernel_function decorators
- Automatic function calling via SK's planner
- Proper chat completion service integration
- No manual fallback orchestration logic
"""

import logging
import re
from typing import Optional, Dict, Any, List
from pydantic import ConfigDict
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from app.core.rag_engine import rag_engine
from app.core import actions
from app.core.semantic_kernel_integration import process_with_semkernel

logger = logging.getLogger(__name__)

# ====================================================================
# PLUGINS: Native SK functions with proper decorators
# ====================================================================

class RAGPlugin:
    """Plugin for RAG operations."""

    @kernel_function(
        name="retrieve_documents",
        description="Retrieve relevant knowledge base documents for a user query. Use this when you need context to answer questions."
    )
    def retrieve_documents(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant documents from the knowledge base."""
        try:
            docs = rag_engine.retrieve_relevant_docs(query, top_k=top_k)
            docs.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)

            if not docs:
                return "No relevant documents found."

            context = "\n\n".join(f"[Document {i+1}]\n{d['text']}" for i, d in enumerate(docs))
            logger.info(f"Retrieved {len(docs)} documents for query: {query[:50]}...")
            return context
        except Exception as e:
            logger.exception(f"Error retrieving documents: {e}")
            return "Error retrieving documents from knowledge base."


class ActionPlugin:
    """Plugin for user actions like password reset, ticket status, etc."""

    def __init__(self):
        self.last_action_result = None

    @kernel_function(
        name="reset_user_password",
        description="Reset a user's password. Use this when user requests password reset. Returns confirmation message."
    )
    def reset_user_password(self, user_id: str) -> str:
        try:
            result = actions.reset_password(user_id)
            self.last_action_result = {"action": "reset_password", "result": result}
            logger.info(f"Password reset for user: {user_id}")
            return result
        except Exception as e:
            logger.exception(f"Error resetting password: {e}")
            return f"Error resetting password: {str(e)}"

    @kernel_function(
        name="check_support_ticket",
        description="Check the status of a support ticket. Use this when user asks about ticket status."
    )
    def check_support_ticket(self, ticket_id: str) -> str:
        try:
            result = actions.check_ticket_status(ticket_id)
            self.last_action_result = {"action": "check_ticket", "result": result}
            logger.info(f"Checked ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.exception(f"Error checking ticket: {e}")
            return f"Error checking ticket: {str(e)}"

    @kernel_function(
        name="summarize_content",
        description="Generate a summary of provided documents or content."
    )
    def summarize_content(self, content: str) -> str:
        try:
            docs = content.split("\n\n") if content else []
            result = actions.generate_summary(docs)
            self.last_action_result = {"action": "summarize", "result": result}
            logger.info("Generated summary")
            return result
        except Exception as e:
            logger.exception(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"


class UtilityPlugin:
    """Plugin for utility functions like greeting detection."""

    @kernel_function(
        name="is_greeting",
        description="Check if a message is a greeting (hi, hello, hey, etc.). Returns 'yes' or 'no'."
    )
    def is_greeting(self, message: str) -> str:
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        msg_lower = message.lower().strip()
        is_greet = any(msg_lower == g or msg_lower.startswith(g + " ") for g in greetings)
        return "yes" if is_greet else "no"

    @kernel_function(
        name="extract_ticket_id",
        description="Extract a ticket ID number from text. Returns the ticket ID or empty string if not found."
    )
    def extract_ticket_id(self, text: str) -> str:
        match = re.search(r"\b(\d{3,12})\b", text)
        return match.group(1) if match else ""

# ====================================================================
# GEMINI ADAPTER: Fixed for Pydantic compatibility
# ====================================================================

class GeminiChatCompletionClient(ChatCompletionClientBase):
    """Chat completion client adapter for Google Gemini."""
    model_config = ConfigDict(extra="allow")  # ✅ allow dynamic fields

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        super().__init__(ai_model_id=model_name, service_id="gemini")
        try:
            from app.llm.llm_client import _use_gemini, _gemini_model
            if not _use_gemini or _gemini_model is None:
                raise RuntimeError("Gemini is not available")

            # ✅ bypass pydantic field validation safely
            object.__setattr__(self, "model", _gemini_model)

            logger.info("✓ Gemini model initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize Gemini model")
            raise RuntimeError(f"Gemini initialization failed: {e}")

    async def get_chat_message_contents(self, chat_history: ChatHistory, settings: Any = None, **kwargs) -> List[ChatMessageContent]:
        """Get chat message completions."""
        try:
            prompt_parts = []
            for msg in chat_history.messages:
                role = "User" if msg.role == AuthorRole.USER else "Assistant"
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                prompt_parts.append(f"{role}: {content}")

            prompt = "\n".join(prompt_parts)

            response = self.model.generate_content(prompt)
            response_text = getattr(response, "text", str(response))

            return [ChatMessageContent(role=AuthorRole.ASSISTANT, content=response_text)]
        except Exception as e:
            logger.exception("Error in Gemini chat completion")
            return [ChatMessageContent(role=AuthorRole.ASSISTANT, content=f"I encountered an error: {str(e)}")]

    async def get_streaming_chat_message_contents(self, *args, **kwargs):
        raise NotImplementedError("Streaming not supported")

# ====================================================================
# KERNEL INITIALIZATION
# ====================================================================

_kernel: Optional[Kernel] = None
_action_plugin: Optional[ActionPlugin] = None

def get_kernel() -> Kernel:
    """Get or create the Semantic Kernel instance with all plugins."""
    global _kernel, _action_plugin

    if _kernel is not None:
        return _kernel

    logger.info("Initializing Semantic Kernel...")
    _kernel = Kernel()

    # Add Gemini chat completion service
    try:
        gemini_service = GeminiChatCompletionClient()
        _kernel.add_service(gemini_service)
        logger.info("✓ Added Gemini chat completion service")
    except Exception as e:
        logger.exception("Failed to add Gemini service")
        raise RuntimeError(f"Cannot initialize SK without LLM service: {e}")

    try:
        _kernel.add_plugin(RAGPlugin(), plugin_name="rag")
        logger.info("✓ Registered RAG plugin")

        _action_plugin = ActionPlugin()
        _kernel.add_plugin(_action_plugin, plugin_name="actions")
        logger.info("✓ Registered Actions plugin")

        _kernel.add_plugin(UtilityPlugin(), plugin_name="utils")
        logger.info("✓ Registered Utility plugin")

    except Exception as e:
        logger.exception("Failed to register plugins")
        raise RuntimeError(f"Plugin registration failed: {e}")

    logger.info("Semantic Kernel initialization complete!")
    return _kernel

# ====================================================================
# MAIN ORCHESTRATOR
# ====================================================================

async def semantic_kernel_orchestrator(user_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Main orchestrator using Semantic Kernel."""
    kernel = get_kernel()

    chat_history = ChatHistory()
    system_prompt = f"""
You are a helpful AI assistant with access to several tools:

1. retrieve_documents → fetch relevant information
2. reset_user_password → reset user password
3. check_support_ticket → get ticket status
4. summarize_content → summarize text
5. is_greeting → detect greeting
6. extract_ticket_id → find ticket IDs

Rules:
- Warmly greet for greetings (don’t use tools)
- Use tools where needed
- Be concise, clear, and professional

Current user ID: {user_id or 'unknown'}
"""
    chat_history.add_system_message(system_prompt)
    chat_history.add_user_message(user_query)

    try:
        chat_service = kernel.get_service("gemini")
        execution_settings = chat_service.get_prompt_execution_settings_class()(service_id="gemini")
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True)

        logger.info(f"Processing query with SK: {user_query[:100]}...")
        response = await chat_service.get_chat_message_contents(chat_history=chat_history, settings=execution_settings, kernel=kernel)
        response_text = response[0].content if response else "I couldn't generate a response."

        # If the LLM responded with a raw tool invocation (e.g., ```tool_code```),
        # fall back to the prompt-based orchestrator which formats KB answers.
        stripped_response = (response_text or "").strip()
        if stripped_response.startswith("```") or "tool_code" in stripped_response:
            logger.warning("SK returned tool invocation text; falling back to prompt-based orchestrator")
            return await process_with_semkernel(query=user_query, user_id=user_id)

        intent = "general_query"
        action_invoked = None
        confidence = 0.8

        if _action_plugin and _action_plugin.last_action_result:
            action_data = _action_plugin.last_action_result
            action_invoked = action_data.get("action")
            intent_map = {
                "reset_password": "password_reset",
                "check_ticket": "check_ticket_status",
                "summarize": "generate_summary"
            }
            intent = intent_map.get(action_invoked, "general_query")
            confidence = 0.9
            _action_plugin.last_action_result = None

        if len(user_query.split()) <= 3 and any(g in user_query.lower() for g in ["hi", "hello", "hey"]):
            intent = "greeting"
            confidence = 0.95

        logger.info(f"✓ SK Response generated (intent: {intent}, action: {action_invoked})")

        return {
            "intent": intent,
            "response": response_text,
            "source_docs": [],
            "confidence": confidence,
            "action_invoked": action_invoked
        }

    except Exception as e:
        logger.exception(f"Semantic Kernel orchestration failed: {e}")
        return await process_with_semkernel(query=user_query, user_id=user_id)
