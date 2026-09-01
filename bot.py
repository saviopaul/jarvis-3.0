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

    msg = bot.reply_to(message, "JARVIS thinking...")
    try:
        result = process_message(user_text)
        if isinstance(result, tuple):
            reply_text, _ = result
            bot.edit_message_text(reply_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(result, chat_id=message.chat.id, message_id=msg.message_id)
    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            bot.edit_message_text("Encountered an issue. Self-healing initiated...", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception:
            pass
        self_heal(e, __file__)

@app.route(f"/{token}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
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
