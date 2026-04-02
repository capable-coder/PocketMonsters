import random
import json

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus

from pokemonster import app
from pokemonster.db.userdb import USERSINFO
from pokemonster.database.claimdb import ClaimDB

UI = USERSINFO()
claim_db = ClaimDB()

# -------- LOAD POKEDEX --------
with open("pokedex.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# -------- DM PROTECTION --------
@app.on_message(filters.command("claim") & filters.private)
async def claim_dm(client: Client, message: Message):
    await message.reply_text(
        "😌 This command works only in groups baby...\n\nAdd me to a group and try there 💖"
    )


# -------- CLAIM COMMAND --------
@app.on_message(filters.command("claim") & filters.group, group=5)
async def claim_pokemon(client: Client, message: Message):

    chat_id = message.chat.id
    user_id = message.from_user.id

    # ❌ Already claimed
    if claim_db.is_claimed(chat_id):
        return await message.reply_text(
            "😏 Already claimed in this group baby~ try another group 💕"
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

    # 💾 Save Pokémon
    UI.save_info(chat_id, user_id, pid)

    # ✅ Mark claimed
    claim_db.set_claimed(chat_id)

    # 💖 Buttons
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💖 View Collection", callback_data="pokedex"),
                InlineKeyboardButton("🎮 Play More", callback_data="games")
            ]
        ]
    )

    # 💖 Caption
    caption = f"""
💖 Hey {message.from_user.mention}…

So you brought me here… I like that 😏✨

🎁 Your reward:
✨ **{name}**

Careful… this one is rare 👀💕

Enjoy it… not everyone gets lucky like you 😌💗
"""

    await message.reply_photo(
        photo=img,
        caption=caption,
        reply_markup=buttons
    )


# -------- POKEDEX CALLBACK (FIXED PART) --------
@app.on_callback_query(filters.regex("^pokedex$"))
async def show_pokedex(client: Client, callback_query: CallbackQuery):

    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await callback_query.answer("📦 Loading your Pokédex...")

    # ⚠️ IMPORTANT: check your actual DB function name
    try:
        user_data = UI.get_user_pokemon(chat_id, user_id)
    except:
        user_data = None

    if not user_data:
        return await callback_query.message.edit_text(
            "😢 You don't have any Pokémon yet!\n\nUse /claim to start your journey 💖"
        )

    text = "💖 Your Pokémon Collection:\n\n"

    for poke in user_data:
        try:
            text += f"🎮 ID: {poke['pid']}\n"
        except:
            text += f"🎮 ID: {poke}\n"

    await callback_query.message.edit_text(text)
