"""Semantic Kernel integration using Microsoft Semantic Kernel and a Gemini adapter.

This module registers a lightweight text completion service that forwards prompts
to the existing Gemini wrapper in `app.llm.llm_client`. It then registers two
semantic functions:
- intent.classify -> few-shot intent classifier (uses INTENT_PROMPT)
- gen.final_answer -> final response generator (uses FINAL_RESPONSE_PROMPT)

If SK or Gemini are unavailable, functions raise exceptions and higher-level
code should fall back to the original orchestrator.
"""
from typing import Any, AsyncGenerator, List
import logging

import semantic_kernel as sk
from semantic_kernel.connectors.ai.text_completion_client_base import TextCompletionClientBase

from app.llm.llm_client import INTENT_PROMPT, FINAL_RESPONSE_PROMPT, GREETING_PROMPT
from app.llm.llm_client import _use_gemini, _gemini_model
from typing import Any, AsyncGenerator, List, Optional
import logging

import semantic_kernel as sk
from semantic_kernel.connectors.ai.text_completion_client_base import TextCompletionClientBase

from app.llm.llm_client import INTENT_PROMPT, FINAL_RESPONSE_PROMPT, GREETING_PROMPT
from app.llm.llm_client import _use_gemini, _gemini_model, generate_response
from app.core.rag_engine import rag_engine
from app.core import actions

logger = logging.getLogger(__name__)


class GeminiTextCompletionClient(TextCompletionClientBase):
    """A minimal TextCompletionClientBase adapter that forwards prompts to Gemini.

    Implements the get_text_contents and get_streaming_text_content methods
    expected by Semantic Kernel. Each completion returns a list with one mapping
    containing a 'text' field.
    """

    def __init__(self, service_url: Optional[str] = None):
        # TextCompletionClientBase is a pydantic model that expects certain
        # fields (like ai_model_id). Provide a lightweight identifier so
        # initialization succeeds.
        try:
            super().__init__(ai_model_id="gemini")
        except TypeError:
            # Older/newer SK versions may not require args; fallback
            try:
                super().__init__()
            except Exception:
                pass
        # Assign extra attribute without triggering pydantic validation
        try:
            object.__setattr__(self, 'service_url', service_url)
        except Exception:
            # If that fails, ignore - the client can operate without this field
            pass

    async def get_text_contents(self, prompt: str, settings) -> List[dict]:
        """Async completion returning list of dicts with 'text'."""
        try:
            # Completion objects SK expects: objects with .text and .metadata
            class _Completion:
                def __init__(self, text: str, metadata: dict | None = None):
                    self.text = text
                    self.metadata = metadata or {}

            if _use_gemini and _gemini_model is not None:
                resp = _gemini_model.generate_content(prompt)
                text = getattr(resp, "text", None) or str(resp)
                return [_Completion(text, metadata={})]
            # Fallback to internal generator if Gemini not available
            text = generate_response(prompt, context="", intent="general_query")
            return [_Completion(text, metadata={})]
        except Exception as e:
            logger.exception("GeminiTextCompletionClient.get_text_contents failed: %s", e)
            class _CompletionErr:
                def __init__(self):
                    self.text = ""
                    self.metadata = {}

            return [_CompletionErr()]

    async def get_streaming_text_content(self, prompt: str, settings) -> AsyncGenerator[dict, None]:
        """Async streaming generator that yields a single chunk (compatible shape)."""
        try:
            for item in self.get_text_contents(prompt, settings):
                yield item
        except Exception as e:
            logger.exception("GeminiTextCompletionClient.get_streaming_text_content failed: %s", e)
            yield {"text": ""}


# Initialize kernel and register the Gemini adapter and semantic functions
kernel: Optional[sk.Kernel] = None


def init_kernel() -> sk.Kernel:
    global kernel
    if kernel is not None:
        return kernel

    kernel = sk.Kernel()

    # Register the Gemini adapter as a text completion service
    try:
        gemini_client = GeminiTextCompletionClient()
        kernel.add_service(gemini_client)
        logger.info("Registered Gemini text completion service with Semantic Kernel")
    except Exception as e:
        logger.exception("Failed to register Gemini service: %s", e)

    # Register semantic functions using prompts. These rely on the text completion
    # service we just registered. Using prompt-based functions keeps us compatible
    # across SK versions that expect prompt strings.
    try:
        kernel.add_function(plugin_name="intent", prompt=INTENT_PROMPT, function_name="classify")
        kernel.add_function(plugin_name="gen", prompt=FINAL_RESPONSE_PROMPT, function_name="final_answer")
        logger.info("Registered semantic functions: intent.classify, gen.final_answer")
    except Exception as e:
        logger.exception("Failed to register semantic functions: %s", e)

    return kernel


