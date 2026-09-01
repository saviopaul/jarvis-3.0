"""
cartoon_generator.py - Multi-Character 2D Cartoon Animation Studio (Jarvis & Dippy)

Features:
1. 100% Fully Responsive Layout (Mobile phones, Android/iPads, Laptops, 4K Desktops)
2. English-Style Phonics Sound & Word-Chopping Engine (क-म-ळ, घ-र, न-ल)
3. Interactive Touch-Friendly Sound Buttons (Click/Tap to hear each chunk & blend!)
4. Dual Character Dialogue (Jarvis Robot ↔ Dippy the Droplet) with distinct voice acting
5. 60 FPS Vector Motion Graphics & Procedural Web Audio Synth
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
    """Uses Gemini 2.5 Flash to generate super simple, English-style Phonics & Pronouns cartoon scripts."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    prompt = (
        f"You are the Lead Kids Cartoon Educator for 10-year-old twin boys Joel & Joshua.\n"
        f"Topic: {topic}\n\n"
        f"CRITICAL RULE: Teach Marathi and Hindi EXACTLY like English Phonics (like C-A-T = CAT).\n"
        f"Keep everything ULTRA SIMPLE, FUN, and PLAYFUL. Absolutely NO hard academic jargon.\n\n"
        f"Generate a valid JSON object with:\n"
        f"{{\n"
        f'  "clean_topic": "Fun Title (e.g. Marathi Phonics & Word-Chopping)",\n'
        f'  "sample_word": "कमळ",\n'
        f'  "word_meaning": "Lotus (Flower)",\n'
        f'  "sound_chunks": ["क (Ka)", "म (Ma)", "ळ (La)"],\n'
        f'  "jarvis_dialogue": "Beep boop! Hello Joel and Joshua! Just like C-A-T makes CAT in English, in Marathi we chop words into sound chunks!",\n'
        f'  "dippy_dialogue": "Yeah! Look at the sounds: Ka... Ma... La! When we blend them, we score a goal: KAMAL! Let\'s pass the ball to Joel and Joshua!",\n'
        f'  "joel_task": "Joel, chop the word \'घर\' (House) into 2 sound chunks: /Gh/ + /R/!",\n'
        f'  "joshua_task": "Joshua, match the English pronoun \'I\' to Marathi: Is it \'मी\' (Mee) or \'तू\' (Too)?",\n'
        f'  "secret_code": "4 - 2 - 8",\n'
        f'  "cliffhanger": "Next time, Dippy and Jarvis unlock the magical Moonwalk Matra powers!"\n'
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
        "clean_topic": "Marathi & Hindi Phonics & Pronouns",
        "sample_word": "कमळ",
        "word_meaning": "Lotus (Flower)",
        "sound_chunks": ["क (Ka)", "म (Ma)", "ळ (La)"],
        "jarvis_dialogue": "Beep boop! Hello Joel and Joshua! Just like C-A-T makes CAT in English, we chop Marathi words into fun sound chunks!",
        "dippy_dialogue": "Woohoo! Let's bounce: Ka... Ma... La! Blend them together and we get KAMAL! Goal scored!",
        "joel_task": "Joel: Chop the word 'घर' into 2 sounds (/Gh/ + /R/)!",
        "joshua_task": "Joshua: Match the English pronoun 'I' ➔ 'मी' (Mee) or 'आम्ही' (We)?",
        "secret_code": "7 - 9 - 2",
        "cliffhanger": "Episode 2: The Magic Moonwalk Matra power is coming tomorrow!"
    }


