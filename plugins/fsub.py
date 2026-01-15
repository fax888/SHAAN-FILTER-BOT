from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os
# ✅ SAFE IMPORT (Render compatible)
try:
    from bot import client
except Exception:
    client = None

# ❌ Stop plugin loading if client is missing
if client is None:
    raise RuntimeError("❌ Telethon client not found. Check bot.py exports.")

# ================= DATABASE =================
DB_FILE = "fsub_settings.json"

# ⚠️ REPLACE WITH YOUR REAL TELEGRAM ID
ADMIN_ID = 1122334455  

def load_db():
    if not os.path.exists(DB_FILE):
        return {"chat1": None, "chat2": None, "total_req": 0}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# ================= COMMANDS =================

@client.on(events.NewMessage(pattern=r'^/setchat1 (.+)'))
async def set_chat_1(event):
    if event.sender_id != ADMIN_ID:
        return
    db["chat1"] = event.pattern_match.group(1)
    save_db(db)
    await event.respond(f"✅ Channel 1 set to:\n`{db['chat1']}`")

@client.on(events.NewMessage(pattern=r'^/setchat2 (.+)'))
async def set_chat_2(event):
    if event.sender_id != ADMIN_ID:
        return
    db["chat2"] = event.pattern_match.group(1)
    save_db(db)
    await event.respond(f"✅ Channel 2 set to:\n`{db['chat2']}`")

@client.on(events.NewMessage(pattern=r'^/delchat1$'))
async def del_chat_1(event):
    if event.sender_id != ADMIN_ID:
        return
    db["chat1"] = None
    save_db(db)
    await event.respond("🗑️ Channel 1 removed.")

@client.on(events.NewMessage(pattern=r'^/delchat2$'))
async def del_chat_2(event):
    if event.sender_id != ADMIN_ID:
        return
    db["chat2"] = None
    save_db(db)
    await event.respond("🗑️ Channel 2 removed.")

@client.on(events.NewMessage(pattern=r'^/totalreq$'))
async def total_req(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.respond(f"📊 Total Requests: `{db.get('total_req', 0)}`")

@client.on(events.NewMessage(pattern=r'^/purge_one$'))
async def purge_one(event):
    if event.sender_id != ADMIN_ID:
        return
    db["chat1"] = None
    save_db(db)
    await event.respond("🧹 DB 1 cleared.")

# ================= ADMIN PANEL =================

@client.on(events.NewMessage(pattern=r'^/admin$'))
async def admin_panel(event):
    if event.sender_id != ADMIN_ID:
        return

    text = (
        "🧩 **Force Subscribe Control Panel**\n\n"
        f"• Channel 1: `{db['chat1']}`\n"
        f"• Channel 2: `{db['chat2']}`"
    )

    buttons = [
        [
            Button.inline("Set Chat 1", b"set1"),
            Button.inline("Set Chat 2", b"set2")
        ],
        [
            Button.inline("Clear Chat 1", b"purge1"),
            Button.inline("Clear Chat 2", b"purge2")
        ]
    ]

    await event.respond(text, buttons=buttons)
