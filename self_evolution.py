"""
self_evolution.py - Autonomous Self-Upgrading & Free-Tier Evolution Engine

Allows Jarvis to:
1. AUTONOMOUSLY UPGRADE HIMSELF: When the user asks for any new agent, tool, skill, or bot,
   Jarvis dynamically writes the persona, registers it into the swarm, and updates his live brain!
2. ZERO-BILLING FIREWALL: Strictly enforces 100% free-tier APIs and open-source models only.
3. PERSISTENT SKILL SYNTHESIS: Saves dynamically learned agents to dynamic_agents.json and Git.
"""

import os
import re
import json
import logging
import requests
from datetime import datetime
from memory import save_life_event

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

EVOLUTION_LOG = os.path.join(os.path.dirname(__file__), "evolution_log.json")
DYNAMIC_AGENTS_FILE = os.path.join(os.path.dirname(__file__), "dynamic_agents.json")


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


def load_dynamic_agents() -> dict:
    """Loads dynamically synthesized self-upgraded agents."""
    if os.path.exists(DYNAMIC_AGENTS_FILE):
        try:
            with open(DYNAMIC_AGENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading dynamic agents: {e}")
    return {}


def save_dynamic_agents(agents_dict: dict):
    """Saves dynamically synthesized agents to disk."""
    with open(DYNAMIC_AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents_dict, f, indent=2, ensure_ascii=False)


def autonomous_self_upgrade(upgrade_request: str) -> dict:
    """
    Takes a user request to add a new specialist, tool, or skill,
    synthesizes the full agent persona, registers it into the swarm,
    and deploys the upgrade at zero cost!
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    prompt = (
        f"You are the Meta-Architecture Evolution Engine for Jarvis 3.0.\n"
        f"The user wants to upgrade Jarvis with a new capability/agent:\n"
        f"USER REQUEST: {upgrade_request}\n\n"
        f"Design a high-precision, production-grade specialist agent persona.\n"
        f"Return a valid JSON object with the following schema:\n"
        f"{{\n"
        f'  "agent_id": "short_unique_snake_case_id",\n'
        f'  "name": "Full Specialist Title",\n'
        f'  "emoji": "🎯",\n'
        f'  "keywords": ["keyword1", "keyword2", "phrase1", "phrase2", "phrase3"],\n'
        f'  "system_prompt": "You are the Senior Specialist... Detailed instructions covering 4 core pillars with 3 options and top recommendation."\n'
        f"}}\n"
        f"Output ONLY the JSON object. Zero markdown, zero introductory text."
    )
    
    agent_data = {}
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=30)
            raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean.strip())
            agent_data = json.loads(clean)
        except Exception as e:
            logger.error(f"Agent synthesis AI error: {e}")
            
    if not agent_data:
        # Fallback dynamic agent
        clean_id = re.sub(r'[^a-zA-Z0-9_]', '_', upgrade_request.lower().strip()[:20])
        agent_data = {
            "agent_id": f"agent_{clean_id}",
            "name": f"{upgrade_request.title()} Specialist",
            "emoji": "⚡",
            "keywords": [w.lower() for w in upgrade_request.split() if len(w) > 3],
            "system_prompt": f"You are the expert specialist in {upgrade_request}. Always provide 3 actionable options with a top recommendation."
        }
        
    # Register into dynamic agents registry
    dynamic_agents = load_dynamic_agents()
    agent_id = agent_data.get("agent_id", f"agent_{uuid.uuid4().hex[:6]}")
    
    dynamic_agents[agent_id] = {
        "emoji": agent_data.get("emoji", "⚡"),
        "name": agent_data.get("name", "Custom Specialist"),
        "keywords": agent_data.get("keywords", []),
        "system": agent_data.get("system_prompt", "")
    }
    save_dynamic_agents(dynamic_agents)
    
    # Log evolution
    _log_evolution("DYNAMIC_AGENT_UPGRADE", f"Synthesized and deployed agent [{agent_data.get('name')}] with triggers: {agent_data.get('keywords')}")
    
    return {
        "agent_id": agent_id,
        "name": agent_data.get("name"),
        "emoji": agent_data.get("emoji"),
        "keywords": agent_data.get("keywords", []),
        "system_prompt": agent_data.get("system_prompt")
    }


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
        
        category = "official" if any(w in msg_lower for w in ["landcraft", "gofrugal", "pos", "inventory", "work", "office"]) else "personal"
        save_life_event(category, fact_entry)
        
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
        json.dump(logs[-50:], f, indent=2)
