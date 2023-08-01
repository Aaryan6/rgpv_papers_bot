from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater, CallbackQueryHandler
from webScraping import getAllLinks
import json
import os

bot_uri = os.environ.get('TELEGRAM_BOT_URI')


def trucateString(original_string):
    max_length = 45  # Maximum length of the final string (including '...')

    if len(original_string) > max_length:
        # Calculate the length of the truncated portion on each side of '...'
        truncated_length = (max_length - 3) // 2
        # Create the truncated string with '...' in the middle
        truncated_string = original_string[:truncated_length] + \
            "..." + original_string[-truncated_length:]
        return truncated_string
    else:
        # If the original string is not longer than the maximum length, keep it as it is
        return original_string

# start function for bot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html("Great to see you here!\n\nType subject name for searching question papers.")

# help command for bot


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


# sending message to user
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    # Your lists
    arr = await getAllLinks(update.message.text)
    if type(arr) == str:
        await update.message.reply_text(arr)
        return

    try:
        # Create a list of InlineKeyboardButton for each item in list1
        keyboard_list = [
            [InlineKeyboardButton(trucateString(item), callback_data=item)] for item in arr if len(item) < 64
        ]

        # Create the InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(keyboard_list)

        # Send the message with the options
        await update.message.reply_text("Please select the paper to download:",
                                        reply_markup=reply_markup)

    except:
        await update.message.reply_text("No links found!")

    # await update.message.reply_document("https://www.rgpvonline.com/be/it-303-data-structure-nov-2022.pdf")


async def handle_selection(update, context):
    query = update.callback_query
    selected_item = "https://www.rgpvonline.com/be/"+query.data+".pdf"
    print(selected_item)
    # Handle the selected item
    try:
        await query.message.reply_document(selected_item)
    except:
        await query.message.reply_text("Something went wrong!")


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(
        bot_uri).build()
    # application = Application.builder().token(os.getenv('TELEGRAM_KEY')).build()

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
