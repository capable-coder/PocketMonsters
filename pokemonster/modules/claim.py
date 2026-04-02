import random
import json
from datetime import datetime
import pytz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from pokemonster import app
from pokemonster.db.userdb import USERSINFO
from pokemonster.database.claimdb import ClaimDB

UI = USERSINFO()
claim_db = ClaimDB()

# -------- LOAD POKEDEX --------
with open("pokedex.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# 🌏 IST TIME
IST = pytz.timezone("Asia/Kolkata")

def get_today():
    return datetime.now(IST).strftime("%Y-%m-%d")


# -------- CLAIM COMMAND --------
@app.on_message(filters.command("claim"))
async def claim_pokemon(client: Client, message: Message):

    user_id = message.from_user.id
    chat_id = message.chat.id
    today = get_today()

    # ❌ Already claimed today
    if claim_db.has_claimed_today(user_id, today):
        return await message.reply_text(
            "😏 Heyyy… slow down baby~\n"
            "You already took your reward today 💕\n\n"
            "Come back tomorrow at 12 AM IST… I’ll be waiting for you 😌💖"
        )

    # 🎲 Pick random Pokémon
    rand_poke = random.choice(data["poke"])
    name = rand_poke["name"]
    img = rand_poke["link"]
    pid = rand_poke["id"]

    # ✨ Clean name
    if "." in name:
        name = " ".join(i.strip() for i in name.split("."))
    elif "-" in name:
        name = " ".join(i.strip() for i in name.split("-"))

    # 💾 Save Pokémon to user
    UI.save_info(chat_id, user_id, pid)

    # 💾 Save daily claim
    claim_db.set_claim(user_id, today)

    # 💖 Buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💖 My Pokédex", callback_data="pokedex"),
            InlineKeyboardButton("🎮 More Fun", callback_data="games")
        ]
    ])

    # 💌 Flirty Caption
    caption = f"""
💖 Hey {message.from_user.mention}…

I was waiting for you… and you finally came 😏✨

🎁 Your daily Pokémon reward is here:
✨ **{name}**

Don’t get too attached… or maybe do 😌💕

⏳ Come back tomorrow at 12 AM IST… I might miss you 💖
"""

    await message.reply_photo(
        photo=img,
        caption=caption,
        reply_markup=buttons
    )


# -------- POKEDEX CALLBACK --------
@app.on_callback_query(filters.regex("^pokedex$"))
async def show_pokedex(client: Client, callback_query: CallbackQuery):

    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await callback_query.answer("💖 Opening your Pokédex…")

    user_data = UI.get_user_pokemon(chat_id, user_id)

    if not user_data:
        return await callback_query.message.edit_text(
            "😢 No Pokémon yet baby…\n\nUse /claim and start your journey with me 💕"
        )

    text = "💖 Your Lovely Pokémon Collection:\n\n"

    for poke in user_data:
        try:
            text += f"🎮 Pokémon ID: {poke['pid']}\n"
        except:
            text += f"🎮 Pokémon ID: {poke}\n"

    text += "\n😏 Not bad… you’re building a strong collection baby~"

    await callback_query.message.edit_text(text)
