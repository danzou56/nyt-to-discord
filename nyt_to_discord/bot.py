import datetime

import discord
from tabulate import tabulate

from nyt import Leaderboard


class NytDiscordBot(discord.Client):
    def __init__(
        self, nyt_cookies: str, channel_id: int, err_channel_id: int, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._channel_id = channel_id
        self._err_channel_id = err_channel_id
        self._nyt_cookies = nyt_cookies
        self._leaderboard = None

    @property
    def leaderboard(self) -> Leaderboard:
        if self._leaderboard is not None:
            return self._leaderboard

        self._leaderboard = Leaderboard(self._nyt_cookies)
        return self._leaderboard

    async def on_ready(self):
        channel = self.get_channel(self._channel_id)
        try:
            await channel.send(self._build_leaderboard_msg())
        except Exception as e:
            await self.get_channel(self._err_channel_id).send(e.__str__())
            raise e
        finally:
            await self.close()

    def _build_leaderboard_msg(self) -> str:
        scores = self.leaderboard.scores
        date = datetime.datetime.strftime(self.leaderboard.date, "%A, %B %-d, %Y")
        formatted_table = tabulate(
            [
                [
                    rank + 1,
                    score.name,
                    ":".join(str(score.time).split(":")[1:]) if score.time else "N/A",
                ]
                for (rank, score) in enumerate(scores)
            ],
            headers=["Rank", "Name", "Time"],
            tablefmt="simple_grid",
        )
        return f"Mini results for {date} 👀\n```{formatted_table}```"
