import logging
import csv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states
NAME, USERNAME, DEPARTMENT, PREFERENCE = range(4)

# Path for the CSV file
DATA_FILE = 'registration_data.csv'
GROUP_INVITE_LINK = "GROUP_INVITE_LINK"  # Replace with your actual group invite link

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome to ARU CLUN Techno Registration! What's your name?")
    return NAME

# Get name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Nice to meet you, {update.message.text}! What's your Telegram username?")
    return USERNAME

# Get username
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text("What is your department?")
    return DEPARTMENT

# Get department
async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['department'] = update.message.text
    await update.message.reply_text("Do you prefer DevOps or AI? (Please type 'DevOps' or 'AI')")
    return PREFERENCE

# Get preference and save data
async def get_preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['preference'] = update.message.text
    
    # Save to CSV
    with open(DATA_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([context.user_data['name'], context.user_data['username'], context.user_data['department'], context.user_data['preference']])

    await update.message.reply_text(f"Thank you, {context.user_data['name']}! You are registered with the following details:\n"
                                     f"Username: {context.user_data['username']}\n"
                                     f"Department: {context.user_data['department']}\n"
                                     f"Preference: {context.user_data['preference']}\n\n"
                                     f"Please join our group using the link: {GROUP_INVITE_LINK}",
                                     parse_mode='Markdown')

    return ConversationHandler.END

# Command to access data
async def access_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id != Telegram_User_ID:  # Replace with your Telegram user ID
        await update.message.reply_text("You are not authorized to access this data.")
        return

    try:
        with open(DATA_FILE, mode='r') as file:
            data = file.read()
            await update.message.reply_text(f"Here is the collected registration data:\n{data}")
    except FileNotFoundError:
        await update.message.reply_text("No data found yet.")

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Registration canceled.')
    return ConversationHandler.END

# Main function to set up the bot
def main() -> None:
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)],
            PREFERENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_preference)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('access_data', access_data))

    application.run_polling()

if __name__ == '__main__':
    main()
