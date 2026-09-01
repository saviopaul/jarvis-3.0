"""
multimodal.py - Multimodal processing engine for Jarvis 3.0

Handles:
1. Photos & Screenshots (Vision)
2. Voice notes & Audio files (.ogg, .mp3, .wav)
3. YouTube video transcripts & understanding
"""

import os
import re
import base64
import requests
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def analyze_media(file_bytes: bytes, mime_type: str, caption_prompt: str = "") -> str:
    """
    Sends images, screenshots, or audio files to Gemini 2.5 Flash for multimodal analysis.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return "Error: GEMINI_API_KEY not configured for media processing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    
    b64_data = base64.b64encode(file_bytes).decode("utf-8")
    
    default_prompt = "Carefully analyze this media. If it's a screenshot or image, read all text, UI elements, and explain what you see. If it's an error message, explain how to fix it. If it's audio, transcribe and understand what is being said, and respond helpfully."
    prompt = caption_prompt if caption_prompt.strip() else default_prompt

    system_instruction = (
        "You are Jarvis 3.0, the user's trusted AI partner with multimodal vision and audio comprehension. "
        "Analyze images, screenshots, and audio thoroughly, give realistic and actionable insights, "
        "and always provide 3 options when recommending next steps or solutions."
    )

    payload = {
        "system_instruction": {"parts": {"text": system_instruction}},
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=40)
        data = resp.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Could not process media: {data.get('error', {}).get('message', resp.text)}"
    except Exception as e:
        return f"Media analysis error: {str(e)}"


def extract_youtube_transcript(url: str) -> str:
    """
    Extracts transcript from a YouTube URL and summarizes/analyzes it.
    """
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if not video_id_match:
        return "Could not find a valid YouTube video ID in the provided link."

    video_id = video_id_match.group(1)

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([t["text"] for t in transcript_list])
        
        # Now send transcript to Gemini for deep summary
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            return f"Transcript extracted ({len(full_transcript)} chars), but no Gemini key to analyze."
            
        prompt = (
            f"Here is the complete transcript of the YouTube video (ID: {video_id}):\n\n"
            f"{full_transcript[:40000]}\n\n"
            f"Please provide a comprehensive, structured breakdown:\n"
            f"1. Executive Summary\n"
            f"2. Key Takeaways & Actionable Points\n"
            f"3. 3 Strategic Options / Applications based on this content with a top recommendation."
        )
        
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url_api, json=payload, timeout=40)
        data = resp.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return f"📹 *YOUTUBE VIDEO ANALYSIS (ID: {video_id})*\n\n" + data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Extracted transcript ({len(full_transcript)} chars), but summary generation failed."
    except Exception as e:
        return f"Could not fetch YouTube transcript: {str(e)}. (Make sure the video has English subtitles/captions enabled)."