async def process_with_semkernel(query: str, user_id: Optional[str] = None, top_k: int = 3) -> dict:
    """High-level helper that uses SK functions to classify intent, retrieve RAG
    context, run intent-specific actions, and generate the final answer.

    Returns a dict compatible with the existing orchestrator output.
    """
    k = init_kernel()

    result = {
        "intent": "unknown",
        "confidence": 0.0,
        "response": "",
        "source_docs": [],
        "action_invoked": None,
    }

    try:
        # 1) Intent classification via the SK function
        from semantic_kernel.functions.kernel_arguments import KernelArguments
        func = k.get_function("intent", "classify")
        ka = KernelArguments(query=query)
        fr = await k.invoke(function=func, arguments=ka)

        def _extract_text(obj):
            try:
                # If SK FunctionResult was returned, unwrap its .value
                if hasattr(obj, 'value'):
                    obj = getattr(obj, 'value')
                if obj is None:
                    return ""
                if hasattr(obj, 'text'):
                    return getattr(obj, 'text')
                if isinstance(obj, (list, tuple)):
                    return "\n".join(_extract_text(x) for x in obj)
                if isinstance(obj, dict) and 'text' in obj:
                    return obj['text']
                if hasattr(obj, 'get_text'):
                    return obj.get_text()
                return str(obj)
            except Exception:
                return str(obj)

        text = _extract_text(fr)

        # Parse LLM reply: expected format 'intent (confidence)'
        import re
        # If SK returned a prompt template (indicating the prompt-based path didn't run properly),
        # fall back to the existing classify_intent implementation.
        if isinstance(text, str) and ("{intent}" in text or "{confidence}" in text or text.strip().startswith("Intent:")):
            from app.llm.llm_client import classify_intent as _classify_intent
            intent, confidence = await _classify_intent(query)
            result["intent"] = intent
            result["confidence"] = confidence
        else:
            m = re.search(r"(\w+)\s*\(([0-9.]+)\)", text or "")
            if m:
                result["intent"] = m.group(1)
                result["confidence"] = float(m.group(2))
            else:
                result["intent"] = text.strip() or "general_query"
                result["confidence"] = 0.5

        # 2) For greeting intents, generate quick response without RAG
        if result["intent"] == "greeting":
            from semantic_kernel.functions.kernel_arguments import KernelArguments
            gfunc = k.get_function("gen", "final_answer")
            gka = KernelArguments(context="", user_query=query, action_result="")
            gfr = await k.invoke(function=gfunc, arguments=gka)
            resp_text = _extract_text(gfr)
            # Fallback to the existing generator if SK returned a template placeholder
            if isinstance(resp_text, str) and ("{answer}" in resp_text or "{" in resp_text and "}" in resp_text):
                from app.llm.llm_client import generate_response as _generate_response
                resp_text = _generate_response(query, context="", intent="greeting")
            result["response"] = resp_text
            result["source_docs"] = []
            return result

        # 3) Non-greeting: retrieve RAG context
        context_docs = rag_engine.retrieve_relevant_docs(query, top_k=top_k)
        context_docs.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        context_text = "\n\n".join(d['text'] for d in context_docs)
        result["source_docs"] = context_docs

        # 4) Intent-specific actions
        action_result = None
        action_name = None

        if result["intent"] == "password_reset":
            action_result = actions.reset_password(user_id or "")
            action_name = "reset_password"
        elif result["intent"] == "check_ticket_status":
            ticket_id = None
            m2 = re.search(r"\b(\d{3,12})\b", query)
            if m2:
                ticket_id = m2.group(1)
            if ticket_id:
                action_result = actions.check_ticket_status(ticket_id)
                action_name = "check_ticket_status"
        elif result["intent"] == "generate_summary":
            docs_texts = [d['text'] for d in context_docs]
            action_result = actions.generate_summary(docs_texts)
            action_name = "generate_summary"

        # 5) Invoke the final generator with context and action result
        from semantic_kernel.functions.kernel_arguments import KernelArguments
        gfunc = k.get_function("gen", "final_answer")
        gka = KernelArguments(context=context_text, user_query=query, action_result=action_result or "")
        gfr = await k.invoke(function=gfunc, arguments=gka)
        final_text = _extract_text(gfr)
        # If SK returned a template placeholder, fall back to the existing generator which uses Gemini wrapper
        if isinstance(final_text, str) and ("{answer}" in final_text or ("{" in final_text and "}" in final_text)):
            from app.llm.llm_client import generate_response as _generate_response
            final_text = _generate_response(query, context=context_text, intent=result.get("intent", "general_query"), action_result=action_result or "")

        result["response"] = final_text
        result["action_invoked"] = action_name
        return result

    except Exception as e:
        logger.exception("Semantic Kernel processing failed: %s", e)
        result["intent"] = "error"
        result["confidence"] = 0.0
        result["response"] = "Semantic Kernel error"
        return result
