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


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip()

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
