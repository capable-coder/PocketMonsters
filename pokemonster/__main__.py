import logging
import random
import os

from pyrogram import idle
from pyrogram.types import BotCommand

from pokemonster import app
from pokemonster.database import Database

# ---------------- SAFE DB INIT ----------------
DB = Database()

# ---------------- LOGGING SAFE PATH ----------------
LOG_PATH = os.path.join("pokemonster", "logs", "logs.txt")

logging.basicConfig(
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format="[KRRISH] %(message)s",
    datefmt="[%X]",
)

LOGGER = logging.getLogger("[KRRISH]")


# ---------------- STARTUP ----------------
async def load_start():
    LOGGER.info("Booting bot...")

    try:
        LOGGER.info("Pyrogram bot started successfully")
    except Exception as e:
        LOGGER.error(f"Startup error: {e}")


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

        # safe random log message (NO CRASH IF CHAT NOT EXISTS)
        try:
            a1 = random.randint(1, 9)
            await app.send_message(
                chat_id=-1003801101735,
                text=f"Bot Started!\nTime: 0.{a1}"
            )
        except Exception as e:
            LOGGER.warning(f"Log channel message failed: {e}")

        await cmds(app)
        await DB.setup()

        LOGGER.info("Bot is running...")
        await idle()

    except Exception as e:
        LOGGER.error(f"Fatal error in main: {e}")

    finally:
        try:
            await app.stop()
        except:
            pass


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(main())
