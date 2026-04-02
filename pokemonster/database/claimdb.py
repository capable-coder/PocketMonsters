from . import MongoDB

class ClaimDB:
    def __init__(self):
        self.db = MongoDB("claim_data")

    def is_claimed(self, chat_id):
        data = self.db.find_one({"_id": chat_id})
        return bool(data and data.get("claimed"))

    def set_claimed(self, chat_id):
        if self.db.find_one({"_id": chat_id}):
            self.db.update({"_id": chat_id}, {"claimed": True})
        else:
            self.db.insert_one({
                "_id": chat_id,
                "claimed": True
            })
