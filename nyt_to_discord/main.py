import os

import discord
from dotenv import load_dotenv

from bot import NytDiscordBot

COOKIES = "NYT_COOKIES"
CHANNEL_ID = "DISCORD_DTS_CHANNEL_ID"
# CHANNEL_ID = "DISCORD_BBB_CHANNEL_ID"
BOT_TOKEN = "DISCORD_BOT_TOKEN"

load_dotenv(os.path.join(os.path.dirname(__file__), "../", ".env"))


def main():
    intents = discord.Intents.default()
    bot = NytDiscordBot(
        nyt_cookies=os.environ[COOKIES],
        channel_id=int(os.environ[CHANNEL_ID]),
        intents=intents,
    )
    bot.run(token=os.environ[BOT_TOKEN])


if __name__ == "__main__":
    main()
