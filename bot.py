import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuration
OWNER_ID = 7588665244  # Your Telegram User ID
BROADCAST_MESSAGE = "📢 Default broadcast message"  # Editable via /setbroadcast
conversation_history = {}
user_ids = set()  # Tracks all users for broadcasting

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_ids.add(user.id)
    welcome_msg = f"""
🎉 *Welcome {user.first_name}!* 🎉  

✨ *I'm your personal AI assistant* ✨  

🤖 How can I assist you today?  

🔥 *Features*:  
✅ 100% Free & Unlimited  
✅ Instant Responses  
✅ Memory Across Chats  

📝 *Quick Commands*:  
🔄 /new - Fresh start  
ℹ️ /help - Show this menu  

⚡ *Try asking*:  
"Explain like I'm 5 🧒"  
"Give me 3 ideas 💡"  

🛠️ Support: @Smartautomationsupport_bot  
🚀 Powered by: @smartautomations  
"""
    update.message.reply_text(welcome_msg, parse_mode="Markdown")

def help_command(update: Update, context: CallbackContext) -> None:
    help_msg = """
🆘 *@smartautomations_bot Help* 🆘  
────────────────────  
💬 *How to chat*:  
Just type messages like:  
• "Explain quantum physics ⚛️"  
• "Write a haiku about cats 🐱"  

⚙️ *Commands*:  
🔄 /new - Reset conversation  
ℹ️ /help - This message  

📏 *Limits*:  
4000 chars/message  
(we auto-split 📜)  

🔋 *Status*: Operational ✅  

💡 *Pro Tip*:  
Use emojis for better responses! 😉  
"""
    update.message.reply_text(help_msg, parse_mode="Markdown")

def new_chat(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = []
    update.message.reply_text("""
🔄 *Memory Cleared!* 🧹  

Ask me anything new! 💭  

*Try these*:  
• "Tell me a fun fact 🎲"  
• "Help me brainstorm 💡"
""", parse_mode="Markdown")

def set_broadcast(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("🚫 *Owner only!*", parse_mode="Markdown")
        return

    global BROADCAST_MESSAGE
    BROADCAST_MESSAGE = " ".join(context.args) or "📢 New broadcast"
    update.message.reply_text(f"✅ *Broadcast message set to:*\n{BROADCAST_MESSAGE}", parse_mode="Markdown")

def broadcast(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("🚫 *Owner only!*", parse_mode="Markdown")
        return

    if not user_ids:
        update.message.reply_text("❌ No users to broadcast to!")
        return

    progress_msg = update.message.reply_text(f"📡 Broadcasting to {len(user_ids)} users...")
    success = 0

    for user_id in user_ids:
        try:
            context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *Announcement*\n\n{BROADCAST_MESSAGE}",
                parse_mode="Markdown"
            )
            success += 1
            if success % 10 == 0:
                context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=progress_msg.message_id,
                    text=f"📡 Broadcasting... ({success}/{len(user_ids)})"
                )
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=progress_msg.message_id,
        text=f"✅ Broadcast complete!\nSent to: {success}/{len(user_ids)} users"
    )

def get_ai_response(prompt: str, chat_id: int) -> str:
    try:
        messages = conversation_history.get(chat_id, [])
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            "https://free.churchless.tech/v1/chat/completions",
            json={"messages": messages},
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_message = update.message.text
    
    if not user_message.strip():
        update.message.reply_text("""
📛 *Oops! Empty Message* 📛

@smartautomations_bot needs text to respond!

Try:
• A question ❓
• An idea 💡
""", parse_mode="Markdown")
        return
    
    if update.effective_user.id not in user_ids:
        user_ids.add(update.effective_user.id)
    
    thinking_msg = update.message.reply_text("""
✨ *Smart AI is thinking* 🤔...  
Please wait...
""", parse_mode="Markdown")
    
    context.bot.send_chat_action(
        chat_id=chat_id,
        action="typing"
    )
    
    ai_response = get_ai_response(user_message, chat_id)
    
    if not ai_response:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=thinking_msg.message_id,
            text="""
⚠️ *Temporary Issue* ⚠️

@smartautomations_bot is working hard but:

🔧 AI service is overloaded
⏳ Try again in 1-2 minutes
🔄 Or /new to reset

💌 Contact @Smartautomationsupport_bot if needed

*We value your patience* 🙏
""",
            parse_mode="Markdown"
        )
        return
    
    if len(ai_response) > 4000:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=thinking_msg.message_id,
            text="📜 *Big Answer Alert!* 📜\nSplitting response into parts...",
            parse_mode="Markdown"
        )
        for i in range(0, len(ai_response), 4000):
            context.bot.send_message(
                chat_id=chat_id,
                text=ai_response[i:i+4000]
            )
    else:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=thinking_msg.message_id,
            text=ai_response
        )

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN not set!")
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("new", new_chat))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))
    dispatcher.add_handler(CommandHandler("setbroadcast", set_broadcast))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    PORT = int(os.getenv("PORT", 8000))
    APP_NAME = os.getenv("KOYEB_APP_NAME", "your-app-name")
    
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{APP_NAME}.koyeb.app/{TOKEN}"
    )
    print(f"🚀 Bot deployed: https://{APP_NAME}.koyeb.app")
    updater.idle()

if __name__ == "__main__":
    main()
