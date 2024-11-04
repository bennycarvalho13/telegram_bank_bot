# main.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from pymongo import MongoClient
from config import BOT_TOKEN, MONGO_URI, DATABASE_NAME, COLLECTION_NAME

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users = db[COLLECTION_NAME]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with options."""
    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("Deposit", callback_data="deposit")],
        [InlineKeyboardButton("Withdraw", callback_data="withdraw")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the Banking Bot! Choose an option:", reply_markup=reply_markup)

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the user's balance and last transaction."""
    query = update.callback_query
    user_id = query.from_user.id
    
    user_data = users.find_one({"user_id": user_id})
    if not user_data:
        user_data = {"user_id": user_id, "balance": 0, "last_transaction": None}
        users.insert_one(user_data)
    
    balance = user_data["balance"]
    last_transaction = user_data.get("last_transaction", "No transactions yet.")
    await query.answer()
    await query.edit_message_text(f"Your balance: ${balance}\nLast transaction: {last_transaction}")

    await return_to_main_menu(query)

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the deposit process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("How much would you like to deposit? Please enter a number.")
    context.user_data['depositing'] = True
    context.user_data['withdrawing'] = False  # Reset withdrawal state

async def handle_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the deposit amount input."""
    if context.user_data.get('depositing'):
        user_id = update.message.from_user.id
        amount = update.message.text

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("The amount must be greater than 0.")

            context.user_data['deposit_amount'] = amount
            
            # Ask for confirmation with buttons
            keyboard = [
                [InlineKeyboardButton("Confirm", callback_data="confirm_deposit"),
                 InlineKeyboardButton("Cancel", callback_data="cancel_deposit")],
                [InlineKeyboardButton("Main Menu", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"You are about to deposit ${amount}. Confirm?", reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("Invalid amount. Please enter a positive integer.")
    else:
        await update.message.reply_text("Please initiate the deposit process first by clicking on 'Deposit'.")

async def confirm_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm the deposit."""
    user_id = update.callback_query.from_user.id
    user_data = users.find_one({"user_id": user_id})
    
    amount = context.user_data.get('deposit_amount')
    if amount:
        new_balance = user_data['balance'] + amount
        users.update_one({"user_id": user_id}, {"$set": {"balance": new_balance, "last_transaction": f"Deposited ${amount}"}})

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"Successfully deposited ${amount}. Your new balance is ${new_balance}.")
        
        # Clear the context data
        del context.user_data['deposit_amount']  
        del context.user_data['depositing']  
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("No deposit amount was set. Please initiate a deposit again.")

    await return_to_main_menu(update.callback_query)

async def cancel_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the cancellation of a deposit."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Deposit cancelled. You can start again by selecting 'Deposit' from the main menu.")
    
    await return_to_main_menu(query)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the withdraw process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("How much would you like to withdraw? Please enter a number.")
    context.user_data['withdrawing'] = True
    context.user_data['depositing'] = False  # Reset deposit state

async def handle_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the withdrawal amount input."""
    if context.user_data.get('withdrawing'):
        user_id = update.message.from_user.id
        amount = update.message.text

        try:
            amount = int(amount)
            user_data = users.find_one({"user_id": user_id})

            if amount <= 0:
                raise ValueError("The amount must be greater than 0.")
            if amount > user_data['balance']:
                raise ValueError("Insufficient balance.")

            context.user_data['withdraw_amount'] = amount
            
            # Ask for confirmation with buttons
            keyboard = [
                [InlineKeyboardButton("Confirm", callback_data="confirm_withdraw"),
                 InlineKeyboardButton("Cancel", callback_data="cancel_withdraw")],
                [InlineKeyboardButton("Main Menu", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"You are about to withdraw ${amount}. Confirm?", reply_markup=reply_markup)
        except ValueError as e:
            await update.message.reply_text(str(e))
    else:
        # Here we include an option to go back to deposit
        keyboard = [
            [InlineKeyboardButton("Deposit", callback_data="deposit")],
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please initiate the deposit process first by clicking on 'Deposit'.", reply_markup=reply_markup)

async def confirm_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm the withdrawal."""
    user_id = update.callback_query.from_user.id
    user_data = users.find_one({"user_id": user_id})
    
    amount = context.user_data.get('withdraw_amount')
    if amount:
        new_balance = user_data['balance'] - amount
        users.update_one({"user_id": user_id}, {"$set": {"balance": new_balance, "last_transaction": f"Withdrew ${amount}"}})

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"Successfully withdrew ${amount}. Your new balance is ${new_balance}.")
        
        # Clear the context data
        del context.user_data['withdraw_amount']  
        del context.user_data['withdrawing']  
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("No withdrawal amount was set. Please initiate a withdrawal again.")

    await return_to_main_menu(update.callback_query)

async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the cancellation of a withdrawal."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Withdrawal cancelled. You can start again by selecting 'Withdraw' from the main menu.")
    
    await return_to_main_menu(query)

async def return_to_main_menu(query):
    """Send user back to the main menu options."""
    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("Deposit", callback_data="deposit")],
        [InlineKeyboardButton("Withdraw", callback_data="withdraw")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("What would you like to do next?", reply_markup=reply_markup)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_balance, pattern="^check_balance$"))
    app.add_handler(CallbackQueryHandler(deposit, pattern="^deposit$"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    
    # Handlers for user messages to handle deposit and withdrawal amounts
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deposit_amount))  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_amount))  
    
    # Handlers for confirmation and cancellation
    app.add_handler(CallbackQueryHandler(confirm_deposit, pattern="^confirm_deposit$"))
    app.add_handler(CallbackQueryHandler(cancel_deposit, pattern="^cancel_deposit$"))
    app.add_handler(CallbackQueryHandler(confirm_withdraw, pattern="^confirm_withdraw$"))
    app.add_handler(CallbackQueryHandler(cancel_withdraw, pattern="^cancel_withdraw$"))

    app.run_polling()
