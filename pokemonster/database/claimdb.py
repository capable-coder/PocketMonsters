from datetime import datetime
import pytz

from pokemonster.db import MongoDB


class ClaimDB:
    def __init__(self):
        self.db = MongoDB("claim_data")

    # 🌏 IST TIME
    def _today(self):
        ist = pytz.timezone("Asia/Kolkata")
        return datetime.now(ist).strftime("%Y-%m-%d")

    # 🔍 CHECK CLAIMED TODAY
    def has_claimed_today(self, user_id, date=None):
        if date is None:
            date = self._today()

        data = self.db.find_one({
            "_id": user_id
        })

        if not data:
            return False

        return data.get("date") == date

    # 💾 SET CLAIM
    def set_claim(self, user_id, date=None):
        if date is None:
            date = self._today()

        # already claimed today
        data = self.db.find_one({"_id": user_id})
        if data and data.get("date") == date:
            return False

        # ✅ SAFE UPSERT (NO DUPLICATE ERROR)
        self.db.update(
            {"_id": user_id},
            {
                "date": date,
                "claimed": True
            },
            upsert=True
        )

        return True

    # 🧹 OPTIONAL: reset old records (cleanup)
    def clear_old(self, keep_last_days=7):
        ist = pytz.timezone("Asia/Kolkata")
        today = datetime.now(ist)

        # ⚠️ WARNING: ye sab delete kar raha hai
        # future me improve karna
        self.db.delete_many({"claimed": True})
