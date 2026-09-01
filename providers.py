"""
providers.py - AI Provider Manager for Jarvis 3.0

Manages multiple FREE AI providers with automatic fallback.
Jarvis will always ask permission before switching providers.

FREE Provider Cascade:
  1. Gemini 1.5 Flash   - Google (1,500 req/day free)
  2. Groq / Llama3      - Groq (free tier, very fast)
  3. Ollama             - Local model on your machine (100% free, unlimited)
"""

import os
import json
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = "provider_state.json"

# All free providers in priority order
PROVIDERS = [
    {
        "id": "gemini",
        "name": "Gemini 1.5 Flash (Google)",
        "daily_limit": 1400,
        "env_key": "GEMINI_API_KEY",
        "cost": "FREE"
    },
    {
        "id": "groq",
        "name": "Llama 3.1 on Groq",
        "daily_limit": 14400,   # Groq free tier is very generous
        "env_key": "GROQ_API_KEY",
        "cost": "FREE"
    },
    {
        "id": "ollama",
        "name": "Ollama (Local AI on your machine)",
        "daily_limit": 999999,   # Unlimited - runs locally
        "env_key": None,
        "cost": "FREE (local)"
    }
]


def _load_state() -> dict:
    today = str(date.today())
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        if state.get("date") == today:
            return state
    # Fresh state for today
    return {
        "date": today,
        "active_provider": "gemini",
        "awaiting_switch_approval": False,
        "proposed_provider": None,
        "usage": {p["id"]: 0 for p in PROVIDERS}
    }


def _save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_active_provider() -> dict:
    state = _load_state()
    pid = state.get("active_provider", "gemini")
    return next((p for p in PROVIDERS if p["id"] == pid), PROVIDERS[0])


def increment_usage(provider_id: str):
    state = _load_state()
    state["usage"][provider_id] = state["usage"].get(provider_id, 0) + 1
    _save_state(state)


def is_provider_exhausted(provider_id: str) -> bool:
    state = _load_state()
    provider = next((p for p in PROVIDERS if p["id"] == provider_id), None)
    if not provider:
        return True
    return state["usage"].get(provider_id, 0) >= provider["daily_limit"]


def get_next_available_provider(current_id: str) -> dict | None:
    """Returns the next provider in the cascade that is available and configured."""
    current_index = next((i for i, p in enumerate(PROVIDERS) if p["id"] == current_id), 0)
    for provider in PROVIDERS[current_index + 1:]:
        # Check if the provider has an API key configured (or is local)
        if provider["env_key"] is None:
            return provider  # Ollama needs no key
        if os.environ.get(provider["env_key"]):
            return provider
    return None


def request_provider_switch() -> tuple[str, str]:
    """
    Called when the active provider is exhausted.
    Returns (switch_message, proposed_provider_id or None)
    """
    state = _load_state()
    current = get_active_provider()
    next_provider = get_next_available_provider(current["id"])

    if next_provider:
        state["awaiting_switch_approval"] = True
        state["proposed_provider"] = next_provider["id"]
        _save_state(state)

        message = (
            f"⚠️ *Heads up, boss!*\n\n"
            f"I've hit my daily free limit on *{current['name']}* "
            f"({current['daily_limit']} requests used).\n\n"
            f"I can switch over to *{next_provider['name']}* which is also completely *{next_provider['cost']}* "
            f"— no charges whatsoever.\n\n"
            f"👉 Reply *YES* to switch, or *NO* to pause until tomorrow midnight when limits reset."
        )
        return message, next_provider["id"]
    else:
        message = (
            f"⚠️ *Heads up, boss!*\n\n"
            f"I've hit my daily free limit on *{current['name']}* and I have no other free providers configured right now.\n\n"
            f"🔧 Options:\n"
            f"1. Add a free *Groq API key* at console.groq.com (takes 1 min)\n"
            f"2. Install *Ollama* locally for unlimited free AI\n"
            f"3. Wait until tomorrow midnight when my limits reset\n\n"
            f"I won't touch anything until then. No charges. 🛡️"
        )
        return message, None


def approve_switch() -> str:
    """Called when user says YES to switching providers."""
    state = _load_state()
    proposed = state.get("proposed_provider")
    if not proposed:
        return "No pending provider switch to approve."

    state["active_provider"] = proposed
    state["awaiting_switch_approval"] = False
    state["proposed_provider"] = None
    _save_state(state)

    provider = next((p for p in PROVIDERS if p["id"] == proposed), None)
    return f"✅ Switched to *{provider['name']}*. Still 100% free. Let's keep going!"


def deny_switch() -> str:
    """Called when user says NO to switching providers."""
    state = _load_state()
    state["awaiting_switch_approval"] = False
    state["proposed_provider"] = None
    _save_state(state)
    return "Got it! I'll pause until tomorrow midnight when the free limit resets. 🌙"


def is_awaiting_approval() -> bool:
    state = _load_state()
    return state.get("awaiting_switch_approval", False)
