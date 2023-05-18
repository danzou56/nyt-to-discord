import os

import discord
from dotenv import load_dotenv

from nyt_to_discord.bot import NytDiscordBot
from nyt_to_discord import ROOT_DIR

COOKIES = "NYT_COOKIES"
CHANNEL_ID = "DISCORD_ERR_CHANNEL_ID"
ERR_CHANNEL_ID = "DISCORD_ERR_CHANNEL_ID"
BOT_TOKEN = "DISCORD_BOT_TOKEN"

load_dotenv(os.path.join(ROOT_DIR, "../", ".env"))


def main():
    intents = discord.Intents.default()
    bot = NytDiscordBot(
        nyt_cookies=os.environ[COOKIES],
        channel_id=int(os.environ[CHANNEL_ID]),
        err_channel_id=int(os.environ[ERR_CHANNEL_ID]),
        intents=intents,
    )
    bot.run(token=os.environ[BOT_TOKEN])


if __name__ == "__main__":
    main()
