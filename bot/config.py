import os
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "")
ADMIN_USERS = list(map(int, os.getenv("ADMIN_USERS", "").split()))
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", 20))
