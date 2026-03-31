from pyrogram import filters
from dotenv import load_dotenv
import os

load_dotenv()

devs = [8400280060]
users_filt = filters.user(devs)

# ---------------- SAFE ENV LOADER ----------------
def get_env(*keys, default=None):
    for key in keys:
        val = os.getenv(key)
        if val:
            return val
    return default


API_ID = int(get_env("API_ID"))
API_HASH = get_env("API_HASH")
BOT_TOKEN = get_env("BOT_TOKEN")

# ---------------- MONGO (UNIFIED NAMES) ----------------
MONGO_URI = get_env("MONGO_URI_1", "MONGO_URI", "MONGO_URL")
MONGO_NAME = get_env("MONGO_NAME_1", "MONGO_NAME", default="pocketmonsters")

MONGO_URI2 = get_env("MONGO_URI_2")
MONGO_NAME2 = get_env("MONGO_NAME_2", default="pocketmonsters")
