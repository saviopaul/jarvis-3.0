import os
import logging
from dotenv import load_dotenv
from flask import Flask, request
import telebot
from brain import process_message
from self_heal import self_heal
from providers import approve_switch, deny_switch, is_awaiting_approval

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

token = os.environ.get("TELEGRAM_TOKEN")
if not token:
    logger.error("TELEGRAM_TOKEN not found.")
    exit(1)

bot = telebot.TeleBot(token)
app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Hey! Jarvis 3.0 here.\n"
        "I am your trusted buddy, running 24/7 in the cloud.\n"
        "Talk to me about anything — work, life, code, or just venting."
    )

def _send_safe_reply(chat_id: int, msg_id: int, text: str):
    """Safely edits the thinking message, or sends multiple chunks if text > 4000 chars."""
    MAX_LEN = 3900
    chunks = [text[i:i + MAX_LEN] for i in range(0, len(text), MAX_LEN)] if len(text) > MAX_LEN else [text]
    
    # Edit the first message with chunk 0
    try:
        bot.edit_message_text(chunks[0], chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
    except Exception:
        try:
            bot.edit_message_text(chunks[0], chat_id=chat_id, message_id=msg_id)  # plain text fallback
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")

    # Send remaining chunks as new messages
    for chunk in chunks[1:]:
        try:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id=chat_id, text=chunk)


from multimodal import analyze_media, extract_youtube_transcript


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    msg = bot.reply_to(message, "👁️ JARVIS inspecting image...")
    try:
        # Get highest resolution photo
        file_info = bot.get_file(message.photo[-1].file_id)
        file_bytes = bot.download_file(file_info.file_path)
        caption = message.caption or "Analyze this screenshot/image in detail and provide insights or solutions."
        
        reply = analyze_media(file_bytes, "image/jpeg", caption)
        _send_safe_reply(message.chat.id, msg.message_id, reply)
    except Exception as e:
        logger.error(f"Photo handling error: {e}")
        bot.edit_message_text(f"⚠️ Error analyzing photo: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)


@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    msg = bot.reply_to(message, "🎙️ JARVIS listening to your voice note...")
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        mime_type = "audio/ogg" if message.voice else "audio/mp3"
        
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        caption = message.caption or "Transcribe what is said, understand the intent, and reply back thoughtfully."
        
        reply = analyze_media(file_bytes, mime_type, caption)
        _send_safe_reply(message.chat.id, msg.message_id, reply)

        # Voice reply generation (if it was a voice message)
        if message.voice:
            try:
                from gtts import gTTS
                import io
                import re
                # Clean up markdown formatting, links, and code blocks for smooth speech
                clean_text = re.sub(r'```.*?```', '', reply, flags=re.DOTALL)
                clean_text = re.sub(r'[*#_`>\[\]\(\)]', '', clean_text)
                clean_text = re.sub(r'http\S+', '', clean_text)
                clean_text = ' '.join(clean_text.split())[:500]
                
                if clean_text:
                    tts = gTTS(text=clean_text, lang='en', tld='co.in', slow=False)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    bot.send_voice(chat_id=message.chat.id, voice=audio_fp)
            except Exception as e_tts:
                logger.error(f"TTS voice reply error: {e_tts}")

    except Exception as e:
        logger.error(f"Audio handling error: {e}")
        bot.edit_message_text(f"⚠️ Error processing audio: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)


from documents import parse_document, analyze_document_content


@bot.message_handler(content_types=['document'])
def handle_document(message):
    doc_name = message.document.file_name or "document.txt"
    msg = bot.reply_to(message, f"📄 JARVIS reading `{doc_name}`...")
    try:
        file_info = bot.get_file(message.document.file_id)
        file_bytes = bot.download_file(file_info.file_path)
        caption = message.caption or "Analyze this file in detail, provide structured takeaways, and recommend 3 actionable next steps."
        
        extracted_text = parse_document(file_bytes, doc_name)
        reply = analyze_document_content(extracted_text, doc_name, caption)
        _send_safe_reply(message.chat.id, msg.message_id, reply)
    except Exception as e:
        logger.error(f"Document handling error: {e}")
        bot.edit_message_text(f"⚠️ Error reading document: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip()

    # YouTube Link Detection
    if ("youtube.com/watch" in user_text or "youtu.be/" in user_text) and len(user_text.split()) == 1:
        msg = bot.reply_to(message, "📹 JARVIS analyzing YouTube video...")
        try:
            summary = extract_youtube_transcript(user_text)
            _send_safe_reply(message.chat.id, msg.message_id, summary)
            return
        except Exception as e:
            bot.edit_message_text(f"⚠️ YouTube error: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)
            return

    # Provider Switch Approval Flow
    if is_awaiting_approval():
        if user_text.upper() in ["YES", "Y", "YES SWITCH", "SWITCH"]:
            bot.reply_to(message, approve_switch(), parse_mode="Markdown")
            return
        elif user_text.upper() in ["NO", "N", "NOPE", "PAUSE"]:
            bot.reply_to(message, deny_switch(), parse_mode="Markdown")
            return

    msg = bot.reply_to(message, "🧠 JARVIS thinking...")
    try:
        result = process_message(user_text)
        if isinstance(result, tuple):
            reply_text, _ = result
        else:
            reply_text = result

        _send_safe_reply(message.chat.id, msg.message_id, reply_text)

    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            bot.edit_message_text("⚠️ Encountered an issue. Self-healing initiated...", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception:
            pass
        self_heal(e, __file__)

@app.route(f"/{token}", methods=["POST"])
def webhook():
    try:
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error(f"Webhook update error: {e}")
    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return "Jarvis 3.0 is alive!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Set webhook on startup
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if webhook_url:
        bot.remove_webhook()
        bot.set_webhook(url=f"{webhook_url}/{token}")
        logger.info(f"Webhook set to {webhook_url}/{token}")
    app.run(host="0.0.0.0", port=port)
