import os
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------- SAFE ENV ----------------
def get_env(*keys, default=None):
    for k in keys:
        v = os.getenv(k)
        if v:
            return v
    return default


# ---------------- CONFIG ----------------
MONGO_URI = get_env("MONGO_URI_1", "MONGO_URI_2", "MONGO_URI", "MONGO_URL")
MONGO_NAME = get_env("MONGO_NAME_1", "MONGO_NAME_2", "MONGO_NAME", default="pocketmonsters")

# ---------------- SAFETY ----------------
if not MONGO_URI:
    raise Exception("❌ Mongo URI missing in environment variables")

if not MONGO_NAME:
    MONGO_NAME = "pocketmonsters"


# ---------------- CLIENT ----------------
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_NAME]

print(">> MongoDB Connected Successfully <<")


# ---------------- COLLECTIONS ----------------
msg_freq = db.msg_freq
pokecoin = db.pokecoin
user_base = db.user_base


# ---------------- USERS ----------------
async def update_user(user_id: int, username: str, name: str):
    await user_base.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "username": username, "name": name}},
        upsert=True
    )


async def get_user(user_id: int):
    return await user_base.find_one({"user_id": user_id}) or {}


# ---------------- FREQUENCY ----------------
async def add_frequency(chat_id: int, frequency: int, chat_title: str):
    await msg_freq.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_title": chat_title, "frequency": frequency}},
        upsert=True,
    )


async def read_frequency(chat_id: int):
    data = await msg_freq.find_one({"chat_id": chat_id})
    return data.get("frequency", 50) if data else 50   # ✅ default = 50


# ---------------- POKECOIN ----------------
async def add_pokecoin(user_id: int, money: int, username: str):
    data = await pokecoin.find_one({"user_id": user_id})

    old = int(data.get("pokecoin", 0)) if data else 0
    new = old + int(money)

    await pokecoin.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "username": username, "pokecoin": new}},
        upsert=True,
    )


async def subtract_pokecoin(user_id: int, money: int):
    data = await pokecoin.find_one({"user_id": user_id})
    if not data:
        return

    new = int(data.get("pokecoin", 0)) - int(money)

    await pokecoin.update_one(
        {"user_id": user_id},
        {"$set": {"pokecoin": new}},
        upsert=True,
    )


async def make_coins_0(user_id: int):
    await pokecoin.update_one(
        {"user_id": user_id},
        {"$set": {"pokecoin": 0}},
        upsert=True,
    )


async def read_money(user_id: int):
    data = await pokecoin.find_one({"user_id": user_id})
    return int(data.get("pokecoin", 0)) if data else 0


# ---------------- LEADERBOARD ----------------
async def sorted_money_database(descending: bool = True):
    data = await pokecoin.find().to_list(length=None)

    if not data:
        return []

    return sorted(
        data,
        key=lambda x: int(x.get("pokecoin", 0)),
        reverse=descending,
    )


# ================================
# ✅ FINAL DATABASE CLASS (IMPORTANT)
# ================================
class Database:

    async def setup(self):
        return True

    # 🔹 Frequency
    async def read_frequency(self, chat_id):
        return await read_frequency(chat_id)

    async def add_frequency(self, chat_id, frequency, chat_title):
        return await add_frequency(chat_id, frequency, chat_title)

    # 🔹 Coins
    async def add_pokecoin(self, user_id, amount, username):
        return await add_pokecoin(user_id, amount, username)

    async def read_money(self, user_id):
        return await read_money(user_id)

    async def subtract_pokecoin(self, user_id, amount):
        return await subtract_pokecoin(user_id, amount)

    async def make_coins_0(self, user_id):
        return await make_coins_0(user_id)

    # 🔹 Users
    async def update_user(self, user_id, username, name):
        return await update_user(user_id, username, name)

    async def get_user(self, user_id):
        return await get_user(user_id)

    # 🔹 Leaderboard
    async def sorted_money_database(self, descending=True):
        return await sorted_money_database(descending)
