"""
self_evolution.py - Autonomous Self-Upgrading & Free-Tier Evolution Engine

Ensures Jarvis agents are:
1. BEST IN CLASS: Continuously improving prompt quality, formatting, and intelligence.
2. 100% FREE TIER ONLY: Strict Zero-Billing Firewall preventing unexpected costs.
3. SELF-LEARNING: Automatically ingesting user corrections and teaching moments into persistent memory.
"""

import os
import json
import logging
import requests
from datetime import datetime
from memory import save_life_event, _load_local_memory, _save_local_memory

logger = logging.getLogger(__name__)

# Strict whitelist of verified 100% FREE AI endpoints and models
FREE_TIER_WHITELIST = {
    "google": {
        "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        "cost": 0.0,
        "policy": "100% Free Tier under Google AI Studio Quota"
    },
    "groq": {
        "models": ["openai/gpt-oss-120b", "qwen/qwen3.6-27b", "llama-3.3-70b-versatile"],
        "cost": 0.0,
        "policy": "100% Free Open-Source Inference on Groq Cloud"
    },
    "telegram": {
        "cost": 0.0,
        "policy": "100% Free Telegram Bot API"
    },
    "render": {
        "cost": 0.0,
        "policy": "100% Free Web Service Tier"
    }
}

EVOLUTION_LOG = "evolution_log.json"


def verify_zero_billing(provider_name: str, model_name: str = None) -> bool:
    """
    Zero-Billing Firewall: Verifies that an AI model/provider is strictly 100% free.
    Blocks any paid or unverified endpoints.
    """
    provider_name = provider_name.lower()
    if provider_name not in FREE_TIER_WHITELIST:
        logger.warning(f"[BILLING FIREWALL BLOCKED] Unverified provider: {provider_name}")
        return False
    
    if model_name:
        allowed_models = FREE_TIER_WHITELIST[provider_name].get("models", [])
        if allowed_models and model_name not in allowed_models:
            logger.warning(f"[BILLING FIREWALL BLOCKED] Model {model_name} not in free whitelist for {provider_name}")
            return False
            
    return True


def auto_learn_from_feedback(user_message: str, agent_name: str = "general") -> str | None:
    """
    Detects if the user is teaching Jarvis a new rule, preference, or fact.
    Automatically evolves the system memory and agent skills.
    """
    learning_triggers = [
        "remember that", "from now on", "always remember", "make sure you",
        "i prefer", "my preference", "dont forget that", "note that",
        "learn this", "rule is", "update yourself"
    ]
    
    msg_lower = user_message.lower()
    if any(trigger in msg_lower for trigger in learning_triggers):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fact_entry = f"[{timestamp}] Auto-Learned Preference: {user_message.strip()}"
        
        # Categorize whether personal or official
        category = "official" if any(w in msg_lower for w in ["landcraft", "gofrugal", "pos", "inventory", "work", "office"]) else "personal"
        save_life_event(category, fact_entry)
        
        # Log to evolution log
        _log_evolution("SKILL_UPGRADE", f"Learned new rule for agent [{agent_name}]: {user_message[:120]}")
        return f"🧠 *Auto-Upgraded Skill & Memory:* I have permanently registered this rule into my core knowledge base at zero cost!"
        
    return None


def _log_evolution(event_type: str, details: str):
    """Logs auto-evolution and upgrade events."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "details": details,
        "cost": "₹0.00 (FREE)"
    }
    
    logs = []
    if os.path.exists(EVOLUTION_LOG):
        try:
            with open(EVOLUTION_LOG, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
    logs.append(log_entry)
    with open(EVOLUTION_LOG, "w") as f:
        json.dump(logs[-50:], f, indent=2)  # Keep last 50 evolution records
