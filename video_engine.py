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


def _create_slide_image(title: str, body_lines: list, bg_color: tuple, badge: str, output_path: str):
    """Generates a vibrant 1280x720 graphic slide."""
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw decorative border
    draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255), width=6)
    
    # Try to load a nice font, fallback to default
    try:
        font_badge = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 34)
    except Exception:
        try:
            font_badge = ImageFont.truetype("arial.ttf", 36)
            font_title = ImageFont.truetype("arialbd.ttf", 48)
            font_body = ImageFont.truetype("arial.ttf", 34)
        except Exception:
            font_badge = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
        
    # Draw Badge
    draw.text((60, 60), f"⭐ {badge.upper()} ⭐", fill=(255, 230, 0), font=font_badge)
    
    # Draw Title
    draw.text((60, 130), title, fill=(255, 255, 255), font=font_title)
    
    # Draw Divider
    draw.line([(60, 210), (width - 60, 210)], fill=(255, 255, 255), width=4)
    
    # Draw Body Content
    y = 260
    for line in body_lines:
        draw.text((60, y), line, fill=(240, 240, 240), font=font_body)
        y += 65
        
    image.save(output_path, "PNG")


def create_educational_video(topic: str, for_twins: bool = True) -> str:
    """
    Generates a 3-scene educational cartoon MP4 video with spoken voiceover.
    Returns the absolute path to the generated MP4 file.
    """
    session_id = uuid.uuid4().hex[:8]
    temp_dir = os.path.join(VIDEOS_DIR, session_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    audience = "Joel & Joshua (10-year-old twin boys)" if for_twins else "Kids"
    
    # Define 3 scenes
    scenes = [
        {
            "badge": "JARVIS ACADEMY • EPISODE 1",
            "title": f"The Mission: {topic[:35]}",
            "bg": (26, 82, 118), # Deep Blue
            "bullets": [
                f"🎯 Explorer Mission for {audience}!",
                "💡 Secret Discovery: Learn the Master Trick",
                "⏱️ Watch closely to unlock the Secret Brain Code!"
            ],
            "narration": f"Welcome Joel and Joshua to today's Jarvis Adventure! Today we are tackling {topic}. Watch carefully because a mystery challenge is waiting for you at the end!"
        },
        {
            "badge": "INTERACTIVE BRAIN CHALLENGE",
            "title": "Pause & Solve: The 10s Time-Bomb!",
            "bg": (120, 40, 31), # Deep Crimson / Red
            "bullets": [
                "💣 TIME BOMB TICKING: 10 SECONDS!",
                "👉 Joel, solve the left side!",
                "👉 Joshua, solve the right side!",
                "💥 Press Pause on your screen right now!"
            ],
            "narration": "Challenge Alert! Pause this video right now. Joel, take the left side; Joshua, take the right side. You have 10 seconds before the time bomb explodes. Ready, set, pause!"
        },
        {
            "badge": "EPIC CLIFFHANGER",
            "title": "Mystery Unlocked • Next Episode!",
            "bg": (20, 90, 50), # Deep Emerald Green
            "bullets": [
                "🏆 VICTORY! Brain Code: [ 7 - 9 - 2 ]",
                "⚔️ Warning: The Boss Monster is approaching!",
                "🍿 Subscribe & tune in tomorrow for Episode 2!"
            ],
            "narration": "Boom! You solved it! Your Secret Brain Code is 7, 9, 2. But wait, what is that sound? The Boss Monster is waking up! Find out what happens in Episode 2 tomorrow!"
        }
    ]
    
    clips = []
    
    for i, scene in enumerate(scenes):
        img_path = os.path.join(temp_dir, f"slide_{i}.png")
        audio_path = os.path.join(temp_dir, f"audio_{i}.mp3")
        
        # 1. Draw Slide Image
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
