import logging
import asyncio
import json # Added this line
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from .. import config
from ..ai_core import ai_core_instance

logger = logging.getLogger(__name__)

# Global variable to hold the Telegram Application instance
telegram_application: Application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I am your AI Cognitive Shell bot. "
        "Send me a message and I will process it using the AI core.",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process a user message using the AI core and send the response."""
    user_message = update.message.text
    chat_id = update.effective_chat.id

    if not user_message:
        await update.message.reply_text("Please send a text message.")
        return

    logger.info(f"Received message from chat_id {chat_id}: {user_message}")

    # Check if the chat_id is allowed if TELEGRAM_CHAT_ID is set
    if config.TELEGRAM_CHAT_ID and str(chat_id) != config.TELEGRAM_CHAT_ID:
        logger.warning(f"Unauthorized chat_id {chat_id} attempted to interact with the bot.")
        await update.message.reply_text("You are not authorized to interact with this bot.")
        return

    try:
        full_response_content = ""
        # Process the message using the AI core instance and stream response
        async for chunk in ai_core_instance.process_chat_stream(chat_id, user_message):
            try:
                parsed_chunk = json.loads(chunk)
                chunk_type = parsed_chunk.get("type")
                chunk_content = parsed_chunk.get("content")

                if chunk_type == "message_chunk":
                    full_response_content += chunk_content
                elif chunk_type == "command":
                    full_response_content += f"\nAI suggested shell command:\n```bash\n{chunk_content}\n```"
                elif chunk_type == "generated_code":
                    filename = chunk_content.get("filename", "unknown_file")
                    code = chunk_content.get("code", "No code generated.")
                    language = chunk_content.get("language", "text")
                    full_response_content += (
                        f"\nAI generated a {language} program: `{filename}`\n"
                        f"```\n{code}\n```"
                    )
                elif chunk_type == "error":
                    full_response_content += f"\nError from AI: {chunk_content}"
                # Add other chunk types if needed for Telegram output

            except json.JSONDecodeError:
                logger.warning(f"Could not decode JSON chunk from AI core: {chunk}")

        if full_response_content:
            # Telegram has limits on message length and Markdown parsing.
            # We should sanitize Markdown and split messages if too long.
            # For now, a basic send.
            await update.message.reply_text(full_response_content, parse_mode="Markdown")
        else:
            await update.message.reply_text("AI processed your message, but no response was generated.")

    except Exception as e:
        logger.error(f"Error processing message for chat_id {chat_id}: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while processing your request. Please try again later.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the user."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    try:
        if update and update.effective_message:
            text = "An error occurred while processing your request. Please try again later."
            await update.effective_message.reply_text(text)
    except Exception as e:
        logger.error(f"Error sending error message to user: {e}")

async def start_telegram_bot():
    global telegram_application
    if not config.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not set. Telegram bot will not start.")
        return

    if telegram_application and telegram_application.running:
        logger.info("Telegram bot is already running.")
        return

    logger.info("Starting Telegram Bot...")
    try:
        telegram_application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        # Remove webhook to ensure polling works correctly
        try:
            await telegram_application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Successfully deleted Telegram webhook and dropped pending updates.")
            await asyncio.sleep(1) # Add a small delay after deleting webhook
        except TelegramError as e:
            logger.warning(f"Could not delete Telegram webhook (might not be set): {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while deleting webhook: {e}")

        # Add handlers
        telegram_application.add_handler(CommandHandler("start", start))
        telegram_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Add a general error handler
        telegram_application.add_error_handler(error_handler)

        # Initialize and start the application
        await telegram_application.initialize()
        await telegram_application.start()
        await telegram_application.updater.start_polling() # Start polling for updates

        logger.info("Telegram bot started.")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        telegram_application = None # Reset application instance on failure

async def stop_telegram_bot():
    global telegram_application
    if telegram_application and telegram_application.running:
        logger.info("Stopping Telegram bot...")
        try:
            if telegram_application.updater and telegram_application.updater.running:
                await telegram_application.updater.stop()
            if telegram_application.running:
                await telegram_application.stop()
            logger.info("Telegram bot stopped.")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}", exc_info=True)
        finally:
            telegram_application = None
    else:
        logger.info("Telegram bot is not running.")