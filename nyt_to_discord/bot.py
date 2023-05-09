import discord

from nyt import Leaderboard


class NytDiscordBot(discord.Client):
    def __init__(self, nyt_cookies: str, channel_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._channel_id = channel_id
        self._leaderboard = Leaderboard(nyt_cookies)

    async def on_ready(self):
        channel = self.get_channel(self._channel_id)
        await channel.send(self._build_leaderboard_msg())
        await self.close()

    def _build_leaderboard_msg(self) -> str:
        return str(self._leaderboard.scores)
