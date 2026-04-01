import json
import random

from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import Message

from pokemonster import app
from pokemonster.database import Database
from pokemonster.db.userdb import USERSINFO

from ..config import users_filt

# Text
run_away_texts = [
    "You Missed the Pokemon!",
    "Oh No! The Pokemon broke free!",
    "Darn! The Pokemon Broke free!",
    "Aww! It appeared to be caught!",
    "Arrgh! Almost had it!",
    "So close!"
]

# Load pokedex
with open('pokedex.json') as f:
    data = json.load(f)

spawned = {}
poke_in = {}

DB = Database()
UI = USERSINFO()


# 🔥 SAFE DEFAULT FUNCTION (IMPORTANT FIX)
async def get_frequency(chatid):
    try:
        return await DB.read_frequency(chatid)
    except:
        return 5  # default spawn after 50 msgs


# 🔹 SPAWN SYSTEM
@app.on_message(filters.group & filters.all, group=0)
async def send_image(c: Client, message: Message):
    chatid = message.chat.id

    # safe dict init
    if str(chatid) not in spawned:
        spawned[str(chatid)] = {"val": False, "msg_count": 0, "appear_msg": 0, "m_id": 0}

    if spawned[str(chatid)]["val"]:
        return

    spawned[str(chatid)]["appear_msg"] += 1

    msg_freq = await get_frequency(chatid)

    if msg_freq <= 0:
        msg_freq = 50

    if spawned[str(chatid)]["appear_msg"] % msg_freq == 0:

        rand_poke = random.choice(data['poke'])
        pokename = rand_poke['name']

        if "." in pokename:
            pokename = " ".join(i.strip() for i in pokename.split("."))
        elif "-" in pokename:
            pokename = " ".join(i.strip() for i in pokename.split("-"))

        poke_in[str(chatid)] = {
            "name": pokename,
            "pokeid": rand_poke["id"],
            "pokelink": rand_poke['link']
        }

        spawned[str(chatid)] = {"appear_msg": 0}

        img = await app.send_photo(
            chat_id=chatid,
            photo=rand_poke['link'],
            caption="✨ A Pokémon appeared!\nUse /catch <name> to catch it!"
        )

        spawned[str(chatid)] = {
            "msg_count": 0,
            "val": True,
            "m_id": img.id,
            "appear_msg": 0
        }

        raise ContinuePropagation


# 🔹 CATCH SYSTEM
@app.on_message(filters.command('catch') & filters.group & ~filters.forwarded, group=1)
async def catch(c: Client, message: Message):
    try:
        if not message.from_user:
            return await message.reply_text("Invalid user")

        chatid = str(message.chat.id)
        userid = message.from_user.id

        if not spawned.get(chatid, {}).get("val"):
            return await message.reply_text("❌ No Pokémon to catch!")

        try:
            guessed = message.text.split(None, 1)[1].lower()
        except:
            return await message.reply_text("Use: /catch <pokemon name>")

        pokename = poke_in[chatid]['name'].lower()

        # smart match
        words = pokename.split()
        short = max(words, key=len)

        if guessed in [pokename, short]:

            pid = poke_in[chatid]["pokeid"]
            UI.save_info(chatid, userid, pid)

            await message.reply_text(
                f"🎉 {message.from_user.mention} caught {pokename.capitalize()}!"
            )

            poke_in[chatid].clear()
            spawned[chatid] = {"val": False, "msg_count": 0, "appear_msg": 0, "m_id": 0}

        else:
            await message.reply_text("❌ Wrong guess!")

    except Exception as e:
        print(e)


# 🔹 RUN SYSTEM
@app.on_message(filters.group, group=2)
async def run(c: Client, message: Message):
    chatid = str(message.chat.id)

    if not spawned.get(chatid, {}).get("val"):
        raise ContinuePropagation

    if spawned[chatid]["msg_count"] >= 30:

        try:
            await app.send_message(
                chatid,
                f"{random.choice(run_away_texts)}\nIt was {poke_in[chatid]['name']}"
            )
        except:
            pass

        try:
            await app.delete_messages(chatid, spawned[chatid]["m_id"])
        except:
            pass

        spawned[chatid] = {"val": False, "msg_count": 0, "appear_msg": 0, "m_id": 0}
        poke_in[chatid].clear()

    else:
        spawned[chatid]["msg_count"] += 1
        raise ContinuePropagation


# 🔹 COOLDOWN CHECK
@app.on_message(filters.command("cooldown") & users_filt, group=8)
async def cooldown_cmd(client: Client, message: Message):
    chatid = str(message.chat.id)

    msg_freq = await get_frequency(chatid)

    appear = spawned.get(chatid, {}).get("appear_msg", 0)
    left = msg_freq - appear

    await message.reply_text(f"⏳ {left} messages left for next spawn")
