import logging
import os

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[InlineKeyboardButton(text="💸 Expense", callback_data="expense"),
                InlineKeyboardButton(text="💰 Income", callback_data="income")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text="V.A.U.L.T. initialized. Your financial system is now active, Mr. Ahmed.",
    reply_markup = reply_markup
)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'expense':
        await query.edit_message_text(text="Where are we Burning the money, sir")
    elif query.data == 'income':
        await query.edit_message_text(text="Money Laundering, sir?")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(start_handler)

    application.run_polling()