import os
import logging
from dotenv import load_dotenv
import telebot
from brain import process_message
from self_heal import self_heal
from providers import approve_switch, deny_switch, is_awaiting_approval

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

token = os.environ.get("TELEGRAM_TOKEN")
if not token:
    logger.error("TELEGRAM_TOKEN not found in environment variables.")
    exit(1)

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
        f"Greetings! I am Jarvis 3.0.\n"
        f"I am fully autonomous and ready to write code, manage GitHub, deploy to Render, and remember your life events.\n"
        f"What shall we build today?"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip()

    # ── Provider Switch Approval Flow ──────────────────────────────────────
    if is_awaiting_approval():
        if user_text.upper() in ["YES", "Y", "YES SWITCH", "SWITCH"]:
            reply = approve_switch()
            bot.reply_to(message, reply, parse_mode="Markdown")
            return
        elif user_text.upper() in ["NO", "N", "NOPE", "PAUSE"]:
            reply = deny_switch()
            bot.reply_to(message, reply, parse_mode="Markdown")
            return
    # ────────────────────────────────────────────────────────────────────────

    msg = bot.reply_to(message, "🧠 JARVIS thinking...")
    try:
        result = process_message(user_text)

        # If process_message returns a tuple, it means we need approval to switch
        if isinstance(result, tuple):
            reply_text, needs_approval = result
            bot.edit_message_text(reply_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(result, chat_id=message.chat.id, message_id=msg.message_id)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        try:
            bot.edit_message_text("⚠️ Encountered an issue. Initiating self-heal...", chat_id=message.chat.id, message_id=msg.message_id)
        except Exception:
            pass
        self_heal(e, __file__)

if __name__ == "__main__":
    logger.info("Starting Jarvis 3.0 Telegram Bot...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Polling crashed: {e}")
            self_heal(e, __file__)
