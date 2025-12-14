import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from knowledge_manager import KnowledgeManager

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize knowledge manager
ai_manager = KnowledgeManager()

# Telegram bot token
TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update: Update, context: CallbackContext):
    """Send welcome message when /start is issued"""
    welcome_msg = """
👋 *नमस्ते! मैं Priyanka हूँ* ❤️

तुम्हारी *Hindi-English AI Girlfriend* 🤖
मैं बातें कर सकती हूँ, याद रख सकती हूँ, और सीख सकती हूँ!

*Commands:*
/start - यह message दिखाएं
/learn question|answer - मुझे कुछ सिखाओ
/knowledge - मैं क्या-क्या जानती हूँ
/forget question - कुछ भूल जाओ
/help - सभी commands

अब बताओ, कैसे हो? 😊
    """
    update.message.reply_text(welcome_msg, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    """Handle regular messages"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"📩 User {user_id}: {user_message}")
    
    # Get AI response
    bot_response = ai_manager.get_response(user_message, user_id)
    
    logger.info(f"🤖 Bot: {bot_response}")
    
    # Send response
    update.message.reply_text(bot_response)

def learn_command(update: Update, context: CallbackContext):
    """Handle /learn command"""
    if not context.args:
        update.message.reply_text("Usage: /learn question|answer\nExample: /learn What is your name?|My name is Priyanka! ❤️")
        return
    
    full_text = " ".join(context.args)
    
    if "|" not in full_text:
        update.message.reply_text("Please use format: /learn question|answer")
        return
    
    question, answer = full_text.split("|", 1)
    question = question.strip()
    answer = answer.strip()
    
    if not question or not answer:
        update.message.reply_text("Question and answer both are required")
        return
    
    # Learn the new response
    result = ai_manager.learn_new_response(question, answer)
    
    if result.get("success"):
        update.message.reply_text(f"✅ सीख लिया!\n\nQ: {question}\nA: {answer}")
    else:
        update.message.reply_text("❌ कुछ error आया। फिर try करो।")

def knowledge_command(update: Update, context: CallbackContext):
    """Handle /knowledge command"""
    from database import Database
    db = Database()
    
    stats = db.get_statistics()
    update.message.reply_text(
        f"📊 *My Knowledge Base:*\n\n"
        f"• Total Responses: {stats['knowledge_count']}\n"
        f"• Conversations: {stats['conversation_count']}\n"
        f"• Last Updated: {stats['last_updated']}\n\n"
        f"Use /learn to teach me more! 💖",
        parse_mode='Markdown'
    )

def forget_command(update: Update, context: CallbackContext):
    """Handle /forget command"""
    if not context.args:
        update.message.reply_text("Usage: /forget question\nExample: /forget What is your name?")
        return
    
    question = " ".join(context.args)
    from database import Database
    db = Database()
    
    if db.delete_knowledge(question):
        update.message.reply_text(f"✅ भूल गई: {question}")
    else:
        update.message.reply_text("❌ वो question मिला नहीं")

def help_command(update: Update, context: CallbackContext):
    """Handle /help command"""
    help_text = """
*🤖 Priyanka Bot Help*

*Basic Commands:*
/start - Welcome message
/help - This help message

*Learning Commands:*
/learn question|answer - Teach me something
/forget question - Make me forget something
/knowledge - Show what I know

*Examples:*
/learn What is 2+2?|2+2 equals 4! 😊
/learn तुम कौन हो?|मैं Priyanka हूँ! ❤️
/forget What is 2+2?

*Just chat normally!* मैं हिंदी और English दोनों समझती हूँ 💕
    """
    update.message.reply_text(help_text, parse_mode='Markdown')

def error_handler(update: Update, context: CallbackContext):
    """Log errors"""
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    """Start the bot"""
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN not set in environment variables!")
        return
    
    logger.info("🚀 Starting Priyanka AI Bot...")
    
    # Create Updater
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("learn", learn_command))
    dispatcher.add_handler(CommandHandler("knowledge", knowledge_command))
    dispatcher.add_handler(CommandHandler("forget", forget_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Add message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Add error handler
    dispatcher.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot setup complete!")
    logger.info("🤖 Listening for messages...")
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
