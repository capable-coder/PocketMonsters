import random
import json

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from pokemonster import app
from pokemonster.db.userdb import USERSINFO

# ✅ IMPORT CLAIM DB
from pokemonster.database.claimdb import ClaimDB

UI = USERSINFO()
claim_db = ClaimDB()

# -------- LOAD POKEDEX --------
with open("pokedex.json") as f:
    data = json.load(f)


# -------- CLAIM COMMAND --------
@app.on_message(filters.command("claim") & filters.group)
async def claim_pokemon(client: Client, message: Message):

    chat_id = message.chat.id
    user_id = message.from_user.id

    # ❌ Already claimed
    if claim_db.is_claimed(chat_id):
        return await message.reply_text(
            "😏 Already claimed in this group baby~ try somewhere else 💕"
        )

    # ❌ Check bot admin
    bot = await client.get_me()
    bot_member = await client.get_chat_member(chat_id, bot.id)

    if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text(
            "😤 Make me admin first baby… then I’ll reward you 💅"
        )

    # ❌ Check group size
    try:
        members_count = await client.get_chat_members_count(chat_id)
    except:
        return await message.reply_text(
            "😶 I can't check members right now… try again later"
        )

    if members_count < 500:
        return await message.reply_text(
            f"🥺 I only reward big groups baby...\n👥 Need: 500+\n📊 Current: {members_count}"
        )

    # 🎲 Random Pokémon
    rand_poke = random.choice(data["poke"])
    name = rand_poke["name"]
    img = rand_poke["link"]
    pid = rand_poke["id"]

    # 🔧 Clean name
    if "." in name:
        name = " ".join(i.strip() for i in name.split("."))
    elif "-" in name:
        name = " ".join(i.strip() for i in name.split("-"))

    # 💾 Save Pokémon (same as catch system)
    UI.save_info(chat_id, user_id, pid)

    # ✅ Mark claimed in DB
    claim_db.set_claimed(chat_id)

    # 💖 Leena Style Caption
    caption = f"""
💖 Hey {message.from_user.mention}…

So you brought me here… I like that 😏✨

🎁 Your reward:
✨ **{name}**

Careful… this one is rare 👀💕

Enjoy it… not everyone gets lucky like you 😌💗
"""

    # 📸 Send Pokémon Image
    await message.reply_photo(
        photo=img,
        caption=caption
    )
