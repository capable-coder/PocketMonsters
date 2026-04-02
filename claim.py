import random
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from pokemonster import app
from pokemonster.database import Database
from pokemonster.db.userdb import USERSINFO

DB = Database()
UI = USERSINFO()

# -------- LOAD POKEDEX --------
with open("pokedex.json") as f:
    data = json.load(f)


# -------- CLAIM COMMAND --------
@app.on_message(filters.command("claim") & filters.group)
async def claim_pokemon(client: Client, message: Message):

    chat_id = message.chat.id
    user_id = message.from_user.id

    # ❌ Already claimed
    if await DB.is_group_claimed(chat_id):
        return await message.reply_text("😏 Already claimed in this group baby~")

    # ❌ Check bot admin
    bot = await client.get_me()
    bot_member = await client.get_chat_member(chat_id, bot.id)

    if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text("😤 Make me admin first baby!")

    # ❌ Check group size
    try:
        members_count = await client.get_chat_members_count(chat_id)
    except:
        return await message.reply_text("😶 Can't verify group members")

    if members_count < 500:
        return await message.reply_text(
            f"🥺 Need 500+ members baby\nCurrent: {members_count}"
        )

    # 🎲 Random Pokémon
    rand_poke = random.choice(data["poke"])
    name = rand_poke["name"]
    img = rand_poke["link"]
    pid = rand_poke["id"]

    # Clean name
    if "." in name:
        name = " ".join(i.strip() for i in name.split("."))
    elif "-" in name:
        name = " ".join(i.strip() for i in name.split("-"))

    # 💾 Save Pokémon to user
    UI.save_info(chat_id, user_id, pid)

    # ✅ Mark claimed in MongoDB
    await DB.mark_group_claimed(chat_id)

    # 💖 Leena Style Caption
    caption = f"""
💖 Hey {message.from_user.mention}…

You added me here… so I had to reward you 😏✨

🎁 You got: **{name}**

Lucky ho tum… sabko aise gifts nahi milte 😌💕
"""

    # 📸 Send Image
    await message.reply_photo(
        photo=img,
        caption=caption
  )
