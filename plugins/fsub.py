from telethon import TelegramClient, events, Button, functions, errors


# --- CONFIGURATION ---
API_ID = 1234567          
API_HASH = 'your_api_hash'    
BOT_TOKEN = 'your_bot_token'  
ADMIN_ID = 1122334455     # Your Telegram ID
DB_FILE = "fsub_settings.json"

client = TelegramClient('fsub_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- DATABASE MANAGEMENT ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {"chat1": None, "chat2": None, "total_req": 0}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- HELPER: CHECK SUBSCRIPTION ---
async def is_subscribed(user_id):
    for key in ["chat1", "chat2"]:
        chat = db.get(key)
        if chat:
            try:
                # This checks if the user is a participant of the channel
                await client(functions.channels.GetParticipantRequest(
                    channel=chat,
                    participant=user_id
                ))
            except errors.rpcerrorlist.UserNotParticipantError:
                return False # User is missing from at least one required channel
            except Exception as e:
                print(f"Error checking {chat}: {e}")
    return True

# --- SETTINGS COMMANDS ---

@client.on(events.NewMessage(pattern='/setchat1 (.+)'))
async def set_1(event):
    if event.sender_id != ADMIN_ID: return
    db["chat1"] = event.pattern_match.group(1)
    save_db(db)
    await event.respond(f"✅ **Channel 1 Updated:** `{db['chat1']}`")

@client.on(events.NewMessage(pattern='/setchat2 (.+)'))
async def set_2(event):
    if event.sender_id != ADMIN_ID: return
    db["chat2"] = event.pattern_match.group(1)
    save_db(db)
    await event.respond(f"✅ **Channel 2 Updated:** `{db['chat2']}`")

@client.on(events.NewMessage(pattern='/delchat1'))
async def del_1(event):
    if event.sender_id != ADMIN_ID: return
    db["chat1"] = None
    save_db(db)
    await event.respond("🗑️ **Channel 1 Removed.**")

# --- THE CONTROL PANEL ---
@client.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    if event.sender_id != ADMIN_ID: return
    
    status_text = (
        "🧩 **Force Subscribe Control Panel**\n\n"
        f"📢 **Channel 1:** `{db['chat1'] or 'Not Set'}`\n"
        f"📢 **Channel 2:** `{db['chat2'] or 'Not Set'}`\n"
        f"📊 **Total Database:** `{db['total_req']}` Users\n\n"
        "Click a button to manage settings:"
    )
    
    buttons = [
        [Button.inline("❌ Clear Chat 1", b"purge1"), Button.inline("❌ Clear Chat 2", b"purge2")],
        [Button.inline("📊 Refresh Stats", b"stats")]
    ]
    await event.respond(status_text, buttons=buttons)

# --- THE ACTUAL FORCE SUB LOGIC ---
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    
    # Increment total requests for stats
    db["total_req"] += 1
    save_db(db)

    if await is_subscribed(user_id):
        await event.respond("Welcome! You have access to the bot.")
    else:
        # User is not subscribed, show them the links
        buttons = []
        if db["chat1"]:
            buttons.append([Button.url("Join Channel 1", f"https://t.me/{db['chat1'].replace('@', '')}")])
        if db["chat2"]:
            buttons.append([Button.url("Join Channel 2", f"https://t.me/{db['chat2'].replace('@', '')}")])
        
        buttons.append([Button.url("🔄 Try Again", f"https://t.me/{(await client.get_me()).username}?start=true")])
        
        await event.respond(
            "⚠️ **Access Denied!**\n\nYou must join our channels to use this bot.",
            buttons=buttons
        )

print("F-Sub Bot is running...")
client.run_until_disconnected()

