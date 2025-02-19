const TelegramBot = require('node-telegram-bot-api');
const { exec } = require('child_process');

// Replace with your actual Telegram bot token
const token = '7324603047:AAE5tXfan8-JWMBoIL4B9LlnddaUsi3F2Zg';
const bot = new TelegramBot(token, { polling: true });

// Command to execute
const commandToRun = `./megoxer ${target} ${port} ${time} 900`;

// Listen for the /run command
bot.onText(/\/run/, (msg) => {
    const chatId = msg.chat.id;

    // Execute the shell command
    exec(commandToRun, (error, stdout, stderr) => {
        if (error) {
            bot.sendMessage(chatId, `Error: ${error.message}`);
            return;
        }
        if (stderr) {
            bot.sendMessage(chatId, `Stderr: ${stderr}`);
            return;
        }
        // Send the output of the command back to the Telegram chat
        bot.sendMessage(chatId, `Output: ${stdout}`);
    });
});

// Start the bot
console.log("Bot is running...");