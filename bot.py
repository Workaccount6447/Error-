
import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuration from environment variables
TELEGRAM_TOKEN = os.getenv('8123828718:AAGwah8P4HhnGz6NvBpo-UeVIEq0qjzWmZc')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
SUPPORT_BOT = "@Smartautomationsupport_bot"
BRAND_CHANNEL = "@smartautomations"
CREATOR = "@smartautomations"

# OpenRouter API URL
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Dictionary to store conversation history
conversation_history = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = []
    
    welcome_message = (
        f"🎉 Welcome {user.first_name}!\n\n"
        "🤖 How can I assist you today?\n\n"
        "🤖 I am totally free and unlimited - feel free to ask me any questions\n\n"
        "🔄 Use /newchat to start a fresh conversation.\n\n"
        f"✅ Support: {SUPPORT_BOT}\n\n"
        f"💥 Powered by: {BRAND_CHANNEL}"
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message."""
    help_text = (
        f"👉 I am smart AI made by {CREATOR}.\n\n"
        "🤖 Ask me any questions and I'll give you answers. Don't worry, I'm completely free 🔥.\n\n"
        f"💥 If you need more support contact us on: {SUPPORT_BOT}"
    )
    update.message.reply_text(help_text)

def newchat(update: Update, context: CallbackContext) -> None:
    """Reset conversation history."""
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = []
    update.message.reply_text("🔄 Chat reset successfully! Ask me anything new.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages."""
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    if not user_message.strip():
        update.message.reply_text("Please send a valid question or message.")
        return
    
    try:
        if chat_id not in conversation_history:
            conversation_history[chat_id] = []
        
        # Send thinking message
        thinking_msg = update.message.reply_text("🔍 Smart AI is thinking 🤔...\n\n✨ We respect your patience")
        
        # Prepare messages with history
        messages = conversation_history[chat_id].copy()
        messages.append({"role": "user", "content": user_message})
        
        response = requests.post(
            OPENROUTER_API_URL,
            json={"model": OPENROUTER_MODEL, "messages": messages},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        ai_response = response.json()["choices"][0]["message"]["content"]
        
        # Update history
        conversation_history[chat_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Edit thinking message with response
        context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=thinking_msg.message_id,
            text=ai_response
        )
        
    except Exception as e:
        print(f"Error: {e}")
        update.message.reply_text(
            f"⚠️ Sorry, I encountered an error. Please try again later or contact {SUPPORT_BOT}"
        )

def main() -> None:
    """Start the bot."""
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("newchat", newchat))

    # Message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == '__main__':
    main()
