import asyncio
import json
import random
import time

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from pokemonster import app
#from pokemonster.database import Database
from pokemonster.database import add_pokecoin, read_money
from ..config import devs


# ---------------- LOAD QUESTIONS ----------------
with open('trivia.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


# ---------------- MEMORY STORAGE ----------------
active_trivia = {}      # user_id -> session
user_cooldowns = {}     # user_id -> cooldown time

#DB = Database()


# ---------------- TRIVIA COMMAND ----------------
@app.on_message(filters.group & filters.command("trivia"), group=84)
async def trivia(_, message: Message):

    user_id = message.from_user.id   # ✅ FIX (STRING HATA DIYA)

    # ---------- COOLDOWN CHECK ----------
    if user_id in user_cooldowns:
        if time.time() < user_cooldowns[user_id]:
            remaining = int(user_cooldowns[user_id] - time.time())
            minutes = remaining // 60
            seconds = remaining % 60
            return await message.reply_text(
                f"⏳ Please wait {minutes}:{seconds} before using trivia again."
            )
        else:
            user_cooldowns.pop(user_id, None)

    # ---------- ACTIVE SESSION CHECK ----------
    if user_id in active_trivia:
        return await message.reply_text("⚠️ You already have an active trivia session!")

    # ---------- SET COOLDOWN ----------
    user_cooldowns[user_id] = time.time() + 120

    # ---------- PICK QUESTION ----------
    quesdata = random.choice(data["results"])
    question = quesdata["question"]
    correct_answer = quesdata["correct_answer"]
    incorrect_answers = quesdata["incorrect_answers"]

    options = incorrect_answers + [correct_answer]
    random.shuffle(options)

    # ---------- BUTTONS ----------
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"triv:{opt.lower()}:{user_id}")]
        for opt in options
    ]

    msg = await message.reply_text(
        f"❓ {question}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # ---------- SAVE SESSION ----------
    active_trivia[user_id] = {
        "correct_answer": correct_answer.lower(),
        "answered": False,
        "expires": time.time() + 15,
        "message_id": msg.id
    }

    # ---------- AUTO TIMEOUT ----------
    await asyncio.sleep(15)

    session = active_trivia.get(user_id)
    if session and not session["answered"]:
        try:
            await msg.edit_text("⏰ Time Up! No answer selected.")
        except:
            pass
        active_trivia.pop(user_id, None)


# ---------------- CALLBACK HANDLER ----------------
@app.on_callback_query(filters.regex(r"^triv:"))
async def trivia_callback(_, query: CallbackQuery):

    try:
        parts = query.data.split(":")
        selected = parts[1].lower()
        user_id = int(parts[2])   # ✅ FIX (STRING → INT)

        click_user = query.from_user.id   # ✅ FIX

        # ---------- SECURITY CHECK ----------
        if click_user != user_id:
            return await query.answer("Not for you 👻", show_alert=True)

        session = active_trivia.get(user_id)

        if not session:
            return await query.answer("Session expired ⌛", show_alert=True)

        if session["answered"]:
            return await query.answer("Already answered!", show_alert=True)

        session["answered"] = True

        # ✅ FIX (DB hata ke direct function use)
        coins = int(await read_money(user_id))
        correct = session["correct_answer"]

        # ---------- CORRECT ----------
        if selected == correct:

            reward = 10

            if coins >= 10000:
                text = "Correct 🎉\nBut wallet already full 💰"
            else:
                if coins + reward > 10000:
                    reward = 10000 - coins

                await add_pokecoin(user_id, reward, query.from_user.username)  # ✅ FIX
                text = f"Correct 🎉 +{reward} Rubies 💎"

        # ---------- WRONG ----------
        else:
            text = "Wrong Answer 😮‍💨"

        active_trivia.pop(user_id, None)

        await query.message.edit_text(
            f"{query.message.text}\n\n{text}"
        )

    except Exception as e:
        print("Callback Error:", e)


# ---------------- ADMIN COMMAND ----------------
@app.on_message(filters.command("endtriv") & filters.user(devs), group=84)
async def endtriv(_, message: Message):
    active_trivia.clear()
    user_cooldowns.clear()
    await message.reply_text("🛑 All Trivia Sessions Ended Successfully")
