# handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_user_data, update_balance

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("Deposit", callback_data="deposit")],
        [InlineKeyboardButton("Withdraw", callback_data="withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to the Banking Bot! Choose an option:", reply_markup=reply_markup)

def check_balance(update: Update, context: CallbackContext):
    user = get_user_data(update.effective_user.id)
    balance = user["balance"]
    last_transaction = user["last_transaction"]
    message = f"Your current balance is {balance}."
    if last_transaction:
        message += f"\nLast transaction: {last_transaction['type']} of {last_transaction['amount']} on {last_transaction['timestamp']}"
    update.callback_query.message.reply_text(message)

def deposit_start(update: Update, context: CallbackContext):
    # Implement multi-step deposit functionality here
    pass

def withdraw_start(update: Update, context: CallbackContext):
    # Implement multi-step withdraw functionality here
    pass
