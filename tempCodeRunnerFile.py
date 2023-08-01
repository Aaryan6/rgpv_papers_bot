
    #     [InlineKeyboardButton(item, callback_data=item)] for item in arr
    # ]

    # # Create the InlineKeyboardMarkup
    # reply_markup = InlineKeyboardMarkup(keyboard_list)

    # # Send the message with the options
    # await update.message.reply_text("Please select an item:",
    #                                 reply_markup=reply_markup)