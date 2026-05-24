import logging
import os

from dotenv import load_dotenv
from models import Transaction
from logic import load_transactions, save_transactions, get_income_sources

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOOSING, TYPING, CHOOSING_CATEGORY, TYPING_CATEGORY = range(4)

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
    
    text: str = update.message.text.strip()

    try:
        amount_str, note = text.split(maxsplit=1)
        amount = float(amount_str)
    except ValueError:
        await update.message.reply_text(
            "Format: <amount> <note> (e.g., 500 food). Try again, Sir."
        )
        return TYPING

    context.user_data["amount"] = amount 
    context.user_data["note"] = note

    if context.user_data["trans_type"] == 'expense':
        category_keyboard = [
            [InlineKeyboardButton("🛒 Groceries", callback_data="Groceries"),
            InlineKeyboardButton("🚗 Transport", callback_data="Transport")],
            [InlineKeyboardButton("🎬 Entertainment", callback_data="Entertainment"),
            InlineKeyboardButton("🍔 Food", callback_data="Food")],
            [InlineKeyboardButton("➕ New Category", callback_data="new_category")]
        ]
        
        reply_markup = InlineKeyboardMarkup(category_keyboard)

        msg = await update.message.reply_text(
            "Select a category for this transaction, sir.",
            reply_markup=reply_markup
        )

        context.user_data["category_msg_id"] = msg.message_id

        return CHOOSING_CATEGORY
    
    elif context.user_data["trans_type"] == 'income':
        income_keywords = ["from", "received", "got", "credited", "on", "for"]

        candidate = note.lower()

        for keyword in income_keywords:
            if keyword in candidate:
                candidate = candidate.replace(keyword, " ").strip()
        
        transactions = load_transactions()
        sources = get_income_sources(transactions)

        if candidate in sources:
            category = candidate
            transaction = Transaction(trans_type=context.user_data["trans_type"], amount=amount, note=note, category=category)
            
            transactions.append(transaction)
            save_transactions(transactions)
            await update.message.reply_text(
                f"Transaction recorded under \"{category}\". Your ledger has been updated."
            )

            return ConversationHandler.END
    
        else:
            context.user_data["candidate"] = candidate

            source_keyboard = []
            if sources == []:
                source_keyboard = [[InlineKeyboardButton("➕ New Source", callback_data="new_source")]]
            else:
                source_keyboard = [
                    [InlineKeyboardButton(source, callback_data=source) for source in sources],
                    [InlineKeyboardButton("➕ New Source", callback_data="new_source")]]
                
            reply_markup = InlineKeyboardMarkup(source_keyboard)
                
            await update.message.reply_text(
                f"New Income source \"{candidate}\" detected, what would you like to do?",
                reply_markup=reply_markup
            )
        
            return CHOOSING_CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    amount = context.user_data["amount"]
    note = context.user_data["note"]
    trans_type = context.user_data["trans_type"]

    if query.data == "new_category":
        await query.edit_message_text(
            "Please type the name of the new category, sir."
        )
        return TYPING_CATEGORY
    
    if trans_type == "expense":
        category = query.data

    elif trans_type == "income":

        if query.data == "new_source":
            category = context.user_data["candidate"]
        else:
            category = query.data

    transaction = Transaction(amount=amount, note=note, category=category, trans_type=trans_type)
    transactions = load_transactions()   
    transactions.append(transaction)   
    save_transactions(transactions)    

    if trans_type == "expense":
        await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["category_msg_id"],
        text="Transaction recorded. Your ledger has been updated."
    )
    
    elif trans_type == "income":
        await query.edit_message_text(
            text=f"Income of {amount} recorded under \"{category}\". Ledger updated."
        )

    return ConversationHandler.END    

async def custom_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text.strip()

    transaction = Transaction(amount=context.user_data["amount"], note=context.user_data["note"], category=category, trans_type=context.user_data["trans_type"])
    transactions = load_transactions()   
    transactions.append(transaction)   
    save_transactions(transactions) 

    await update.message.reply_text(
        f"Transaction recorded under \"{category}\". Your ledger has been updated."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_handler)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, typing_handler)],
            CHOOSING_CATEGORY: [CallbackQueryHandler(category_handler)],
            TYPING_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_category_handler)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()