import logging
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from database import approve_auth_session, reject_auth_session

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8486309645:AAHGj8DkNk6vGRY2p8yFGTA9_xWxfv8g8Xs"
ADMIN_TELEGRAM_ID = 180587749

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks for admin approval/rejection"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin
    if user_id != ADMIN_TELEGRAM_ID:
        await query.edit_message_text("❌ У вас нет прав администратора")
        return

    data = query.data

    if data.startswith("approve_"):
        session_token = data.replace("approve_", "")

        # Approve the session in database
        approve_auth_session(session_token)

        # Update message
        await query.edit_message_text(
            f"✅ Доступ разрешен\n"
            f"🔑 Токен: {session_token[:8]}...\n\n"
            f"Пользователь будет автоматически перенаправлен в админ-панель."
        )

        logger.info(f"Session {session_token} approved by admin {user_id}")

    elif data.startswith("deny_"):
        session_token = data.replace("deny_", "")

        # Reject the session in database
        reject_auth_session(session_token)

        # Update message
        await query.edit_message_text(
            f"❌ Доступ отклонен\n"
            f"🔑 Токен: {session_token[:8]}...\n\n"
            f"Пользователь получит уведомление об отказе."
        )

        logger.info(f"Session {session_token} rejected by admin {user_id}")

def run_bot():
    """Run the Telegram bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set")
        return

    if not ADMIN_TELEGRAM_ID:
        logger.error("ADMIN_TELEGRAM_ID is not set")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add only callback handler - no commands needed
    application.add_handler(CallbackQueryHandler(button_callback))

    # Run the bot
    logger.info("Starting bot (callback handler only)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Initialize database first
    from database import init_db
    init_db()

    print("🤖 Telegram Bot для авторизации (только inline кнопки)")
    print(f"✅ BOT_TOKEN: установлен")
    print(f"✅ ADMIN_TELEGRAM_ID: {ADMIN_TELEGRAM_ID}")
    print()

    run_bot()
