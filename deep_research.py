"""
deep_research.py - Autonomous Web Research & Knowledge Synthesizer

Allows Jarvis to search the web, fetch live documentation, synthesize architecture plans,
and gather cutting-edge tutorials at zero cost!
"""

import os
import json
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def search_web_free(query: str, max_results: int = 5) -> list:
    """
    Performs a free web search using DuckDuckGo HTML / Instant Answers.
    Returns a list of {title, snippet, url}.
    """
    results = []
    try:
        # DuckDuckGo HTML search
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for result in soup.find_all("div", class_="result")[:max_results]:
                title_elem = result.find("a", class_="result__a")
                snippet_elem = result.find("a", class_="result__snippet")
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    results.append({"title": title, "snippet": snippet, "url": link})
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        
    return results


def fetch_webpage_text(url: str, max_chars: int = 4000) -> str:
    """Fetches and strips HTML from a webpage to extract clean text."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts and styles
            for s in soup(["script", "style", "nav", "footer", "header"]):
                s.decompose()
            text = ' '.join(soup.stripped_strings)
            return text[:max_chars]
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return f"Error fetching {url}: {str(e)}"
    return ""


def run_deep_research(topic: str) -> str:
    """
    Performs autonomous multi-step research on any complex topic, tool, or tech stack,
    synthesizing an actionable, step-by-step master plan.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    search_results = search_web_free(topic, max_results=4)
    
    context_data = "\n\n".join([
        f"SOURCE [{i+1}]: {r['title']}\nURL: {r['url']}\nSUMMARY: {r['snippet']}"
        for i, r in enumerate(search_results)
    ])
    
    prompt = (
        f"You are the Chief Research & Autonomous Systems Architect (Gemini / Anthropic / Claude caliber).\n"
        f"A user asked to research, design, and architect the following goal:\n"
        f"GOAL: {topic}\n\n"
        f"WEB RESEARCH FINDINGS:\n{context_data}\n\n"
        f"Provide a comprehensive, authoritative MASTER BLUEPRINT:\n"
        f"1. 🎯 EXECUTIVE SUMMARY & FEASIBILITY\n"
        f"2. 🏗️ SYSTEM ARCHITECTURE & TECH STACK (100% Free / Open Source tools)\n"
        f"3. 🛠️ STEP-BY-STEP STEP EXECUTION BLUEPRINT (Numbered phases with exact commands and logic)\n"
        f"4. 📦 PRODUCTION-READY CODE STRUCTURE (Folder tree and core file blueprints)\n"
        f"5. 💡 3 STRATEGIC IMPLEMENTATION OPTIONS with a top recommendation."
    )
    
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=35)
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini research synthesis failed: {e}")
            
    return f"Research results gathered for '{topic}':\n\n{context_data}"
