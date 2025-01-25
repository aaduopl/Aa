import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the sticker file ID
STICKER_FILE_ID = 'AAMCBQADGQEAATEeY2eUrxc1oSuoT2nM5MJ5MYcT5156AAKeCgACTtYwVgFrI1FutgoDAQAHbQADNgQ'

# Function to start the bot
def @user_x_dead(update, context):
    update.message.reply_text('Hey there my Owner is offline please wait sometime')

# Function to send a sticker
def send_sticker(update, context):
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_FILE_ID)

# Main function to run the bot
def main():
    # Replace 'YOUR_TOKEN' with your bot's API token
    updater = Updater('7324603047:AAGq8qfsYAB2_-6A7ZoKxB57_td0ofrKDn0', use_context=True)
    
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("aadi", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, send_sticker))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
