from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, Message
from info import REQST_CHANNEL,ADMINS
from database.users_chats_db import db


ADMIN_ID = 1122334455  # 🔴 change to your Telegram ID
DB_FILE = "fsub.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"channel": None}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

@Client.on_message(filters.command("setfsub") & filters.user(ADMIN_ID))
async def set_fsub(_, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setfsub -100xxxxxxxxxx")
    db["channel"] = int(message.command[1])
    save_db(db)
    await message.reply("✅ Force-sub channel set")

@Client.on_message(filters.command("fsub") & filters.user(ADMIN_ID))
async def show_fsub(_, message):
    await message.reply(f"📌 Current channel:\n`{db['channel']}`")

@Client.on_message(filters.private)
async def force_sub(_, message):
    if not db["channel"]:
        return

    try:
        await _.get_chat_member(db["channel"], message.from_user.id)
    except Exception:
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/c/{str(db['channel'])[4:]}")]]
        )
        await message.reply(
            "❗ You must join the channel to use this bot.",
            reply_markup=btn
        )
        return
