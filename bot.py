# ✅ Advanced Stylish Subtitle Translator Bot
# 🔥 Google Translate (Web API) Based | No external pip for googletrans needed
# 🐳 Dockerized | Flask Keepalive | Progress Bar | Stylish UI

import os
import json
import aiohttp
import zipfile
import aiofiles
import urllib.parse
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ----------------- Load Config -----------------
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "")
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", 20))

# ----------------- Globals -----------------
user_tasks = {}
user_limits = {}
LANGS = {
    "bn": "Bengali 🇧🇩",
    "hi": "Hindi 🇮🇳",
    "en": "English 🇬🇧",
    "es": "Spanish 🇪🇸"
}

# ----------------- Google Translate Web API -----------------
async def google_translate(text: str, target: str = "en") -> str:
    try:
        base = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target,
            "dt": "t",
            "q": text,
        }
        url = base + "?" + urllib.parse.urlencode(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.text()
                data = json.loads(result)
                return ''.join([part[0] for part in data[0] if part[0]])
    except:
        return text

async def translate_subtitles(content: str, lang: str, update_progress):
    lines = content.splitlines()
    total = len(lines)
    result = []
    for i, line in enumerate(lines):
        if "-->" in line or line.strip() == "" or line[0].isdigit():
            result.append(line)
        else:
            result.append(await google_translate(line, target=lang))
        if i % (total // 5 + 1) == 0:
            await update_progress(f"🔄 Progress: {int((i/total)*100)}%")
    await update_progress("✅ Translation complete.")
    return "\n".join(result)

# ----------------- File Handlers -----------------
async def extract_zip(zip_path: str, extract_to: str = "temp/") -> list:
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        return [os.path.join(extract_to, name) for name in zip_ref.namelist()]

async def read_file(file_path: str) -> str:
    async with aiofiles.open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        return await f.read()

async def write_file(file_path: str, content: str):
    async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
        await f.write(content)

# ----------------- UI Helpers -----------------
def lang_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇩 Bengali", callback_data="lang_bn"),
         InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

async def is_subscribed(bot, user_id):
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ----------------- Bot Client -----------------
bot = Client("sub_translator", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    if not await is_subscribed(client, message.from_user.id):
        return await message.reply("📢 Please join our channel first!", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")]
        ]))
    await message.reply("👋 Send a .srt/.ass/.zip file to translate it to your language.")

@bot.on_message(filters.document)
async def handle_doc(client, message: Message):
    uid = message.from_user.id
    if user_tasks.get(uid):
        return await message.reply("⏳ One task at a time.")
    if user_limits.get(uid, 0) >= DAILY_LIMIT:
        return await message.reply("🚫 Daily limit reached.")
    user_tasks[uid] = {"file": message}
    user_limits[uid] = user_limits.get(uid, 0) + 1
    await message.reply("🌐 Choose language:", reply_markup=lang_buttons())

@bot.on_callback_query(filters.regex(r"lang_(.+)"))
async def handle_lang(client, cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    uid = cb.from_user.id
    task = user_tasks.get(uid)
    if not task: return await cb.message.edit("⚠️ No task found.")

    msg = task['file']
    file_path = await msg.download()
    await cb.message.edit("📥 File downloaded. Starting...")

    async def prog_bar(status):
        await cb.message.edit(status)

    try:
        files = await extract_zip(file_path) if file_path.endswith(".zip") else [file_path]
        for f in files:
            if f.endswith((".srt", ".ass")):
                content = await read_file(f)
                translated = await translate_subtitles(content, lang, prog_bar)
                out_path = f"{f}.{lang}.txt"
                await write_file(out_path, translated)
                await cb.message.reply_document(out_path, caption=f"✅ Done: {LANGS[lang]}")
    except Exception as e:
        await cb.message.edit(f"❌ Failed: {e}")
    finally:
        user_tasks.pop(uid, None)

@bot.on_callback_query(filters.regex("cancel"))
async def cancel(client, cb: CallbackQuery):
    user_tasks.pop(cb.from_user.id, None)
    await cb.message.edit("❎ Task cancelled.")

# ----------------- Run Flask + Bot -----------------
if __name__ == '__main__':
    import threading
    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def index(): return '✅ Bot running'

    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.run()
