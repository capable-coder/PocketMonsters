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
            "_id": user_id,
            "date": date
        })

        return bool(data)

    # 💾 SET CLAIM
    def set_claim(self, user_id, date=None):
        if date is None:
            date = self._today()

        existing = self.db.find_one({
            "_id": user_id,
            "date": date
        })

        # already claimed today
        if existing:
            return False

        self.db.insert_one({
            "_id": user_id,
            "date": date,
            "claimed": True
        })

        return True

    # 🧹 OPTIONAL: reset old records (cleanup)
    def clear_old(self, keep_last_days=7):
        ist = pytz.timezone("Asia/Kolkata")
        today = datetime.now(ist)

        # simple cleanup logic (optional)
        # you can improve later with full date comparison
        self.db.delete_many({"claimed": True})
