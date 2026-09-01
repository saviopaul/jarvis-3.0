"""
cartoon_generator.py - Multi-Character 2D Cartoon Animation Studio (Jarvis & Dippy)

Features:
1. True Back-and-Forth Multi-Character Dialogue (Jarvis Robot ↔ Dippy the Droplet)
2. Distinct Voice Acting (Robot deep pitch for Jarvis vs Playful high pitch for Dippy)
3. Synchronized Character Highlighting & Talking Animations
4. Football & Michael Jackson victory dance interactive challenges
5. 60 FPS HTML5/Canvas/CSS3 Vector Animation Player
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
        f"You are the Lead Cartoon Director for an animated YouTube-style 2D show starring:\n"
        f"1. JARVIS ROBOT (Deep, friendly, smart AI coach)\n"
        f"2. DIPPY THE DROPLET (High-energy, funny, bouncing cartoon mascot who loves football & dancing)\n"
        f"Audience: 10-year-old twin brothers Joel and Joshua (5th Standard).\n"
        f"Topic: {topic}\n\n"
        f"Generate a JSON object with this exact structure:\n"
        f"{{\n"
        f'  "clean_topic": "Punchy Topic Title",\n'
        f'  "jarvis_dialogue": "Jarvis Robot speaking directly to Joel and Joshua about the mission.",\n'
        f'  "dippy_dialogue": "Dippy responding excitedly with football energy or fun analogies.",\n'
        f'  "joel_task": "Specific task/question for Joel on the left side",\n'
        f'  "joshua_task": "Specific task/question for Joshua on the right side",\n'
        f'  "secret_code": "7 - 9 - 2",\n'
        f'  "cliffhanger": "Thrilling 1-sentence teaser for Episode 2."\n'
        f"}}\n"
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
        "jarvis_dialogue": f"Beep boop! Greetings, Joel and Joshua! Captain Jarvis reporting for duty. Today we are unlocking the secret science of {topic}!",
        "dippy_dialogue": f"Woohoo! Pass the football to me! I'm Dippy, and I'm ready to score some mega goals with Joel and Joshua!",
        "joel_task": "Joel, solve Step 1 on the left side before the bomb explodes!",
        "joshua_task": "Joshua, tackle Step 2 on the right side to crack the victory code!",
        "secret_code": "9 - 3 - 7",
        "cliffhanger": "The Volcano Boss is awakening! Will the twins score the winning goal tomorrow in Episode 2?"
    }


def generate_interactive_2d_cartoon_webpage(topic: str) -> dict:
    """
    Generates a rich 60 FPS 2D cartoon animation webpage with interactive
    dialogue between Jarvis Robot and Dippy.
    """
    session_id = uuid.uuid4().hex[:8]
    slug = f"cartoon-{session_id}"
    file_path = os.path.join(SITES_DIR, f"{slug}.html")
    
    script_data = _generate_cartoon_script_ai(topic)
    
    clean_title = script_data.get("clean_topic", topic)
    jarvis_dialogue = script_data.get("jarvis_dialogue", "Beep boop! Greetings Joel and Joshua!")
    dippy_dialogue = script_data.get("dippy_dialogue", "Woohoo! Let's play and learn!")
    joel_task = script_data.get("joel_task", "Solve the left side!")
    joshua_task = script_data.get("joshua_task", "Solve the right side!")
    secret_code = script_data.get("secret_code", "7 - 9 - 2")
    cliffhanger = script_data.get("cliffhanger", "The Boss Monster is waking up!")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jarvis & Dippy 2D Cartoon: {clean_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes float {{
      0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
      50% {{ transform: translateY(-16px) rotate(3deg); }}
    }}
    @keyframes bounce-char {{
      0%, 100% {{ transform: translateY(0px) scale(1); }}
      50% {{ transform: translateY(-26px) scale(1.08); }}
    }}
    @keyframes pulse-glow {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 15px #38bdf8); }}
      50% {{ transform: scale(1.06); filter: drop-shadow(0 0 30px #facc15); }}
    }}
    @keyframes mouth-talk {{
      0%, 100% {{ height: 4px; }}
      50% {{ height: 18px; }}
    }}
    @keyframes cloud-move {{
      0% {{ transform: translateX(-150px); }}
      100% {{ transform: translateX(110vw); }}
    }}
    @keyframes football-kick {{
      0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
      50% {{ transform: translate(260px, -90px) rotate(720deg); }}
    }}
    .floating {{ animation: float 3s ease-in-out infinite; }}
    .bouncing {{ animation: bounce-char 1.6s ease-in-out infinite; }}
    .pulsing {{ animation: pulse-glow 2s infinite; }}
    .talking-mouth {{ animation: mouth-talk 0.3s infinite; }}
    .moving-cloud-1 {{ animation: cloud-move 20s linear infinite; }}
    .moving-cloud-2 {{ animation: cloud-move 30s linear infinite 4s; }}
    .kicking-ball {{ animation: football-kick 3.5s ease-in-out infinite; }}
    .speaking-highlight {{
      box-shadow: 0 0 35px #facc15, 0 0 10px #ffffff;
      border-color: #facc15 !important;
      transform: scale(1.05);
      transition: all 0.3s ease;
    }}
  </style>
</head>
<body class="bg-gradient-to-b from-sky-400 via-indigo-700 to-slate-950 min-h-screen text-white font-sans overflow-x-hidden flex flex-col items-center justify-between p-4">

  <!-- TOP HEADER -->
  <header class="w-full max-w-5xl bg-slate-900/90 backdrop-blur border-2 border-yellow-400 rounded-2xl p-4 my-3 flex items-center justify-between shadow-2xl">
    <div class="flex items-center gap-3">
      <span class="text-4xl animate-bounce">⚽</span>
      <div>
        <h1 class="text-xl md:text-2xl font-black text-yellow-300 tracking-wide">JARVIS & DIPPY 2D CARTOON STUDIO</h1>
        <p class="text-xs md:text-sm text-sky-200">Starring Super Twins: <strong class="text-white font-black">Joel & Joshua</strong> 🕺</p>
      </div>
    </div>
    <div class="bg-yellow-400 text-slate-950 font-black px-4 py-1.5 rounded-full text-xs shadow-lg animate-pulse">
      EPISODE 1 • DUAL CHARACTER
    </div>
  </header>

  <!-- 2D CARTOON STAGE -->
  <main class="w-full max-w-5xl bg-slate-950/75 rounded-3xl border-4 border-white/20 p-6 relative overflow-hidden shadow-2xl min-h-[520px] flex flex-col items-center justify-between">
    
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

    <!-- MISSION BANNER -->
    <div class="bg-indigo-900/90 border-2 border-sky-400 px-8 py-2.5 rounded-full text-center shadow-xl pulsing z-10">
      <h2 class="text-lg md:text-xl font-bold text-sky-200">Mission: <span class="text-yellow-300 font-black">{clean_title}</span> 🏆</h2>
    </div>

    <!-- 2D INTERACTIVE CHARACTERS ROW -->
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-8 my-6 z-10 relative">
      
      <!-- CHARACTER 1: JARVIS ROBOT & DIALOGUE -->
      <div id="jarvis-card" class="bg-slate-900/90 border-4 border-sky-500 rounded-3xl p-5 flex items-center gap-5 shadow-2xl transition-all">
        <!-- Animated Jarvis Robot -->
        <div class="flex flex-col items-center floating shrink-0">
          <div class="relative">
            <div class="w-2 h-6 bg-sky-400 mx-auto rounded-t"></div>
            <div class="w-4 h-4 bg-yellow-400 rounded-full mx-auto -mt-1 ring-2 ring-white animate-ping"></div>
            <div class="w-24 h-22 bg-slate-800 border-4 border-sky-400 rounded-2xl flex flex-col items-center justify-center relative shadow-xl p-2">
              <div class="flex gap-3 mb-2">
                <div class="w-4 h-4 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_8px_#38bdf8]"></div>
                <div class="w-4 h-4 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_8px_#38bdf8]"></div>
              </div>
              <div id="jarvis-mouth" class="w-7 bg-red-500 rounded-full border border-white h-1.5"></div>
            </div>
          </div>
          <span class="mt-2 text-xs font-black text-sky-300 bg-slate-800 border border-sky-500 px-2.5 py-0.5 rounded-full">🤖 Jarvis Robot</span>
        </div>

        <!-- Jarvis Speech Bubble -->
        <div class="bg-sky-950/80 border-2 border-sky-400 rounded-2xl p-4 flex-1 shadow-inner relative">
          <h4 class="text-xs font-black text-sky-300 uppercase tracking-wider mb-1">🤖 Captain Jarvis Says:</h4>
          <p id="jarvis-text" class="text-sm font-semibold text-white leading-relaxed">
            "{jarvis_dialogue}"
          </p>
        </div>
      </div>

      <!-- CHARACTER 2: DIPPY THE WATER DROPLET & DIALOGUE -->
      <div id="dippy-card" class="bg-slate-900/90 border-4 border-cyan-500 rounded-3xl p-5 flex items-center gap-5 shadow-2xl transition-all">
        <!-- Animated Dippy -->
        <div class="flex flex-col items-center bouncing shrink-0">
          <div class="relative w-22 h-26 flex items-center justify-center">
            <svg viewBox="0 0 100 120" class="w-20 h-24 drop-shadow-xl">
              <path d="M50 0 C50 0 0 60 0 85 C0 105 22 120 50 120 C78 120 100 105 100 85 C100 60 50 0 50 0 Z" fill="#38bdf8" stroke="white" stroke-width="4"/>
              <circle cx="35" cy="75" r="10" fill="white"/>
              <circle cx="65" cy="75" r="10" fill="white"/>
              <circle cx="37" cy="77" r="5" fill="#0f172a"/>
              <circle cx="67" cy="77" r="5" fill="#0f172a"/>
              <ellipse cx="22" cy="88" rx="7" ry="4" fill="#f472b6"/>
              <ellipse cx="78" cy="88" rx="7" ry="4" fill="#f472b6"/>
              <path id="dippy-mouth" d="M40 92 Q50 106 60 92" stroke="#0f172a" stroke-width="4" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="mt-2 text-xs font-black text-cyan-300 bg-slate-800 border border-cyan-500 px-2.5 py-0.5 rounded-full">💧 Dippy Droplet</span>
        </div>

        <!-- Dippy Speech Bubble -->
        <div class="bg-cyan-950/80 border-2 border-cyan-400 rounded-2xl p-4 flex-1 shadow-inner relative">
          <h4 class="text-xs font-black text-cyan-300 uppercase tracking-wider mb-1">💧 Dippy Replies:</h4>
          <p id="dippy-text" class="text-sm font-semibold text-white leading-relaxed">
            "{dippy_dialogue}"
          </p>
        </div>
      </div>

    </div>

    <!-- 10-SECOND INTERACTIVE TIME BOMB SECTION -->
    <div id="challenge-box" class="w-full bg-red-950/90 border-4 border-red-500 rounded-3xl p-5 my-2 text-center z-10 hidden shadow-2xl">
      <h3 class="text-xl md:text-2xl font-black text-yellow-300 animate-pulse">💣 10-SECOND TIME-BOMB CHALLENGE! 💣</h3>
      <div class="text-4xl md:text-5xl font-mono font-black text-red-400 my-2" id="timer-count">10s</div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-left my-3">
        <!-- Joel's Card -->
        <div class="bg-blue-900/90 p-4 rounded-2xl border-2 border-sky-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-base mb-1 flex items-center gap-2">👦 JOEL'S STRIKER ZONE (LEFT):</h4>
          <p class="text-sm text-sky-100 font-medium leading-snug">{joel_task}</p>
        </div>
        <!-- Joshua's Card -->
        <div class="bg-emerald-900/90 p-4 rounded-2xl border-2 border-emerald-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-base mb-1 flex items-center gap-2">👦 JOSHUA'S STRIKER ZONE (RIGHT):</h4>
          <p class="text-sm text-emerald-100 font-medium leading-snug">{joshua_task}</p>
        </div>
      </div>

      <!-- Victory Reveal Banner -->
      <div id="victory-banner" class="hidden mt-3 p-4 bg-emerald-800 border-3 border-yellow-300 rounded-2xl shadow-xl">
        <h4 class="text-xl font-black text-yellow-300">🏆 GOAL SCORED! BRAIN CODE: [{secret_code}]</h4>
        <p class="text-sm text-emerald-100 mt-1 font-bold">🕺 Moonwalk Victory Dance! ⚔️ {cliffhanger}</p>
      </div>
    </div>

    <!-- CONTROLS & DUAL VOICE PLAYBACK -->
    <div class="flex flex-wrap gap-4 items-center justify-center mt-4 z-10">
      <button onclick="playDualCharacterShow()" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-7 py-3.5 rounded-full text-base flex items-center gap-3 shadow-2xl hover:scale-105 transition">
        <span>🎬 Play Jarvis & Dippy 2D Show</span>
      </button>
      <button onclick="startChallenge()" class="bg-yellow-400 hover:bg-yellow-300 text-slate-950 font-black px-7 py-3.5 rounded-full text-base flex items-center gap-3 shadow-2xl hover:scale-105 transition">
        <span>⏱️ Start 10s Time-Bomb Challenge</span>
      </button>
    </div>

  </main>

  <!-- MULTI-VOICE SYNTHESIS & DUAL ANIMATION SCRIPT -->
  <script>
    const jarvisSpeech = "{jarvis_dialogue}";
    const dippySpeech = "{dippy_dialogue}";

    // Web Audio Synthesizer
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

    function playDualCharacterShow() {{
      if (!('speechSynthesis' in window)) {{
        alert("Speech synthesis is active on your device!");
        return;
      }}
      window.speechSynthesis.cancel();

      const jarvisCard = document.getElementById("jarvis-card");
      const dippyCard = document.getElementById("dippy-card");
      const jarvisMouth = document.getElementById("jarvis-mouth");

      // ── STEP 1: JARVIS SPEAKS (Deep, Friendly Robot Pitch) ──
      jarvisCard.classList.add("speaking-highlight");
      dippyCard.classList.remove("speaking-highlight");
      jarvisMouth.classList.add("talking-mouth");
      playBeep(480, 'sawtooth', 0.2);

      const utterance1 = new SpeechSynthesisUtterance(jarvisSpeech);
      utterance1.rate = 0.92;
      utterance1.pitch = 0.75; // Deep Robot Voice

      utterance1.onend = () => {{
        jarvisMouth.classList.remove("talking-mouth");
        jarvisCard.classList.remove("speaking-highlight");

        // ── STEP 2: DIPPY RESPONDS (Playful, High-Energy Cartoon Voice) ──
        setTimeout(() => {{
          dippyCard.classList.add("speaking-highlight");
          playBeep(880, 'triangle', 0.2);

          const utterance2 = new SpeechSynthesisUtterance(dippySpeech);
          utterance2.rate = 1.15;
          utterance2.pitch = 1.6; // High Cartoon Mascot Voice

          utterance2.onend = () => {{
            dippyCard.classList.remove("speaking-highlight");
            // Auto prompt the challenge
            startChallenge();
          }};

          window.speechSynthesis.speak(utterance2);
        }}, 400);
      }};

      window.speechSynthesis.speak(utterance1);
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
          playBeep(440 + (10 - count)*45, 'sine', 0.1);
        }} else {{
          clearInterval(interval);
          countElem.innerText = "💥 TIME UP! 💥";
          countElem.className = "text-3xl font-black text-yellow-300 my-2";
          victory.classList.remove("hidden");
          // Victory Fanfare
          playBeep(784, 'triangle', 0.3);
          setTimeout(() => playBeep(987, 'triangle', 0.3), 150);
          setTimeout(() => playBeep(1318, 'triangle', 0.5), 300);
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
