import random

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import (
    ChatMember,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from pokemonster import app

# 🔥 CHANGE THESE LINKS
BOT_USERNAME = "im_Pokedexbot"
SUPPORT_LINK = "https://t.me/+xduW4Tvtl2Y3ODZl"
UPDATE_LINK = "https://t.me/II_ADI_II"
OWNER_LINK = "https://t.me/II_ADI_II"

START_IMG = "https://i.ibb.co/PGS2JdYX/x.jpg"


# 🔹 RANDOM TEXT
def random_text(message):
    responses = [
        f"🔥 Ready to catch Pokémons {message.from_user.first_name}?",
        f"🎮 Let's start your journey {message.from_user.mention}!",
        f"⚡ Become the best trainer {message.from_user.first_name}!",
        f"🏆 Catch 'em all {message.from_user.mention}!",
    ]
    return random.choice(responses)
   
    IMAGES = [
    "https://i.ibb.co/BHNStd9P/x.jpg",
    "https://i.ibb.co/S4D4kRg3/x.jpg",
    "https://i.ibb.co/8gfRGhh5/x.jpg"
    ]


# 🔹 BOT ADDED IN GROUP
@app.on_chat_member_updated()
async def on_chat_member_updated(client: Client, message: Message):
    if isinstance(message.new_chat_member, ChatMember) and message.new_chat_member.user.id == client.me.id:
        chat_id = message.chat.id
        await client.send_message(chat_id, "🔥 Thanks for adding me!\n👉 Make me admin to start catching Pokémon.")


# 🔹 START COMMAND
@app.on_message(filters.command("start") & ~filters.bot, group=-4)
async def start(client: Client, message: Message):

    me = await app.get_me()

    # 👉 PRIVATE CHAT
    if message.chat.type == ChatType.PRIVATE:

        text = f"""
╭━━━〔 ⚡ Pokémon World ⚡ 〕━━━╮
┃
┃ 👑 **Powered by ADI**
┃
┃ 🐾 Catch • Trade • Battle
┃ 🎮 Become the Ultimate Trainer
┃ 💎 Build Your Dream Team
┃
┃ ⚡ Start your journey now!
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯
"""

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➕ 𝐏𝐨𝐤𝐞𝐝𝐞𝐱🗯🐛", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
            ],
            [
                InlineKeyboardButton("📢 𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=UPDATE_LINK),
                InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_LINK)
            ],
            [
                InlineKeyboardButton("👑 𝐀𝐝𝐢", url=OWNER_LINK)
            ],
            [
                InlineKeyboardButton("📖 𝐇𝐞𝐥𝐩 & 𝐂𝐦𝐝𝐬", callback_data="help_menu")
            ]
        ])

        await message.reply_photo(
            photo=START_IMG,
            caption=text,
            reply_markup=buttons
        )

    # 👉 GROUP CHAT
    # 👉 GROUP CHAT
else:
    Check = await app.get_chat_member(message.chat.id, me.id)

    if Check.status == ChatMemberStatus.ADMINISTRATOR:

        text = random_text(message)
        image = random.choice(IMAGES)

        await message.reply_photo(
            photo=image,
            caption=text
        )

    else:
        await message.reply_text("❌ Make me admin to play!")

# 🔹 HELP MENU
@app.on_callback_query(filters.regex("help_menu"))
async def help_menu(client, query):

    text = """
📖 **Bot Commands**

🎮 Game:
• /catch <name> — Catch Pokémon  
• /pokedex — Your Pokémon list  
• /trade — Trade Pokémon  

⚙️ Others:
• /cooldown — Spawn status  
• /start — Restart bot  

💡 Tip: Add bot in group to play!
"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
    ])

    await query.message.edit_text(text, reply_markup=buttons)


# 🔹 BACK BUTTON
@app.on_callback_query(filters.regex("back_start"))
async def back_start(client, query):

    text = "✨ Welcome back Trainer!"

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATE_LINK),
            InlineKeyboardButton("💬 Support", url=SUPPORT_LINK)
        ],
        [
            InlineKeyboardButton("👑 ADI", url=OWNER_LINK)
        ],
        [
            InlineKeyboardButton("📖 Help & Commands", callback_data="help_menu")
        ]
    ])

    await query.message.edit_text(text, reply_markup=buttons)
