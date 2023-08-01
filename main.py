from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater, CallbackQueryHandler
from webScraping import getAllLinks
import json
import os
from dotenv import load_dotenv

# load the envoironment keys
load_dotenv()


def trucateString(original_string):
    max_length = 45
    if len(original_string) > max_length:
        truncated_length = (max_length - 3) // 2
        truncated_string = original_string[:truncated_length] + \
            "..." + original_string[-truncated_length:]
        return truncated_string
    else:
        return original_string


# start function for bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html("Great to see you here!\n\nType subject name for searching question papers.")


# help command for bot
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


# getting the subject name from the user and sending the links
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    # get all links from the website related to the subject
    arr = await getAllLinks(update.message.text)

    # if the arr is string then send the string
    if type(arr) == str:
        await update.message.reply_text(arr)
        return

    try:
        keyboard_list = [
            [InlineKeyboardButton(trucateString(item), callback_data=item)] for item in arr if len(item) < 64
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_list)

        await update.message.reply_text("Please select the paper to download:",
                                        reply_markup=reply_markup)

    except:
        await update.message.reply_text("No links found!")


# sending the pdf to the user
async def handle_selection(update, context):
    query = update.callback_query
    selected_item = "https://www.rgpvonline.com/be/"+query.data+".pdf"

    try:
        await query.message.reply_document(selected_item)
    except:
        await query.message.reply_text("Something went wrong!")


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # start command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # text message
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(CallbackQueryHandler(handle_selection))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
