"""
video_engine.py - Automated Educational Cartoon MP4 Video Generator

Generates complete animated learning video clips with voice narration,
visual graphic slides, interactive checkpoints, and cliffhangers!
"""

import os
import re
import json
import uuid
import logging
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

logger = logging.getLogger(__name__)
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)


def _get_font(size: int, bold: bool = False):
    """Loads appropriate system font across Windows and Linux Docker."""
    font_candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf"
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _create_slide_image(title: str, body_lines: list, bg_color: tuple, badge: str, output_path: str):
    """Generates a vibrant, high-contrast 1280x720 graphic slide."""
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Outer Glow / Double Border
    draw.rectangle([15, 15, width - 15, height - 15], outline=(255, 255, 255), width=5)
    draw.rectangle([25, 25, width - 25, height - 25], outline=(255, 215, 0), width=2)
    
    font_badge = _get_font(34, bold=True)
    font_title = _get_font(52, bold=True)
    font_body = _get_font(38, bold=False)
    
    # Badge Pill Header
    draw.rounded_rectangle([50, 45, 650, 105], radius=15, fill=(0, 0, 0, 180), outline=(255, 215, 0), width=3)
    draw.text((70, 55), f"⭐ {badge.upper()} ⭐", fill=(255, 230, 0), font=font_badge)
    
    # Title
    draw.text((55, 135), title, fill=(255, 255, 255), font=font_title)
    
    # Glowing Divider Line
    draw.line([(55, 215), (width - 55, 215)], fill=(255, 215, 0), width=5)
    
    # Content Card Background
    draw.rounded_rectangle([50, 245, width - 50, height - 50], radius=20, fill=(10, 25, 47, 200), outline=(255, 255, 255), width=2)
    
    # Body Bullets
    y = 280
    for line in body_lines:
        draw.text((80, y), line, fill=(245, 245, 245), font=font_body)
        y += 75
        
    image.save(output_path, "PNG")


def create_educational_video(topic: str, for_twins: bool = True) -> str:
    """
    Generates a 3-scene educational cartoon MP4 video with spoken voiceover.
    Returns the absolute path to the generated MP4 file.
    """
    session_id = uuid.uuid4().hex[:8]
    temp_dir = os.path.join(VIDEOS_DIR, session_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    audience = "Joel & Joshua" if for_twins else "Kids"
    
    # Define 3 rich scenes
    scenes = [
        {
            "badge": "JARVIS ACADEMY • BUILT BY SAVIO PAUL",
            "title": f"The Mission: {topic[:38]}",
            "bg": (15, 45, 85), # Midnight Navy
            "bullets": [
                "🤖 Built by Father Savio Paul as your Companion & Tutor!",
                f"🎯 Special Learning Mission for {audience}!",
                "⏱️ Pay attention to the 10-Second Time Bomb Challenge!"
            ],
            "narration": f"Hi Joel and Joshua! I am Jarvis, built by your father Savio Paul. I was made to be your companion and tutor for all subjects! Today we are tackling {topic}. Watch carefully because a mystery challenge is waiting for you at the end!"
        },
        {
            "badge": "10-SECOND TIME-BOMB CHALLENGE",
            "title": "Pause & Solve: Time Bomb Ticking!",
            "bg": (115, 20, 20), # Crimson Red
            "bullets": [
                "💣 TIME BOMB TICKING: 10 SECONDS!",
                "👉 Joel: Solve the Left Side equation!",
                "👉 Joshua: Solve the Right Side equation!",
                "💥 Hit PAUSE on your screen right now!"
            ],
            "narration": "Challenge Alert! Pause this video right now. Joel, take the left side; Joshua, take the right side. You have 10 seconds before the time bomb explodes. Ready, set, pause!"
        },
        {
            "badge": "EPIC CLIFFHANGER • NEXT EPISODE",
            "title": "Mystery Solved • Code: [ 7 - 9 - 2 ]",
            "bg": (15, 80, 45), # Emerald Green
            "bullets": [
                "🏆 VICTORY! Brain Code: [ 7 - 9 - 2 ] Unlocked!",
                "⚔️ ALERT: The Boss Monster is waking up!",
                "🍿 Subscribe & tune in tomorrow for Episode 2!"
            ],
            "narration": "Boom! You solved it! Your Secret Brain Code is 7, 9, 2. But wait, what is that sound? The Boss Monster is waking up! Find out what happens in Episode 2 tomorrow!"
        }
    ]
    
    clips = []
    
    for i, scene in enumerate(scenes):
        img_path = os.path.join(temp_dir, f"slide_{i}.png")
        audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
        
        # 1. Draw High-Res Slide Image
        _create_slide_image(scene["title"], scene["bullets"], scene["bg"], scene["badge"], img_path)
        
        # 2. Generate Audio with gTTS
        tts = gTTS(text=scene["narration"], lang='en', tld='co.in', slow=False)
        tts.save(audio_path)
        
        # 3. Create Video Clip with MoviePy
        audio_clip = AudioFileClip(audio_path)
        duration = max(audio_clip.duration + 0.5, 4.0)
        img_clip = ImageClip(img_path).set_duration(duration).set_audio(audio_clip)
        clips.append(img_clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    output_video_path = os.path.join(VIDEOS_DIR, f"jarvis_video_{session_id}.mp4")
    
    final_video.write_videofile(
        output_video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"),
        remove_temp=True,
        logger=None
    )
    
    # Close clips
    for c in clips:
        c.close()
    final_video.close()
    
    return output_video_path
