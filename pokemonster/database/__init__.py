from threading import RLock
import os
from motor.motor_asyncio import AsyncIOMotorClient

from ..config import MONGO_NAME2, MONGO_URI2

INSERTION_LOCK = RLock()


def get_env(*keys, default=None):
    """Safe env fallback reader"""
    for key in keys:
        val = os.getenv(key)
        if val:
            return val
    return default


class Database:
    def __init__(self):

        # ✅ SAFE MONGO URI (multi fallback)
        mongo_uri = (
            MONGO_URI2
            or get_env("MONGO_URI2", "MONGO_URL", "MONGO_URI")
        )

        # ✅ SAFE DB NAME (multi fallback)
        mongo_name = (
            MONGO_NAME2
            or get_env("MONGO_NAME2", "MONGO_NAME")
            or "pocketmonsters"
        )

        # ❌ HARD STOP IF MISSING
        if not mongo_uri:
            raise Exception("❌ Mongo URI missing (check MONGO_URI2 / MONGO_URL)")

        if not isinstance(mongo_name, str):
            raise Exception("❌ Mongo DB name invalid")

        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[mongo_name]

        self.msg_freq = self.db.msg_freq
        self.pokecoin = self.db.pokecoin

    async def setup(self):
        try:
            await self.client.admin.command("ping")
            print(">> Database Connection Successful! <<")
        except Exception as e:
            print(f"Database Connection Failed: {e}")
            quit(1)

    # ---------------- USERS ----------------
    async def update_user(self, user_id: int, username: str, name: str):
        context = {"user_id": user_id, "username": username, "name": name}
        await self.db.user_base.update_one(
            {"user_id": user_id}, {"$set": context}, upsert=True
        )

    async def get_user(self, user_id: int):
        return await self.db.user_base.find_one({"user_id": user_id}) or {}

    # ---------------- FREQUENCY ----------------
    async def add_frequency(self, chat_id: int, frequency: int, chat_title: str):
        await self.msg_freq.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_title": chat_title, "frequency": frequency}},
            upsert=True,
        )

    async def read_frequency(self, chat_id: int) -> int:
        data = await self.msg_freq.find_one({"chat_id": chat_id})
        return data["frequency"] if data else 100

    # ---------------- POKECOIN ----------------
    async def add_pokecoin(self, user_id: int, money: int, username: str):
        data = await self.pokecoin.find_one({"user_id": user_id})

        old_money = int(data["pokecoin"]) if data else 0
        new_money = old_money + int(money)

        await self.pokecoin.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "pokecoin": new_money}},
            upsert=True,
        )

    async def subtract_pokecoin(self, user_id: int, money: int):
        data = await self.pokecoin.find_one({"user_id": user_id})
        if not data:
            return

        new_money = int(data.get("pokecoin", 0)) - int(money)

        await self.pokecoin.update_one(
            {"user_id": user_id},
            {"$set": {"pokecoin": new_money}},
            upsert=True,
        )

    async def make_coins_0(self, user_id: int):
        await self.pokecoin.update_one(
            {"user_id": user_id},
            {"$set": {"pokecoin": 0}},
            upsert=True,
        )

    async def read_money(self, user_id: int):
        with INSERTION_LOCK:
            data = await self.pokecoin.find_one({"user_id": user_id})
            return data["pokecoin"] if data else 0

    # ---------------- LEADERBOARD ----------------
    async def sorted_money_database(self, descending: bool = True):
        with INSERTION_LOCK:
            data = await self.pokecoin.find().to_list(None)
            if not data:
                return []

            return sorted(
                data,
                key=lambda x: int(x.get("pokecoin", 0)),
                reverse=descending,
            )
