import logging
import os
from pyrogram import Client

from .config import API_ID, API_HASH, BOT_TOKEN


# ---------------- SAFE LOG PATH ----------------
LOG_DIR = "pokemonster/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "logEvents.txt")


# ---------------- LOGGING ----------------
FORMAT = "[ok] %(message)s"

logging.basicConfig(
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
)

logging.getLogger("pyrogram").setLevel(logging.INFO)

LOGGER = logging.getLogger("[ok]")


# ---------------- PYROGRAM CLIENT ----------------
app = Client(
    name="client3",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
    # ❌ plugins hata diya
)

LOGGER.info("Client initialized successfully")
