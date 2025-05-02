import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Store conversation history (user-specific)
user_conversations = {}

# Welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []  # Reset chat history
    welcome_msg = (
        f"🎉 Welcome {update.effective_user.first_name}!\n\n"
        "🤖 You can ask me anything!\n\n"
        "🔄 Use /newchat to start a fresh conversation.\n"
        "✅ Support: @YourSupportChannel\n"
        "💥 Powered by: @YourBrandChannel"
    )
    await update.message.reply_text(welcome_msg)

# New chat command with confirmation
async def newchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []  # Clear history
    
    # Send confirmation message
    await update.message.reply_text("🧹 **Bot history has been reset.**\n\n🔄 New chat started! Ask me anything.")

# Handle messages (with conversation history)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Initialize user's conversation history if not exists
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    # Add user message to history
    user_conversations[user_id].append({"role": "user", "content": user_message})

    # Send "ChatGPT is thinking..." message
    thinking_msg = await update.message.reply_text("ChatGPT is thinking 🤔...")

    try:
        # Call OpenAI API with conversation history
        response = openai.ChatCompletion.create(
            model="gpt-4-32k",
            messages=user_conversations[user_id],
            max_tokens=2000,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message['content']
        
        # Add bot's reply to history
        user_conversations[user_id].append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        logger.error(f"Error: {e}")
        bot_reply = "⚠️ Error processing your request. Try again later."

    # Edit the message with the final response
    await context.bot.edit_message_text(
        chat_id=update.message.chat_id,
        message_id=thinking_msg.message_id,
        text=bot_reply
    )

# Start the bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newchat", newchat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    app.add_error_handler(lambda update, context: logger.error(f"Update {update} caused error: {context.error}"))
    
    # Run bot
    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
