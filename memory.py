import os
import json
import redis
from datetime import datetime

# Initialize Redis (or fallback to local file if not configured)
REDIS_URL = os.environ.get("REDIS_URL")
redis_client = redis.from_url(REDIS_URL) if REDIS_URL else None
LOCAL_MEMORY_FILE = "life_context.json"

def _load_local_memory():
    if os.path.exists(LOCAL_MEMORY_FILE):
        with open(LOCAL_MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"personal": [], "official": []}

def _save_local_memory(data):
    with open(LOCAL_MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def save_life_event(category: str, event_details: str) -> str:
    """
    Saves a fact, event, or task about the user's life into long-term memory.
    category must be either 'personal' or 'official'.
    """
    category = category.lower()
    if category not in ["personal", "official"]:
        category = "personal"
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {event_details}"
    
    if redis_client:
        redis_client.lpush(f"jarvis_memory_{category}", entry)
    else:
        mem = _load_local_memory()
        mem[category].append(entry)
        _save_local_memory(mem)
        
    return f"Successfully recorded to {category} memory."

def get_life_context() -> str:
    """Retrieves all current facts and events from the user's personal and official life."""
    context = "USER LIFE CONTEXT:\n\n"
    
    if redis_client:
        official = redis_client.lrange("jarvis_memory_official", 0, -1)
        personal = redis_client.lrange("jarvis_memory_personal", 0, -1)
        
        context += "--- OFFICIAL LIFE ---\n"
        for item in official:
            context += f"- {item.decode('utf-8')}\n"
            
        context += "\n--- PERSONAL LIFE ---\n"
        for item in personal:
            context += f"- {item.decode('utf-8')}\n"
    else:
        mem = _load_local_memory()
        context += "--- OFFICIAL LIFE ---\n"
        for item in mem.get("official", []):
            context += f"- {item}\n"
            
        context += "\n--- PERSONAL LIFE ---\n"
        for item in mem.get("personal", []):
            context += f"- {item}\n"
            
    return context
