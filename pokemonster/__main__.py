import logging
import random
import os
import asyncio

from pyrogram import idle
from pyrogram.types import BotCommand
# 🔥 LOAD ALL MODULES (IMPORTANT)
import pokemonster.modules.claim
import pokemonster.modules.dev
import pokemonster.modules.frequency
import pokemonster.modules.guess
import pokemonster.modules.help
import pokemonster.modules.host
import pokemonster.modules.leader
import pokemonster.modules.pokecoin
import pokemonster.modules.pokedex
import pokemonster.modules.pokegift
import pokemonster.modules.pokestore
import pokemonster.modules.release
import pokemonster.modules.spawner
import pokemonster.modules.start
import pokemonster.modules.trivia
import pokemonster.modules.watcher

from pokemonster import app

# ---------------- DATABASE IMPORT ----------------
from pokemonster.database import (
    update_user,
    get_user,
    add_frequency,
    read_frequency,
    add_pokecoin,
    subtract_pokecoin,
    make_coins_0,
    read_money,
    sorted_money_database
)

# ---------------- LOGGING SAFE PATH ----------------
LOG_PATH = os.path.join("pokemonster", "logs", "logs.txt")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format="[KRRISH] %(message)s",
)

LOGGER = logging.getLogger("[KRRISH]")


# ---------------- STARTUP ----------------
async def load_start():
    LOGGER.info("Booting bot...")
    LOGGER.info("Pyrogram bot started successfully")


# ---------------- COMMANDS ----------------
async def cmds(app):
    await app.set_bot_commands(
        [
            BotCommand("start", "Check bot status"),
            BotCommand("catch", "Catch Pokemon"),
            BotCommand("pokedex", "View collection"),
            BotCommand("ptrade", "Trade Pokemon"),
            BotCommand("pfav", "Set favourite"),
            BotCommand("pgift", "Gift Pokemon"),
            BotCommand("winner", "Top player"),
            BotCommand("leader", "Leaderboard"),
            BotCommand("release", "Release Pokemon"),
            BotCommand("pinfo", "Pokemon info"),
            BotCommand("devcmds", "Developer commands"),
            BotCommand("updatepower", "Update power"),
            BotCommand("spawn", "Spawn test"),
            BotCommand("guess", "Guess Pokemon"),
            BotCommand("poketrivia", "Trivia game"),
            BotCommand("freqchange", "Change spawn frequency"),
            BotCommand("pokestore", "Buy Pokemon"),
            BotCommand("wallet", "Check coins"),
            BotCommand("pay", "Send money"),
        ]
    )


# ---------------- MAIN ----------------
async def main():
    try:
        await app.start()
        await load_start()

        # safe startup message
        try:
            a1 = random.randint(1, 9)
            await app.send_message(
                chat_id=-1003801101735,
                text=f"Bot Started!\nTime: 0.{a1}"
            )
        except Exception as e:
            LOGGER.warning(f"Log channel message failed: {e}")

        await cmds(app)

        LOGGER.info("Bot is running...")
        await idle()

    except Exception as e:
        LOGGER.error(f"Fatal error in main: {e}")

    finally:
        try:
            await app.stop()
        except Exception as e:
            LOGGER.error(f"Stop error: {e}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    asyncio.run(main())
