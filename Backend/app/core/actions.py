from typing import List

def reset_password(user_id: str) -> str:
    # In a real system this would trigger a password reset flow.
    return "You can reset your password from the login page under 'Forgot Password'."

def check_ticket_status(ticket_id: str) -> str:
    # Stub implementation — replace with real ticketing system integration.
    return f"Ticket {ticket_id} is currently being processed by the support team."

def generate_summary(docs: List[str]) -> str:
    # Very small summarizer stub. Replace with an LLM summarization call if needed.
    joined = " ".join(docs or [])
    return f"Summary: {joined[:200]}..." if joined else "Summary: No documents available."
