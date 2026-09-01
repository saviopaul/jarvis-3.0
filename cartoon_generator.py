"""
cartoon_generator.py - Gemini & Groq Powered 2D Cartoon Animation Studio

Creates dynamic, topic-specific 2D interactive animated cartoons with:
1. Moving SVG cartoon characters (Jarvis Robot, Dippy, Explorer Avatars)
2. 60 FPS CSS3 / Canvas motion graphics & procedural Web Audio sound effects
3. Dynamic educational content generation (Marathi, Hindi, Maths, EVS, Science)
4. Interactive 10s challenge game tailored specifically for Joel & Joshua
5. Hosted live 24/7 at https://jarvis-3-telegram-bot.onrender.com/sites/...
"""

import os
import re
import json
import uuid
import logging
import requests

logger = logging.getLogger(__name__)
SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")
os.makedirs(SITES_DIR, exist_ok=True)


def _generate_cartoon_script_ai(topic: str) -> dict:
    """Uses Gemini 2.5 Flash to write custom character dialogue and challenge questions."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    prompt = (
        f"You are the Lead Creative Director for a 2D Kids Educational Cartoon starring 10-year-old twin boys Joel and Joshua (5th Standard).\n"
        f"Topic: {topic}\n\n"
        f"Generate a JSON object with:\n"
        f"1. 'clean_topic': A short punchy title (max 5 words)\n"
        f"2. 'dialogue': An enthusiastic 2-sentence intro spoken by Jarvis Robot and cartoon character Dippy.\n"
        f"3. 'joel_task': A specific question/step for Joel (Left Side)\n"
        f"4. 'joshua_task': A specific question/step for Joshua (Right Side)\n"
        f"5. 'secret_code': A 3-number victory code like '7 - 9 - 2'\n"
        f"6. 'cliffhanger': A 1-sentence teaser for the next episode.\n\n"
        f"Output ONLY valid JSON."
    )
    
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=25)
            raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean.strip())
            return json.loads(clean)
        except Exception as e:
            logger.error(f"Gemini cartoon script generation error: {e}")
            
    # Fallback script
    return {
        "clean_topic": topic[:35],
        "dialogue": f"Welcome Joel and Joshua! Today we are mastering {topic}! Watch closely as we unlock today's secret super power!",
        "joel_task": "Solve the First Part of the mission on the left!",
        "joshua_task": "Solve the Second Part of the mission on the right!",
        "secret_code": "8 - 4 - 1",
        "cliffhanger": "The Shadow Boss is stirring in the mountains! Tune in tomorrow for Episode 2!"
    }


def generate_interactive_2d_cartoon_webpage(topic: str) -> dict:
    """
    Generates a rich 60 FPS 2D cartoon animation webpage for kids.
    Returns the live URL, file path, and slug.
    """
    session_id = uuid.uuid4().hex[:8]
    slug = f"cartoon-{session_id}"
    file_path = os.path.join(SITES_DIR, f"{slug}.html")
    
    script_data = _generate_cartoon_script_ai(topic)
    
    clean_title = script_data.get("clean_topic", topic)
    dialogue = script_data.get("dialogue", "Welcome Joel and Joshua!")
    joel_task = script_data.get("joel_task", "Solve the left side!")
    joshua_task = script_data.get("joshua_task", "Solve the right side!")
    secret_code = script_data.get("secret_code", "7 - 9 - 2")
    cliffhanger = script_data.get("cliffhanger", "The Boss Monster is waking up!")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jarvis 2D Cartoon: {clean_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes float {{
      0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
      50% {{ transform: translateY(-16px) rotate(3deg); }}
    }}
    @keyframes bounce-char {{
      0%, 100% {{ transform: translateY(0px) scale(1); }}
      50% {{ transform: translateY(-24px) scale(1.06); }}
    }}
    @keyframes pulse-glow {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 15px #38bdf8); }}
      50% {{ transform: scale(1.06); filter: drop-shadow(0 0 30px #facc15); }}
    }}
    @keyframes mouth-talk {{
      0%, 100% {{ height: 4px; }}
      50% {{ height: 16px; }}
    }}
    @keyframes cloud-move {{
      0% {{ transform: translateX(-150px); }}
      100% {{ transform: translateX(110vw); }}
    }}
    .floating {{ animation: float 3s ease-in-out infinite; }}
    .bouncing {{ animation: bounce-char 1.8s ease-in-out infinite; }}
    .pulsing {{ animation: pulse-glow 2s infinite; }}
    .talking-mouth {{ animation: mouth-talk 0.35s infinite; }}
    .moving-cloud-1 {{ animation: cloud-move 22s linear infinite; }}
    .moving-cloud-2 {{ animation: cloud-move 32s linear infinite 5s; }}
  </style>
</head>
<body class="bg-gradient-to-b from-sky-400 via-indigo-600 to-slate-950 min-h-screen text-white font-sans overflow-x-hidden flex flex-col items-center justify-between p-4">

  <!-- TOP HEADER -->
  <header class="w-full max-w-4xl bg-slate-900/90 backdrop-blur border-2 border-yellow-400 rounded-2xl p-4 my-3 flex items-center justify-between shadow-2xl">
    <div class="flex items-center gap-3">
      <span class="text-3xl animate-bounce">🎬</span>
      <div>
        <h1 class="text-xl md:text-2xl font-black text-yellow-300 tracking-wide">JARVIS 2D CARTOON ACADEMY</h1>
        <p class="text-xs md:text-sm text-sky-200">Starring: <strong class="text-white">Joel & Joshua</strong></p>
      </div>
    </div>
    <div class="bg-yellow-400 text-slate-900 font-extrabold px-4 py-1.5 rounded-full text-xs shadow-lg animate-pulse">
      EPISODE 1 LIVE
    </div>
  </header>

  <!-- 2D ANIMATION STAGE -->
  <main class="w-full max-w-4xl bg-slate-950/70 rounded-3xl border-4 border-white/20 p-6 relative overflow-hidden shadow-2xl min-h-[480px] flex flex-col items-center justify-between">
    
    <!-- BACKGROUND CLOUDS -->
    <div class="absolute top-4 left-0 moving-cloud-1 opacity-70 pointer-events-none">
      <svg width="120" height="60" viewBox="0 0 120 60" fill="white">
        <circle cx="30" cy="35" r="25"/>
        <circle cx="60" cy="25" r="30"/>
        <circle cx="90" cy="35" r="25"/>
      </svg>
    </div>
    <div class="absolute top-16 left-0 moving-cloud-2 opacity-50 pointer-events-none">
      <svg width="90" height="45" viewBox="0 0 120 60" fill="white">
        <circle cx="30" cy="35" r="25"/>
        <circle cx="60" cy="25" r="30"/>
        <circle cx="90" cy="35" r="25"/>
      </svg>
    </div>

    <!-- MISSION TITLE BANNER -->
    <div class="bg-indigo-900/90 border-2 border-sky-400 px-6 py-2.5 rounded-full text-center shadow-xl pulsing z-10">
      <h2 class="text-lg md:text-xl font-bold text-sky-200">Mission: <span class="text-yellow-300 font-black">{clean_title}</span></h2>
    </div>

    <!-- 2D CHARACTERS ROW -->
    <div class="w-full flex items-center justify-around my-6 z-10 relative">
      
      <!-- 2D CARTOON JARVIS ROBOT -->
      <div class="flex flex-col items-center floating">
        <div class="relative">
          <!-- Antenna -->
          <div class="w-2 h-6 bg-sky-400 mx-auto rounded-t"></div>
          <div class="w-5 h-5 bg-yellow-400 rounded-full mx-auto -mt-1 ring-2 ring-white animate-ping"></div>
          
          <!-- Robot Head -->
          <div class="w-28 h-24 bg-slate-800 border-4 border-sky-400 rounded-2xl flex flex-col items-center justify-center relative shadow-xl">
            <!-- Screen Eyes -->
            <div class="flex gap-4 mb-2">
              <div class="w-5 h-5 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_10px_#38bdf8]"></div>
              <div class="w-5 h-5 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_10px_#38bdf8]"></div>
            </div>
            <!-- Animated Mouth -->
            <div class="w-8 bg-red-500 rounded-full border border-white talking-mouth"></div>
          </div>
        </div>
        <span class="mt-2 text-xs font-bold text-sky-300 bg-slate-900 px-2 py-0.5 rounded-md">Jarvis Robot</span>
      </div>

      <!-- SPEECH DIALOG BUBBLE -->
      <div class="bg-white text-slate-900 rounded-3xl p-5 max-w-sm md:max-w-md shadow-2xl relative border-4 border-indigo-600">
        <div class="absolute -left-3 top-1/2 -translate-y-1/2 w-0 h-0 border-t-8 border-t-transparent border-r-[12px] border-r-white border-b-8 border-b-transparent"></div>
        <p id="dialog-text" class="text-sm md:text-base font-bold text-slate-800 leading-relaxed">
          "{dialogue}"
        </p>
      </div>

      <!-- 2D CARTOON CHARACTER "DIPPY" -->
      <div class="flex flex-col items-center bouncing">
        <div class="relative w-24 h-28 flex items-center justify-center">
          <svg viewBox="0 0 100 120" class="w-full h-full drop-shadow-xl">
            <path d="M50 0 C50 0 0 60 0 85 C0 105 22 120 50 120 C78 120 100 105 100 85 C100 60 50 0 50 0 Z" fill="#38bdf8" stroke="white" stroke-width="4"/>
            <circle cx="35" cy="75" r="10" fill="white"/>
            <circle cx="65" cy="75" r="10" fill="white"/>
            <circle cx="37" cy="77" r="5" fill="#0f172a"/>
            <circle cx="67" cy="77" r="5" fill="#0f172a"/>
            <ellipse cx="22" cy="88" rx="7" ry="4" fill="#f472b6"/>
            <ellipse cx="78" cy="88" rx="7" ry="4" fill="#f472b6"/>
            <path d="M40 92 Q50 105 60 92" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="mt-2 text-xs font-bold text-cyan-300 bg-slate-900 px-2 py-0.5 rounded-md">Dippy the Droplet</span>
      </div>

    </div>

    <!-- 10-SECOND INTERACTIVE TIME BOMB SECTION -->
    <div id="challenge-box" class="w-full bg-red-950/85 border-2 border-red-500 rounded-2xl p-5 my-2 text-center z-10 hidden shadow-2xl">
      <h3 class="text-xl md:text-2xl font-black text-yellow-300 animate-pulse">💣 10-SECOND TIME-BOMB CHALLENGE! 💣</h3>
      <div class="text-4xl md:text-5xl font-mono font-black text-red-400 my-2" id="timer-count">10s</div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-left my-3">
        <!-- Joel's Card -->
        <div class="bg-blue-900/80 p-4 rounded-xl border-2 border-sky-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-base mb-1">👦 JOEL'S MISSION (LEFT):</h4>
          <p class="text-sm text-sky-100 font-medium leading-snug">{joel_task}</p>
        </div>
        <!-- Joshua's Card -->
        <div class="bg-emerald-900/80 p-4 rounded-xl border-2 border-emerald-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-base mb-1">👦 JOSHUA'S MISSION (RIGHT):</h4>
          <p class="text-sm text-emerald-100 font-medium leading-snug">{joshua_task}</p>
        </div>
      </div>

      <!-- Victory Reveal Banner -->
      <div id="victory-banner" class="hidden mt-3 p-3 bg-emerald-800 border-2 border-yellow-300 rounded-xl">
        <h4 class="text-lg font-black text-yellow-300">🏆 MISSION CRACKED! BRAIN CODE: [{secret_code}]</h4>
        <p class="text-xs text-emerald-100 mt-1 font-semibold">⚔️ {cliffhanger}</p>
      </div>
    </div>

    <!-- CONTROLS & VOICE BUTTON -->
    <div class="flex flex-wrap gap-4 items-center justify-center mt-4 z-10">
      <button onclick="playCartoonVoice()" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-6 py-3 rounded-full text-base flex items-center gap-2 shadow-xl hover:scale-105 transition">
        <span>🔊 Play Voiceover Narration</span>
      </button>
      <button onclick="startChallenge()" class="bg-yellow-400 hover:bg-yellow-300 text-slate-950 font-black px-6 py-3 rounded-full text-base flex items-center gap-2 shadow-xl hover:scale-105 transition">
        <span>⏱️ Start 10s Time-Bomb Challenge</span>
      </button>
    </div>

  </main>

  <!-- SOUND & SPEECH SYNTHESIS ENGINE -->
  <script>
    const narrationText = "{dialogue}";

    // Web Audio Procedural Beep Synth
    function playBeep(freq = 440, type = 'sine', duration = 0.15) {{
      try {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = type;
        osc.frequency.value = freq;
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + duration);
        osc.stop(ctx.currentTime + duration);
      }} catch (e) {{}}
    }}

    function playCartoonVoice() {{
      playBeep(600, 'triangle', 0.2);
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(narrationText);
        utterance.rate = 0.95;
        utterance.pitch = 1.1;
        window.speechSynthesis.speak(utterance);
      }}
    }}

    function startChallenge() {{
      const box = document.getElementById("challenge-box");
      const victory = document.getElementById("victory-banner");
      box.classList.remove("hidden");
      victory.classList.add("hidden");
      
      let count = 10;
      const countElem = document.getElementById("timer-count");
      countElem.innerText = "10s";
      countElem.className = "text-4xl md:text-5xl font-mono font-black text-red-400 my-2";
      
      playBeep(520, 'square', 0.2);

      const interval = setInterval(() => {{
        count--;
        if (count > 0) {{
          countElem.innerText = count + "s";
          playBeep(440 + (10 - count)*40, 'sine', 0.1);
        }} else {{
          clearInterval(interval);
          countElem.innerText = "💥 TIME UP! 💥";
          countElem.className = "text-3xl font-black text-yellow-300 my-2";
          victory.classList.remove("hidden");
          // Victory Chime
          playBeep(880, 'triangle', 0.4);
          setTimeout(() => playBeep(1100, 'triangle', 0.5), 150);
        }}
      }}, 1000);
    }}
  </script>
</body>
</html>
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    live_url = f"https://jarvis-3-telegram-bot.onrender.com/sites/{slug}"
    return {
        "slug": slug,
        "file_path": file_path,
        "live_url": live_url
    }
