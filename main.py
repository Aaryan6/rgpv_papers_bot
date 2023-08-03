from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater, CallbackQueryHandler, CallbackContext, ConversationHandler
from webScraping import getAllLinks
import json
import os
from dotenv import load_dotenv

# load the envoironment keys
load_dotenv()

# States
COLLEGE_YEAR, BRANCH, DOWNLOAD = range(3)
BRANCH_OPTIONS = ["IT", "CS", "CIVIL", "EC", "EE", "ME", "EX"]
INITIAL_USER_STATE = {
    "year": "",
    "branch": "",
}


def load_user_choices():
    try:
        with open('userChoices.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_user_choices(user_choices):
    with open('userChoices.json', 'w') as file:
        json.dump(user_choices, file, indent=2)


# Load user choices from the JSON file
user_choices = load_user_choices()

# truncate string


def trucateString(original_string):
    max_length = 45
    if len(original_string) > max_length:
        truncated_length = (max_length - 3) // 2
        truncated_string = original_string[:truncated_length] + \
            "..." + original_string[-truncated_length:]
        return truncated_string
    else:
        return original_string


# help command for bot
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


# start function for bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user_id = str(update.message.from_user.id)
    user_choices = load_user_choices()

    options = ["First", "Second", "Third", "Final"]
    if user_id in user_choices:
        keyboard_list = [
            [InlineKeyboardButton(optn, callback_data=optn)] for optn in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_list)

        await update.message.reply_text("Great to see you here!\n\nWhat is your Year?",
                                        reply_markup=reply_markup)
        return COLLEGE_YEAR

    # If user choices do not exist, proceed with the rest of the start logic
    options = ["First", "Second", "Third", "Final"]
    keyboard_list = [
        [InlineKeyboardButton(optn, callback_data=optn)] for optn in options
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_list)

    await update.message.reply_text("What is your Year?\n",
                                    reply_markup=reply_markup)
    # Initialize user choices for this user
    user_choices[user_id] = INITIAL_USER_STATE
    save_user_choices(user_choices)
    return COLLEGE_YEAR


async def handle_college_year(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data == "First":

        user_choices[user_id] = {"year": "first", "branch": ""}
        save_user_choices(user_choices)

        await query.message.reply_text("Alright, Please enter the subject name:")
        return DOWNLOAD

    else:

        user_choices[user_id] = {"year": query.data.lower(), "branch": ""}
        save_user_choices(user_choices)

        keyboard_list = [
            [InlineKeyboardButton(optn, callback_data=optn)] for optn in BRANCH_OPTIONS
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_list)

        await query.message.reply_text("What is your branch?\n",
                                       reply_markup=reply_markup)
        return BRANCH

# handle user response to branch question


async def handle_branch(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data in ["IT", "CS", "CIVIL", "EC", "EE", "ME", "EX"]:
        user_choices[user_id] = {"branch": query.data,
                                 "year": user_choices[user_id]["year"]}
        save_user_choices(user_choices)
        await query.message.reply_text(f"Branch -> {query.data}\nAlright, Please enter the subject name:")

    return DOWNLOAD


# getting the subject name from the user and sending the links
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    arr = []
    user_id = str(update.message.from_user.id)
    branch = ""
    year = ""
    # Retrieve user's branch choice from user_choices dictionary
    if user_id in user_choices:
        branch = user_choices[user_id]["branch"]
        year = user_choices[user_id]["year"]
    else:
        await update.message.reply_text("Please select your branch using /start command.")
        return

    # get all links from the website related to the subject
    if (year == "first"):
        arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/rgpv-first-year.html#list")
    else:
        if (branch == "IT"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-it-question-papers.html#list")
        elif (branch == "CS"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-cse-question-papers.html#list")
        elif (branch == "CIVIL"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-civil-question-papers.html#list")
        elif (branch == "EC"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-ec-question-papers.html#list")
        elif (branch == "EE"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-ee-question-papers.html#list")
        elif (branch == "ME"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-me-question-papers.html#list")
        elif (branch == "EX"):
            arr = await getAllLinks(update.message.text, "https://www.rgpvonline.com/btech-ex-question-papers.html#list")

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
        await update.message.reply_text("No paper found!")


# sending the pdf to the user
async def handle_selection(update, context):
    query = update.callback_query

    await query.answer()
    selected_item = "https://www.rgpvonline.com/be/"+query.data+".pdf"

    try:
        await query.message.reply_document(selected_item)
    except:
        await query.message.reply_text("Something went wrong!")

    return BRANCH


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Create a ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            COLLEGE_YEAR: [CallbackQueryHandler(handle_college_year)],
            BRANCH: [CallbackQueryHandler(handle_branch)],
            DOWNLOAD: [CallbackQueryHandler(handle_selection)]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # text message
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