def generate_interactive_2d_cartoon_webpage(topic: str) -> dict:
    """
    Generates a rich 60 FPS 2D cartoon animation webpage with 100% responsive
    mobile/tablet/desktop layouts, touch-friendly Phonics sound buttons, and dual character dialogue.
    """
    session_id = uuid.uuid4().hex[:8]
    slug = f"cartoon-{session_id}"
    file_path = os.path.join(SITES_DIR, f"{slug}.html")
    
    script_data = _generate_cartoon_script_ai(topic)
    
    clean_title = script_data.get("clean_topic", "Phonics & Word-Chopping")
    sample_word = script_data.get("sample_word", "कमळ")
    word_meaning = script_data.get("word_meaning", "Lotus")
    sound_chunks = script_data.get("sound_chunks", ["क (Ka)", "म (Ma)", "ळ (La)"])
    jarvis_dialogue = script_data.get("jarvis_dialogue", "Beep boop! Let's chop words into phonics sounds!")
    dippy_dialogue = script_data.get("dippy_dialogue", "Woohoo! Ka-Ma-La makes KAMAL!")
    joel_task = script_data.get("joel_task", "Chop the word 'घर' into 2 sounds!")
    joshua_task = script_data.get("joshua_task", "What is the Marathi pronoun for 'I'?")
    secret_code = script_data.get("secret_code", "7 - 9 - 2")
    cliffhanger = script_data.get("cliffhanger", "Magic Matra power unlocked tomorrow!")
    
    sound_buttons_html = ""
    for idx, chunk in enumerate(sound_chunks):
        letter_only = chunk.split()[0]
        sound_buttons_html += f"""
        <button onclick="playPhonicSound('{letter_only}')" class="bg-amber-400 hover:bg-yellow-300 active:scale-95 text-slate-950 font-black px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl sm:rounded-2xl text-base sm:text-lg shadow-lg transition transform border-2 border-white flex flex-col items-center flex-1 min-w-[75px]">
          <span class="text-xl sm:text-2xl font-black">{letter_only}</span>
          <span class="text-[10px] sm:text-xs font-bold text-slate-800">Sound #{idx+1}</span>
        </button>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Jarvis & Dippy: {clean_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes float {{
      0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
      50% {{ transform: translateY(-10px) rotate(2deg); }}
    }}
    @keyframes bounce-char {{
      0%, 100% {{ transform: translateY(0px) scale(1); }}
      50% {{ transform: translateY(-16px) scale(1.05); }}
    }}
    @keyframes pulse-glow {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 10px #38bdf8); }}
      50% {{ transform: scale(1.03); filter: drop-shadow(0 0 20px #facc15); }}
    }}
    @keyframes mouth-talk {{
      0%, 100% {{ height: 3px; }}
      50% {{ height: 14px; }}
    }}
    @keyframes cloud-move {{
      0% {{ transform: translateX(-150px); }}
      100% {{ transform: translateX(110vw); }}
    }}
    .floating {{ animation: float 3s ease-in-out infinite; }}
    .bouncing {{ animation: bounce-char 1.6s ease-in-out infinite; }}
    .pulsing {{ animation: pulse-glow 2s infinite; }}
    .talking-mouth {{ animation: mouth-talk 0.3s infinite; }}
    .moving-cloud-1 {{ animation: cloud-move 20s linear infinite; }}
    .speaking-highlight {{
      box-shadow: 0 0 25px #facc15, 0 0 8px #ffffff;
      border-color: #facc15 !important;
      transform: scale(1.02);
      transition: all 0.3s ease;
    }}
    button {{ touch-action: manipulation; }}
  </style>
</head>
<body class="bg-gradient-to-b from-sky-400 via-indigo-700 to-slate-950 min-h-screen text-white font-sans p-2 sm:p-4 md:p-6 flex flex-col items-center justify-between antialiased">

  <!-- TOP RESPONSIVE HEADER -->
  <header class="w-full max-w-5xl bg-slate-900/95 backdrop-blur border-2 border-yellow-400 rounded-2xl sm:rounded-3xl p-3 sm:p-5 my-2 flex flex-col sm:flex-row items-center justify-between shadow-2xl gap-3 text-center sm:text-left">
    <div class="flex items-center gap-3">
      <span class="text-3xl sm:text-4xl animate-bounce">🪓</span>
      <div>
        <h1 class="text-base sm:text-xl md:text-2xl font-black text-yellow-300 tracking-wide">JARVIS PHONICS ACADEMY</h1>
        <p class="text-xs sm:text-sm text-sky-200">Starring Super Twins: <strong class="text-white font-black">Joel & Joshua</strong> ⚽</p>
      </div>
    </div>
    <div class="bg-emerald-400 text-slate-950 font-black px-3 py-1 sm:px-4 sm:py-1.5 rounded-full text-xs shadow-lg animate-pulse inline-block">
      ENGLISH-STYLE PHONICS
    </div>
  </header>

  <!-- 2D CARTOON STAGE -->
  <main class="w-full max-w-5xl bg-slate-950/85 rounded-2xl sm:rounded-3xl border-2 sm:border-4 border-white/20 p-3 sm:p-6 shadow-2xl flex flex-col items-center justify-between my-2 relative">
    
    <!-- BACKGROUND CLOUDS -->
    <div class="absolute top-4 left-0 moving-cloud-1 opacity-70 pointer-events-none">
      <svg width="100" height="50" viewBox="0 0 120 60" fill="white">
        <circle cx="30" cy="35" r="25"/>
        <circle cx="60" cy="25" r="30"/>
        <circle cx="90" cy="35" r="25"/>
      </svg>
    </div>

    <!-- MISSION BANNER -->
    <div class="bg-indigo-900/90 border-2 border-sky-400 px-4 sm:px-8 py-1.5 sm:py-2.5 rounded-full text-center shadow-xl pulsing z-10 my-1">
      <h2 class="text-xs sm:text-base md:text-lg font-bold text-sky-200">Mission: <span class="text-yellow-300 font-black">{clean_title}</span> 🌟</h2>
    </div>

    <!-- 2D CHARACTERS ROW (RESPONSIVE GRID) -->
    <div class="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-6 my-3 sm:my-5 z-10 relative">
      
      <!-- JARVIS ROBOT CARD -->
      <div id="jarvis-card" class="bg-slate-900/90 border-2 sm:border-4 border-sky-500 rounded-2xl sm:rounded-3xl p-3 sm:p-5 flex items-center gap-3 sm:gap-4 shadow-xl transition-all">
        <div class="flex flex-col items-center floating shrink-0">
          <div class="relative">
            <div class="w-1.5 h-4 sm:h-5 bg-sky-400 mx-auto rounded-t"></div>
            <div class="w-3 h-3 sm:w-3.5 sm:h-3.5 bg-yellow-400 rounded-full mx-auto -mt-1 ring-2 ring-white animate-ping"></div>
            <div class="w-16 h-14 sm:w-20 sm:h-18 bg-slate-800 border-2 sm:border-4 border-sky-400 rounded-xl sm:rounded-2xl flex flex-col items-center justify-center relative shadow-xl p-1 sm:p-2">
              <div class="flex gap-2 mb-1.5">
                <div class="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_6px_#38bdf8]"></div>
                <div class="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-sky-400 rounded-full ring-2 ring-white shadow-[0_0_6px_#38bdf8]"></div>
              </div>
              <div id="jarvis-mouth" class="w-4 sm:w-5 bg-red-500 rounded-full border border-white h-1"></div>
            </div>
          </div>
          <span class="mt-1 text-[10px] sm:text-xs font-black text-sky-300 bg-slate-800 border border-sky-500 px-1.5 py-0.5 rounded-full">🤖 Jarvis</span>
        </div>

        <div class="bg-sky-950/80 border border-sky-400 rounded-xl sm:rounded-2xl p-2.5 sm:p-3.5 flex-1 shadow-inner text-left">
          <h4 class="text-[10px] sm:text-xs font-black text-sky-300 uppercase tracking-wider mb-0.5">🤖 Captain Jarvis:</h4>
          <p id="jarvis-text" class="text-xs sm:text-sm font-semibold text-white leading-tight sm:leading-relaxed">
            "{jarvis_dialogue}"
          </p>
        </div>
      </div>

      <!-- DIPPY DROPLET CARD -->
      <div id="dippy-card" class="bg-slate-900/90 border-2 sm:border-4 border-cyan-500 rounded-2xl sm:rounded-3xl p-3 sm:p-5 flex items-center gap-3 sm:gap-4 shadow-xl transition-all">
        <div class="flex flex-col items-center bouncing shrink-0">
          <div class="relative w-16 h-18 sm:w-20 sm:h-22 flex items-center justify-center">
            <svg viewBox="0 0 100 120" class="w-14 h-16 sm:w-18 sm:h-20 drop-shadow-xl">
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
          <span class="mt-1 text-[10px] sm:text-xs font-black text-cyan-300 bg-slate-800 border border-cyan-500 px-1.5 py-0.5 rounded-full">💧 Dippy</span>
        </div>

        <div class="bg-cyan-950/80 border border-cyan-400 rounded-xl sm:rounded-2xl p-2.5 sm:p-3.5 flex-1 shadow-inner text-left">
          <h4 class="text-[10px] sm:text-xs font-black text-cyan-300 uppercase tracking-wider mb-0.5">💧 Dippy Replies:</h4>
          <p id="dippy-text" class="text-xs sm:text-sm font-semibold text-white leading-tight sm:leading-relaxed">
            "{dippy_dialogue}"
          </p>
        </div>
      </div>

    </div>

    <!-- TOUCH-FRIENDLY WORD-CHOPPING PHONICS LAB -->
    <div class="w-full bg-indigo-950/90 border-2 sm:border-4 border-yellow-400 rounded-2xl sm:rounded-3xl p-3 sm:p-5 my-2 text-center shadow-2xl z-10">
      <h3 class="text-xs sm:text-sm md:text-base font-black text-yellow-300 uppercase tracking-wider mb-1 sm:mb-2">
        🪓 WORD-CHOPPING LAB: <span class="text-white text-sm sm:text-lg bg-indigo-800 px-2.5 py-0.5 rounded-lg border border-sky-400">{sample_word} ({word_meaning})</span>
      </h3>
      <p class="text-[10px] sm:text-xs text-sky-200 mb-3">Tap each sound chunk to hear it, then tap <strong>BLEND & SCORE GOAL</strong>!</p>
      
      <!-- Sound Buttons Row -->
      <div class="flex flex-wrap gap-2 sm:gap-4 items-center justify-center mb-3">
        {sound_buttons_html}
      </div>

      <!-- Blend Button -->
      <div class="flex justify-center">
        <button onclick="playBlendedWord('{sample_word}')" class="w-full sm:w-auto bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-slate-950 font-black px-4 sm:px-6 py-2.5 sm:py-3 rounded-full text-xs sm:text-base shadow-xl transition flex items-center justify-center gap-2 border-2 border-white">
          <span>⚽ BLEND & SCORE GOAL: {sample_word}!</span>
        </button>
      </div>
    </div>

    <!-- 10-SECOND TIME-BOMB (RESPONSIVE GRID) -->
    <div id="challenge-box" class="w-full bg-red-950/90 border-2 sm:border-4 border-red-500 rounded-2xl sm:rounded-3xl p-3 sm:p-5 my-2 text-center z-10 hidden shadow-2xl">
      <h3 class="text-base sm:text-xl font-black text-yellow-300 animate-pulse">💣 10-SECOND TIME-BOMB CHALLENGE! 💣</h3>
      <div class="text-3xl sm:text-4xl font-mono font-black text-red-400 my-1 sm:my-2" id="timer-count">10s</div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-left my-2">
        <!-- Joel's Card -->
        <div class="bg-blue-900/90 p-3 sm:p-4 rounded-xl sm:rounded-2xl border-2 border-sky-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-xs sm:text-sm mb-1 flex items-center gap-1.5">👦 JOEL'S STRIKER ZONE:</h4>
          <p class="text-xs sm:text-sm text-sky-100 font-semibold leading-snug">{joel_task}</p>
        </div>
        <!-- Joshua's Card -->
        <div class="bg-emerald-900/90 p-3 sm:p-4 rounded-xl sm:rounded-2xl border-2 border-emerald-400 shadow-md">
          <h4 class="font-black text-yellow-300 text-xs sm:text-sm mb-1 flex items-center gap-1.5">👦 JOSHUA'S STRIKER ZONE:</h4>
          <p class="text-xs sm:text-sm text-emerald-100 font-semibold leading-snug">{joshua_task}</p>
        </div>
      </div>

      <!-- Victory Reveal Banner -->
      <div id="victory-banner" class="hidden mt-2 p-3 bg-emerald-800 border-2 border-yellow-300 rounded-xl shadow-xl">
        <h4 class="text-sm sm:text-base font-black text-yellow-300">🏆 GOAL SCORED! BRAIN CODE: [{secret_code}]</h4>
        <p class="text-xs text-emerald-100 mt-0.5 font-bold">🕺 Moonwalk Victory Dance! ⚔️ {cliffhanger}</p>
      </div>
    </div>

    <!-- MAIN CONTROL BUTTONS -->
    <div class="flex flex-wrap gap-2 sm:gap-4 items-center justify-center mt-2 z-10 w-full">
      <button onclick="playDualCharacterShow()" class="flex-1 sm:flex-initial bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-slate-950 font-black px-4 sm:px-6 py-2.5 sm:py-3 rounded-full text-xs sm:text-sm flex items-center justify-center gap-2 shadow-2xl transition">
        <span>🎬 Play Jarvis & Dippy Show</span>
      </button>
      <button onclick="startChallenge()" class="flex-1 sm:flex-initial bg-yellow-400 hover:bg-yellow-300 active:scale-95 text-slate-950 font-black px-4 sm:px-6 py-2.5 sm:py-3 rounded-full text-xs sm:text-sm flex items-center justify-center gap-2 shadow-2xl transition">
        <span>⏱️ Start 10s Countdown</span>
      </button>
    </div>

  </main>

  <script>
    const jarvisSpeech = "{jarvis_dialogue}";
    const dippySpeech = "{dippy_dialogue}";

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

    function playPhonicSound(letter) {{
      playBeep(520, 'triangle', 0.15);
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(letter);
        utter.lang = 'mr-IN';
        utter.rate = 0.85;
        window.speechSynthesis.speak(utter);
      }}
    }}

    function playBlendedWord(word) {{
      playBeep(660, 'sine', 0.2);
      setTimeout(() => playBeep(880, 'sine', 0.3), 150);
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(word);
        utter.lang = 'mr-IN';
        utter.rate = 0.9;
        window.speechSynthesis.speak(utter);
      }}
    }}

    function playDualCharacterShow() {{
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      const jarvisCard = document.getElementById("jarvis-card");
      const dippyCard = document.getElementById("dippy-card");
      const jarvisMouth = document.getElementById("jarvis-mouth");

      jarvisCard.classList.add("speaking-highlight");
      dippyCard.classList.remove("speaking-highlight");
      jarvisMouth.classList.add("talking-mouth");
      playBeep(480, 'sawtooth', 0.2);

      const utterance1 = new SpeechSynthesisUtterance(jarvisSpeech);
      utterance1.rate = 0.92;
      utterance1.pitch = 0.75;

      utterance1.onend = () => {{
        jarvisMouth.classList.remove("talking-mouth");
        jarvisCard.classList.remove("speaking-highlight");

        setTimeout(() => {{
          dippyCard.classList.add("speaking-highlight");
          playBeep(880, 'triangle', 0.2);

          const utterance2 = new SpeechSynthesisUtterance(dippySpeech);
          utterance2.rate = 1.15;
          utterance2.pitch = 1.6;

          utterance2.onend = () => {{
            dippyCard.classList.remove("speaking-highlight");
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
      countElem.className = "text-3xl sm:text-4xl font-mono font-black text-red-400 my-1 sm:my-2";
      
      playBeep(520, 'square', 0.2);

      const interval = setInterval(() => {{
        count--;
        if (count > 0) {{
          countElem.innerText = count + "s";
          playBeep(440 + (10 - count)*45, 'sine', 0.1);
        }} else {{
          clearInterval(interval);
          countElem.innerText = "💥 TIME UP! 💥";
          countElem.className = "text-2xl sm:text-3xl font-black text-yellow-300 my-1";
          victory.classList.remove("hidden");
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
