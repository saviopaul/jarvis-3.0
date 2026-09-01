import os
import json
import requests as http_requests
from datetime import date
from google import genai
from tools import AVAILABLE_TOOLS
from memory import save_life_event, get_life_context, get_life_context as _get_context_text
from providers import (
    get_active_provider, increment_usage, is_provider_exhausted,
    request_provider_switch, is_awaiting_approval
)
from agents import run_crew, detect_agents_needed

# Add memory tools
ALL_TOOLS = AVAILABLE_TOOLS + [save_life_event, get_life_context]

SYSTEM_INSTRUCTION = (
    "You are Jarvis 3.0, the user's most trusted buddy, confidant, and autonomous AI partner. "
    "The user comes to you for absolutely ANYTHING: serious software engineering, business strategy, personal advice, or just someone to bounce ideas off of. "
    "Your tone should be warm, direct, conversational, and deeply supportive. Never use robotic corporate filler. "
    "Your primary job is to keep track of EVERYTHING happening in their personal and official life. "
    "When the user tells you about an upcoming event, task, or fact, ALWAYS use the `save_life_event` tool to remember it. "
    "When the user asks for advice or a summary, ALWAYS use the `get_life_context` tool first to read their current situation. "
    "CRITICAL RULE: Whenever the user asks for advice, a strategy, a solution, or a decision on ANYTHING (legal, coding, business, personal), you must ALWAYS provide exactly 3 distinct options. After presenting the 3 options, explicitly state which one you recommend as the best choice and why. "
    "Give advice that is highly REALISTIC and grounded in their actual life context. Do NOT make assumptions. "
    "If you don't have enough context in memory, ask the user clarifying questions. "
    "You also have tools to deploy code and manage GitHub if asked. Act as their ultimate partner in all aspects of life."
)


def _call_gemini(user_message: str, chat_history: list) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": {"text": SYSTEM_INSTRUCTION}},
        "contents": [{"parts": [{"text": user_message}]}]
    }
    resp = http_requests.post(url, json=payload, timeout=25)
    data = resp.json()
    if "candidates" in data and len(data["candidates"]) > 0:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    raise ValueError(f"Gemini error: {data.get('error', {}).get('message', resp.text)}")


def _call_groq(user_message: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "qwen/qwen3.6-27b",
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }
    resp = http_requests.post(url, headers=headers, json=payload, timeout=25)
    data = resp.json()
    if "choices" in data and len(data["choices"]) > 0:
        content = data["choices"][0]["message"]["content"]
        # Remove reasoning tags if present
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        return content
    raise ValueError(f"Groq error: {data.get('error', {}).get('message', resp.text)}")


def _call_llm_with_fallback(user_message: str) -> str:
    """Tries Gemini 2.5 Flash first (most accurate), falls back to Groq, then Ollama."""
    # 1. Try Gemini 2.5 Flash
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return _call_gemini(user_message, [])
        except Exception:
            pass

    # 2. Try Groq (Qwen 3.6)
    if os.environ.get("GROQ_API_KEY"):
        try:
            return _call_groq(user_message)
        except Exception:
            pass

    # 3. Try Ollama (local)
    try:
        return _call_ollama(user_message)
    except Exception:
        pass

    return "Sorry, I am temporarily unable to connect to the AI providers. Please check your API keys."


def _call_ollama(user_message: str) -> str:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }
    resp = http_requests.post(url, json=payload, timeout=60)
    return resp.json()["message"]["content"]


from self_evolution import auto_learn_from_feedback, verify_zero_billing


def process_message(user_message: str, chat_history: list = None) -> str | tuple:
    """
    Routes the message to the active AI provider.
    - Simple/personal messages → Gemini/Groq directly
    - Specialist requests (legal, code, design etc.) → CrewAI Swarm
    Returns either a string reply, or a tuple (reply, needs_approval=True)
    """
    # ── Autonomous Self-Evolution / Auto-Learn Check ────────────────────────
    learned_notice = auto_learn_from_feedback(user_message)
    # ────────────────────────────────────────────────────────────────────────

    provider = get_active_provider()

    # Check if current provider is exhausted
    if is_provider_exhausted(provider["id"]):
        switch_message, _ = request_provider_switch()
        return switch_message, True

    # ── CrewAI Swarm Routing ─────────────────────────────────────────────────
    # Detect if a specialist agent should handle this
    specialists_needed = detect_agents_needed(user_message)
    # Only activate the crew for non-trivial specialist tasks
    SPECIALIST_TRIGGERS = ["lawyer", "web", "designer", "hardware", "server", "musician", "gofrugal", "email", "personal", "insurance", "education", "youtube_growth", "marathi", "hindi", "tester", "debugger", "playwright", "crawler", "bank_ocr", "psychologist", "viral_growth"]
    if any(s in specialists_needed for s in SPECIALIST_TRIGGERS):
        try:
            life_context = _get_context_text()
            reply = run_crew(user_message, life_context)
            increment_usage(provider["id"])
            if learned_notice:
                reply = f"{learned_notice}\n\n{reply}"
            return reply
        except Exception as e:
            # Fallback to regular brain if crew fails
            pass
    # ────────────────────────────────────────────────────────────────────────

    try:
        reply = _call_llm_with_fallback(user_message)
        increment_usage(provider["id"])
        if learned_notice:
            reply = f"{learned_notice}\n\n{reply}"
        return reply
    except Exception as e:
        return f"System Error: {str(e)}"
