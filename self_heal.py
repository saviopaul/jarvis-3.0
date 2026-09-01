"""
self_heal.py - Jarvis Self-Healing Module

When Jarvis encounters any error, this module:
1. Captures the full error traceback
2. Sends it to Gemini/Claude to diagnose the root cause
3. Generates a code fix
4. Patches the broken file automatically
5. Restarts the affected component
6. Notifies the user on Telegram that healing occurred
"""

import os
import sys
import traceback
import subprocess
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")  # Your personal Telegram chat ID

HEALING_LOG = "healing_log.json"


def notify_owner(message: str):
    """Send a Telegram message to the owner about healing activity."""
    if not TELEGRAM_TOKEN or not OWNER_CHAT_ID:
        logger.warning("Cannot notify owner: TELEGRAM_TOKEN or OWNER_CHAT_ID not set.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": OWNER_CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


def diagnose_and_fix(error_traceback: str, broken_file: str) -> str | None:
    """
    Sends the error to the AI and asks for a patch.
    Returns the fixed file content, or None if it cannot fix it.
    """
    if not GEMINI_API_KEY:
        logger.error("No GEMINI_API_KEY available for self-healing diagnosis.")
        return None

    try:
        # Read the broken file
        with open(broken_file, "r") as f:
            broken_code = f.read()
    except FileNotFoundError:
        logger.error(f"Cannot read broken file: {broken_file}")
        return None

    prompt = (
        f"You are an expert Python debugger. A Jarvis AI system encountered an error.\n"
        f"Your job is to fix the bug. Return ONLY the complete corrected Python file, with no explanation, no markdown code blocks, just raw Python code.\n\n"
        f"ERROR TRACEBACK:\n{error_traceback}\n\n"
        f"BROKEN FILE ({broken_file}):\n{broken_code}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        fixed_code = result["candidates"][0]["content"]["parts"][0]["text"]
        return fixed_code
    except Exception as e:
        logger.error(f"AI diagnosis failed: {e}")
        return None


def apply_fix(broken_file: str, fixed_code: str) -> bool:
    """Backs up the broken file and writes the fix."""
    try:
        # Backup the broken file
        backup_path = broken_file + f".broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(broken_file, "r") as f:
            original = f.read()
        with open(backup_path, "w") as f:
            f.write(original)

        # Write the fix
        with open(broken_file, "w") as f:
            f.write(fixed_code)

        logger.info(f"Fix applied to {broken_file}. Backup saved to {backup_path}.")
        return True
    except Exception as e:
        logger.error(f"Failed to apply fix: {e}")
        return False


def self_heal(error: Exception, broken_file: str):
    """
    Main self-healing entry point. Call this from any except block.
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            self_heal(e, __file__)
    """
    error_tb = traceback.format_exc()
    logger.error(f"[SELF-HEAL] Error detected in {broken_file}: {error}")

    # Notify owner that healing has started
    notify_owner(
        f"⚠️ *JARVIS SELF-HEALING INITIATED*\n\n"
        f"📁 File: `{os.path.basename(broken_file)}`\n"
        f"❌ Error: `{str(error)[:200]}`\n\n"
        f"🧠 Diagnosing with AI..."
    )

    # Ask AI to diagnose and fix
    fixed_code = diagnose_and_fix(error_tb, broken_file)

    if fixed_code:
        success = apply_fix(broken_file, fixed_code)
        if success:
            notify_owner(
                f"✅ *JARVIS HEALED SUCCESSFULLY*\n\n"
                f"📁 Fixed: `{os.path.basename(broken_file)}`\n"
                f"🔄 Restarting affected module..."
            )
            # Restart the entire bot process to reload fixed code
            logger.info("[SELF-HEAL] Restarting bot process...")
            subprocess.Popen([sys.executable, "bot.py"])
            sys.exit(0)  # Exit current broken process
        else:
            notify_owner(
                f"❌ *JARVIS COULD NOT APPLY FIX*\n\n"
                f"File: `{os.path.basename(broken_file)}`\n"
                f"Please check the logs manually."
            )
    else:
        notify_owner(
            f"🆘 *JARVIS COULD NOT DIAGNOSE THE ERROR*\n\n"
            f"File: `{os.path.basename(broken_file)}`\n"
            f"Error: `{str(error)[:300]}`\n\n"
            f"Your attention is required."
        )
