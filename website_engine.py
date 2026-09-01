"""
website_engine.py - Autonomous Live Website Builder & Hosting Engine

Generates complete, modern, responsive HTML5 + Tailwind CSS websites from user prompts
and hosts them live instantly with zero fees!
"""

import os
import re
import uuid
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")
os.makedirs(SITES_DIR, exist_ok=True)


def build_and_host_website(user_prompt: str, life_context: str = "") -> dict:
    """
    Builds a full-fledged responsive website using Gemini 2.5 Flash / Groq
    and saves it to the sites directory for instant live preview.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    system_instruction = (
        "You are an elite Senior Full-Stack Web Developer & UI/UX Designer. "
        "Your job is to generate a 100% COMPLETE, production-ready, beautiful, modern single-page website. "
        "Use Tailwind CSS CDN (https://cdn.tailwindcss.com), FontAwesome icons, modern Google Fonts, and vanilla JavaScript for interactivity. "
        "Include vibrant gradients, clean navigation, hero section, interactive feature cards, testimonials, FAQ, contact form, and footer. "
        "Make it fully mobile-responsive and visually stunning. "
        "Output ONLY valid, raw HTML5 code starting with <!DOCTYPE html> and ending with </html>. Do not include markdown backticks or explanations."
    )
    
    html_code = ""
    
    # Try Gemini 2.5 Flash
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {
                "system_instruction": {"parts": {"text": system_instruction}},
                "contents": [{"parts": [{"text": f"User Request: {user_prompt}\n\nContext:\n{life_context}"}]}]
            }
            resp = requests.post(url, json=payload, timeout=35)
            data = resp.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Strip markdown formatting if any
                clean_html = re.sub(r"^```(?:html)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
                clean_html = re.sub(r"\s*```$", "", clean_html.strip())
                html_code = clean_html
        except Exception as e:
            logger.error(f"Gemini website generation failed: {e}")
            
    # Fallback to Groq if Gemini failed
    if not html_code and groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ]
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=35)
            raw_text = resp.json()["choices"][0]["message"]["content"]
            clean_html = re.sub(r"^```(?:html)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
            clean_html = re.sub(r"\s*```$", "", clean_html.strip())
            html_code = clean_html
        except Exception as e:
            logger.error(f"Groq website generation failed: {e}")
            
    if not html_code:
        raise ValueError("Failed to generate HTML website code.")
        
    # Generate clean slug
    slug_base = re.sub(r"[^a-zA-Z0-9]+", "-", user_prompt.lower())[:30].strip("-")
    if not slug_base:
        slug_base = "site"
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"
    
    file_path = os.path.join(SITES_DIR, f"{slug}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_code)
        
    live_url = f"https://jarvis-3-telegram-bot.onrender.com/sites/{slug}"
    
    return {
        "slug": slug,
        "live_url": live_url,
        "file_path": file_path,
        "html_code": html_code
    }
