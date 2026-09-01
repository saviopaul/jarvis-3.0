"""
agents.py - Jarvis 3.0 Lightweight Swarm Architecture

Custom multi-agent system built without heavy frameworks.
Works on Python 3.14+. Zero extra dependencies.

Each specialist agent is just a focused API call with a unique
expert system prompt. The Manager routes tasks and consolidates results.

TEAM:
  - Lawyer Agent           → Legal advice, contracts, compliance
  - Coder Agent            → Software engineering, debugging
  - Web Developer Agent    → HTML, CSS, JS, React, full-stack
  - Designer Agent         → UI/UX, branding, color, layout
  - Hardware Agent         → Servers, networking, PC builds
  - Server Agent           → Linux, DevOps, Docker, deployment
  - Musician Agent         → Music theory, lyrics, composition
"""

import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ── SPECIALIST AGENT PERSONAS ─────────────────────────────────────────────────

AGENTS = {
    "lawyer": {
        "emoji": "⚖️",
        "name": "Legal Advisor",
        "keywords": ["legal", "law", "contract", "sue", "court", "rights",
                     "compliance", "agreement", "terms", "dispute", "clause", "liable"],
        "system": (
            "You are a seasoned legal advisor with 20+ years of experience. "
            "You cover contract law, corporate law, IP, and employment law. "
            "Speak in plain English, not jargon. Be realistic about risks. "
            "Always give exactly 3 options with a clear best recommendation."
        ),
    },
    "coder": {
        "emoji": "🧑‍💻",
        "name": "Software Engineer",
        "keywords": ["code", "bug", "python", "function", "script", "debug",
                     "algorithm", "api", "backend", "database", "error", "fix"],
        "system": (
            "You are a senior software engineer expert in Python, JavaScript, "
            "REST APIs, databases and cloud systems. Write clean, working code "
            "with error handling and comments. Be concise and practical."
        ),
    },
    "web": {
        "emoji": "🌐",
        "name": "Web Developer",
        "keywords": ["website", "html", "css", "react", "frontend", "landing page",
                     "web app", "responsive", "nextjs", "tailwind", "ui component"],
        "system": (
            "You are an expert full-stack web developer specializing in HTML5, CSS3, "
            "JavaScript ES6+, React, Next.js and Tailwind CSS. Write complete, "
            "working code that is responsive and accessible. Include all markup needed."
        ),
    },
    "designer": {
        "emoji": "🎨",
        "name": "UI/UX Designer",
        "keywords": ["design", "ui", "ux", "color", "font", "layout", "logo",
                     "branding", "mockup", "palette", "figma", "wireframe"],
        "system": (
            "You are a creative UI/UX designer with deep knowledge of design "
            "principles, typography, color theory and user psychology. "
            "Give specific, actionable design specifications. Always provide "
            "3 design direction options with a clear recommendation."
        ),
    },
    "hardware": {
        "emoji": "🖥️",
        "name": "Hardware Specialist",
        "keywords": ["hardware", "cpu", "gpu", "ram", "server rack", "networking",
                     "router", "iot", "pc build", "specs", "motherboard", "switch"],
        "system": (
            "You are a hardware and networking specialist expert in CPUs, GPUs, "
            "RAM, storage, networking protocols, server racks and IoT devices. "
            "Give practical, budget-aware recommendations with 3 options and a best pick."
        ),
    },
    "server": {
        "emoji": "⚙️",
        "name": "DevOps Engineer",
        "keywords": ["deploy", "docker", "linux", "nginx", "ssl", "render",
                     "heroku", "aws", "devops", "ci/cd", "bash", "server", "vps"],
        "system": (
            "You are a DevOps engineer expert in Linux, Bash, Docker, Nginx, "
            "SSL/TLS, Render, GitHub Actions and cloud platforms. "
            "Optimize for uptime, security and zero-cost deployments. "
            "Provide exact commands and configs, not vague instructions."
        ),
    },
    "musician": {
        "emoji": "🎵",
        "name": "Musician & Producer",
        "keywords": ["music", "song", "chord", "lyrics", "melody", "beat",
                     "tempo", "key", "scale", "produce", "compose", "instrument"],
        "system": (
            "You are a professional multi-genre musician and producer with knowledge "
            "across classical, jazz, pop, hip-hop and electronic music. "
            "Explain music concepts clearly for any skill level. "
            "Give 3 creative options with a recommendation when asked for direction."
        ),
    },
}

BASE_SYSTEM = (
    "CRITICAL RULE: Whenever giving advice, strategy or decisions, "
    "ALWAYS provide exactly 3 distinct options. "
    "After the options, state which is your recommendation and why. "
    "Be realistic, grounded and concise."
)


def _call_groq_raw(system_prompt: str, user_message: str) -> str:
    """Direct Groq API call for specialist agents."""
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not set")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": system_prompt + "\n\n" + BASE_SYSTEM},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 1500,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    data = resp.json()
    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    raise ValueError(f"Groq error: {data.get('error', {}).get('message', resp.text)}")


def _call_gemini_raw(system_prompt: str, user_message: str) -> str:
    """Direct Gemini API call for specialist agents."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    payload = {
        "system_instruction": {"parts": {"text": system_prompt + "\n\n" + BASE_SYSTEM}},
        "contents": [{"parts": [{"text": user_message}]}]
    }
    resp = requests.post(url, json=payload, timeout=25)
    result = resp.json()
    if "candidates" in result and len(result["candidates"]) > 0:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    raise ValueError(f"Gemini error: {result.get('error', {}).get('message', resp.text)}")


def _call_agent(system_prompt: str, user_message: str) -> str:
    """Calls the best available provider with automatic fallback."""
    # Try Groq first
    if os.environ.get("GROQ_API_KEY"):
        try:
            return _call_groq_raw(system_prompt, user_message)
        except Exception:
            pass
    # Fallback to Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return _call_gemini_raw(system_prompt, user_message)
        except Exception as e:
            raise e
    return "No AI provider available."


def detect_agents_needed(user_message: str) -> list:
    """Detects which specialist agents should handle this message."""
    msg = user_message.lower()
    needed = []
    for agent_id, agent in AGENTS.items():
        if any(kw in msg for kw in agent["keywords"]):
            needed.append(agent_id)
    return needed


def run_crew(user_message: str, life_context: str = "") -> str:
    """
    Runs the appropriate specialist agents for the given message.
    Returns a consolidated expert response.
    """
    agents_needed = detect_agents_needed(user_message)

    if not agents_needed:
        return None  # No specialist needed, use regular brain

    context_note = f"\n\nUser's current life context:\n{life_context}" if life_context else ""
    full_message = user_message + context_note

    results = []
    agent_names = []

    for agent_id in agents_needed:
        agent = AGENTS[agent_id]
        agent_names.append(f"{agent['emoji']} {agent['name']}")
        try:
            reply = _call_agent(agent["system"], full_message)
            results.append(f"{agent['emoji']} *{agent['name']}*:\n{reply}")
        except Exception as e:
            results.append(f"{agent['emoji']} *{agent['name']}*: (unavailable — {str(e)})")

    header = f"🤖 *JARVIS CREW ACTIVATED*\nSpecialists: {', '.join(agent_names)}\n\n"
    return header + "\n\n---\n\n".join(results)
