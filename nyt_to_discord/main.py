import os

import discord

from nyt_to_discord.nyt import Leaderboard

COOKIES = "NYT_COOKIES"
CHANNEL_ID = "DISCORD_DTS_CHANNEL_ID"
# CHANNEL_ID = "DISCORD_BBB_CHANNEL_ID"
BOT_TOKEN = "DISCORD_BOT_TOKEN"

intents = discord.Intents.default()
client = discord.Client(intents=intents)


# weird global data workaround
class MSG:
    msg = "hello"


def main():
    leaderboard = Leaderboard(os.environ[COOKIES])
    print(leaderboard.date)
    MSG.msg = str(leaderboard.scores)
    client.run(token=os.environ[BOT_TOKEN])


@client.event
async def on_ready():
    channel = client.get_channel(int(os.environ[CHANNEL_ID]))
    await channel.send(MSG.msg)
    print("Sent!")
    await client.close()


if __name__ == "__main__":
    main()
