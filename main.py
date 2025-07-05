from pyrogram import Client
from bot.config import API_ID, API_HASH, BOT_TOKEN
from bot.handlers import register_handlers

app = Client("sub_trans_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

register_handlers(app)

if __name__ == "__main__":
    app.run()
