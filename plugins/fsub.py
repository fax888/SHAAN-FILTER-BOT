import os
import json
from telethon import events, Button, functions, errors

# Import the client from your main file (bot.py or main.py)
# This ensures you don't get 'coroutine' errors
try:
    from bot import client 
except ImportError:
    from main import client

# --- DATABASE LOGIC ---
DB_FILE = "fsub_settings.json"
ADMIN_ID = 1122334455  # <--- REPLACE WITH YOUR TELEGRAM ID

def load_db():
    if not os.path.exists(DB_FILE):
        return {"chat1": None, "chat2": None, "total_req": 0}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- COMMANDS ---

# Set Channel 1
@client.on(events.NewMessage(pattern='/setchat1 (.+)'))
async def set_chat_1(event):
    if event.sender_id != ADMIN_ID: return
    chat_id = event.pattern_match.group(1)
    db["chat1"] = chat_id
    save_db(db)
    await event.respond(f"✅ **Channel 1 set to:** `{chat_id}`")

# Set Channel 2
@client.on(events.NewMessage(pattern='/setchat2 (.+)'))
async def set_chat_2(event):
    if event.sender_id != ADMIN_ID: return
    chat_id = event.pattern_match.group(1)
    db["chat2"] = chat_id
    save_db(db)
    await event.respond(f"✅ **Channel 2 set to:** `{chat_id}`")

# Delete Channel 1
@client.on(events.NewMessage(pattern='/delchat1'))
async def del_chat_1(event):
    if event.sender_id != ADMIN_ID: return
    db["chat1"] = None
    save_db(db)
    await event.respond("🗑️ **Channel 1 removed.**")

# Show Total Requests
@client.on(events.NewMessage(pattern='/totalreq'))
async def total_req(event):
    if event.sender_id != ADMIN_ID: return
    count = db.get("total_req", 0)
    await event.respond(f"📊 **Total Requests:** `{count}`")

# Purge Database 1
@client.on(events.NewMessage(pattern='/purge_one'))
async def purge_one(event):
    if event.sender_id != ADMIN_ID: return
    db["chat1"] = None
    save_db(db)
    await event.respond("🧹 **DB 1 Cleared.**")

# --- ADMIN PANEL ---
@client.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    if event.sender_id != ADMIN_ID: return
    text = (
        "🧩 **Force Subscribe Control Panel**\n\n"
        f"• **Channel 1:** `{db['chat1']}`\n"
        f"• **Channel 2:** `{db['chat2']}`\n"
    )
    buttons = [
        [Button.inline("Set Chat 1", b"set1"), Button.inline("Set Chat 2", b"set2")],
        [Button.inline("Clear DB 1", b"purge1"), Button.inline("Clear DB 2", b"purge2")]
    ]
    await event.respond(text, buttons=buttons)
