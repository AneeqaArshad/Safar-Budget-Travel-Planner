"""
LLM Service — Local Ollama Integration (robust)
"""

from typing import Optional
from langchain_community.chat_models.ollama import ChatOllama
LLM_MODEL = "tinyllama"  # you can switch anytime (mistral, llama3, etc.)
OLLAMA_URL = "http://host.docker.internal:11434"

def get_llm() -> Optional[ChatOllama]:
    """Return ChatOllama instance with safe fallback."""
    try:
        return ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_URL,
            temperature=0.2,
            request_timeout=30,
        )
    except Exception as e:
        print(f"[LLM INIT ERROR] {e}")
        return None


def safe_llm_invoke(prompt: str) -> str:
    """Safely invoke LLM and return text."""
    llm = get_llm()
    if not llm:
        return ""

    try:
        response = llm.invoke(prompt)
        return getattr(response, "content", str(response)).strip()
    except Exception as e:
        print(f"[LLM INVOKE ERROR] {e}")
        return ""


def health_check() -> bool:
    """Quick check to verify Ollama + model is reachable."""
    out = safe_llm_invoke("Reply with exactly: OK")
    return "OK" in out.strip().upper()