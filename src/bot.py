import logging
import os

from dotenv import load_dotenv
from models import Transaction

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOOSING, TYPING, CHOOSING_CATEGORY = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[InlineKeyboardButton(text="💸 Expense", callback_data="expense"),
                InlineKeyboardButton(text="💰 Income", callback_data="income")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text="V.A.U.L.T. initialized. Your financial system is now active, Mr. Ahmed.",
    reply_markup = reply_markup
)
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["trans_type"] = query.data

    if query.data == 'expense':
        await query.edit_message_text(text="Where are we Burning the money, sir")
    elif query.data == 'income':
        await query.edit_message_text(text="Money Laundering, sir?")
    
    return TYPING

async def typing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(" ", 1)
        amount = float(parts[0])
        note = parts[1]
    except (IndexError, ValueError):
        await update.message.reply_text("Use format: <amount> <note> (e.g., 500 food), Sir.")
        return TYPING

    context.user_data["amount"] = amount
    context.user_data["note"] = note

    category_keyboard = [
    [InlineKeyboardButton("🛒 Groceries", callback_data="Groceries"),
     InlineKeyboardButton("🚗 Transport", callback_data="Transport")],
    [InlineKeyboardButton("🎬 Entertainment", callback_data="Entertainment"),
     InlineKeyboardButton("🍔 Food", callback_data="Food")],
    [InlineKeyboardButton("➕ New Category", callback_data="new_category")]
    ]
    
    reply_markup = InlineKeyboardMarkup(category_keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select a category for this transaction, sir.",
        reply_markup=reply_markup
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(start_handler)

    application.run_polling()