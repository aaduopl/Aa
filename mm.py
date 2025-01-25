import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a command handler. Here we use /start command.
def aadi(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I will react to your messages!')

# Define a message handler that reacts to messages
def react_to_message(update: Update, context: CallbackContext) -> None:
    # React with a thumbs-up emoji
    update.message.reply_text('🕊️')

def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater("7324603047:AAGq8qfsYAB2_-6A7ZoKxB57_td0ofrKDn0")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler("aadi", aadi))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, react_to_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
