import logging
import logging.config
from datetime import date, datetime
import pytz

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram import types

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import (
    SESSION, API_ID, API_HASH, BOT_TOKEN,
    LOG_STR, LOG_CHANNEL, PORT, BIN_CHANNEL
)
from Script import script
from utils import temp

import pyromod.listen
from aiohttp import web

# ---------------- LOGGING ----------------

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# ---------------- WEB SERVER (RENDER) ----------------

async def health_check(request):
    return web.Response(text="OK", status=200)

async def web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    return app

# ---------------- BOT CLASS ----------------

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=5
        )

    async def start(self):
        await super().start()

        temp.BOT = self

        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await Media.ensure_indexes()

        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = f"@{me.username}"

        # ---- Start web server (Render health) ----
        runner = web.AppRunner(await web_server())
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        logging.info(
            f"{me.first_name} started using Pyrogram v{__version__} "
            f"(Layer {layer}) as {me.username}"
        )
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        tz = pytz.timezone("Asia/Kolkata")
        today = date.today()
        now = datetime.now(tz).strftime("%H:%M:%S %p")

        await self.send_message(
            LOG_CHANNEL,
            script.RESTART_TXT.format(today, now)
        )

        try:
            m = await self.send_message(BIN_CHANNEL, "Test")
            await m.delete()
        except Exception:
            logging.error("Bot must be admin in BIN_CHANNEL")
            raise SystemExit

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")

# ---------------- RUN BOT ----------------

if __name__ == "__main__":
    Bot().run()
