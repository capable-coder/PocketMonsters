import asyncio
import json
import random
import time
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from pokemonster import app
from pokemonster.database import Database

from ..config import users_filt

# Load pokedex
with open('pokedex.json') as f:
    data = json.load(f)

unique_event = {}
cooldown = {}
msg_dict = {}
uuid_for_this_event = None

DB = Database()


def uuid_generator():
    return str(datetime.now()).replace("-", "").replace(":", "").replace(".", "").replace(" ", "")


@app.on_message(filters.command('spawn'), group=0)
async def hunt(c: Client, message: Message):
    global uuid_for_this_event

    unique_event.clear()
    chat_id = message.chat.id

    # ⛔ Cooldown check
    if chat_id in cooldown:
        time_left = int(cooldown[chat_id] - time.time())
        if time_left > 0:
            minutes = time_left // 60
            seconds = time_left % 60
            return await message.reply_text(
                f"⏳ Already spawned!\nWait {minutes}:{seconds} sec"
            )

    uuid_for_this_event = uuid_generator()

    # ✅ FIX: pehle pokemon select karo
    rand_poke = random.choice(data['poke'])

    # ✅ name clean karo
    pokename = rand_poke['name']

    if "." in pokename:
        pokename = " ".join(i.strip() for i in pokename.split("."))
    elif "-" in pokename:
        pokename = " ".join(i.strip() for i in pokename.split("-"))

    unique_event[uuid_for_this_event] = {
        "pid": rand_poke['id'],
        "pname": pokename.lower(),  # lowercase safe compare
        "plink": rand_poke['link'],
        "sent": True,
        "msg_count": 0,
    }

    msg = await c.send_photo(
        chat_id=chat_id,
        photo=rand_poke['link'],
        caption="🧩 Guess the Pokémon!\nUse: /guess <name>"
    )

    msg_dict[chat_id] = msg
    cooldown[chat_id] = time.time() + 300  # 5 min cooldown

    # ⏳ 60 sec baad delete
    await asyncio.sleep(60)

    if chat_id in msg_dict:
        try:
            await msg_dict[chat_id].delete()
        except:
            pass

    unique_event.clear()


@app.on_message(filters.command("guess") & ~filters.forwarded)
async def guessed_name(c: Client, message: Message):
    global uuid_for_this_event

    try:
        text = message.text.split(None, 1)[1].strip().lower()

        if uuid_for_this_event and unique_event.get(uuid_for_this_event, {}).get('sent'):
            unique_event[uuid_for_this_event]['msg_count'] += 1

            if text == unique_event[uuid_for_this_event]['pname']:

                username = message.from_user.username or message.from_user.first_name

                coins = await DB.read_money(message.from_user.id)

                if int(coins) >= 10000:
                    response = "✅ Correct!\nWallet full 💰"
                else:
                    add = 5
                    if int(coins) + add > 10000:
                        add = 10000 - int(coins)

                    await DB.add_pokecoin(message.from_user.id, add, username)
                    response = f"🎉 Correct!\n+{add} coins added"

                await message.reply_text(response)

                try:
                    await msg_dict[message.chat.id].delete()
                except:
                    pass

                unique_event.clear()
                cooldown.clear()
                msg_dict.clear()

            else:
                await message.reply_text("❌ Wrong! Try again")

    except IndexError:
        await message.reply_text("❗ Use: /guess <pokemon name>")
    except Exception as e:
        print(e)


@app.on_message(filters.command("endguess") & users_filt)
async def end(client, message: Message):
    unique_event.clear()
    cooldown.clear()
    msg_dict.clear()
    await message.reply_text("🛑 Guess ended!")
